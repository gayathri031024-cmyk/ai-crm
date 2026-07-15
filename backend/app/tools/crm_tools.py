"""
The 5 tools required by the assignment:
  1. log_interaction   — create a structured Interaction from natural language
  2. edit_interaction  — patch an existing Interaction ("actually it was 10 samples")
  3. search_hcp        — find HCPs by name/hospital/city/specialization
  4. schedule_follow_up — set/move a follow-up date
  5. generate_visit_summary — produce a readable recap of recent interactions

Each function returns a plain dict: {"status": "ok" | "needs_clarification" | "error",
"message": <str for the LLM to relay/react to>, "data": <structured payload or None>}
so the agent graph can feed the result straight back to the model as a tool message.
"""
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.interaction import CreatedVia, Interaction, InteractionType, Sentiment
from app.models.interaction_history import ChangeSource
from app.repositories.hcp_repository import HCPRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction import InteractionCreate, InteractionUpdate
from app.services.interaction_service import InteractionService
from app.tools.hcp_resolver import resolve_hcp_by_name
from app.tools.schemas import (
    EditInteractionArgs,
    GenerateVisitSummaryArgs,
    LogInteractionArgs,
    ScheduleFollowUpArgs,
    SearchHCPArgs,
)
from app.utils.date_parser import resolve_date_phrase


def _clarification_response(candidates) -> dict:
    names = ", ".join(f"{c.full_name} ({c.hospital_name or 'no hospital listed'})" for c in candidates)
    return {
        "status": "needs_clarification",
        "message": f"I found multiple matching HCPs: {names}. Which one did you mean?",
        "data": {"candidates": [{"id": c.id, "full_name": c.full_name} for c in candidates]},
    }


def _not_found_response(name: str) -> dict:
    return {
        "status": "needs_clarification",
        "message": f"I couldn't find an HCP named '{name}' in the system. "
        f"Could you confirm the spelling, or should I create a new HCP record?",
        "data": None,
    }


# ---------------------------------------------------------------------------
# 1. Log Interaction
# ---------------------------------------------------------------------------
def log_interaction(db: Session, user_id: str, args: LogInteractionArgs) -> dict:
    resolution = resolve_hcp_by_name(db, args.hcp_name)
    if resolution.needs_clarification:
        return _clarification_response(resolution.candidates)
    if resolution.not_found:
        return _not_found_response(args.hcp_name)

    visit_date_str = resolve_date_phrase(args.visit_date) or args.visit_date
    try:
        visit_dt = datetime.fromisoformat(visit_date_str)
    except ValueError:
        return {
            "status": "error",
            "message": f"I couldn't understand the visit date '{args.visit_date}'. "
            f"Could you give it as e.g. '2026-07-13'?",
            "data": None,
        }

    follow_up_str = resolve_date_phrase(args.follow_up_date)
    follow_up: date | None = None
    if follow_up_str:
        try:
            follow_up = date.fromisoformat(follow_up_str)
        except ValueError:
            follow_up = None

    try:
        interaction_type = InteractionType(args.interaction_type)
    except ValueError:
        interaction_type = InteractionType.visit

    sentiment = None
    if args.sentiment:
        try:
            sentiment = Sentiment(args.sentiment.lower())
        except ValueError:
            sentiment = None

    service = InteractionService(db)
    create_data = InteractionCreate(
        hcp_id=resolution.hcp.id,
        interaction_type=interaction_type,
        visit_date=visit_dt,
        follow_up_date=follow_up,
        discussion_summary=args.discussion_summary,
        products_discussed=args.products_discussed,
        samples_given=args.samples_given,
        sentiment=sentiment,
        next_action=args.next_action,
        notes=args.notes,
        created_via=CreatedVia.ai_chat,
    )
    interaction = service.create_interaction(create_data, user_id=user_id)

    summary_bits = [f"Logged a {interaction_type.value} with {resolution.hcp.full_name}"]
    if args.products_discussed:
        summary_bits.append(f"discussing {', '.join(args.products_discussed)}")
    if args.samples_given:
        summary_bits.append(f"with {args.samples_given} samples given")
    if follow_up:
        summary_bits.append(f"and a follow-up set for {follow_up.isoformat()}")

    return {
        "status": "ok",
        "message": " ".join(summary_bits) + ".",
        "data": {
            "interaction_id": interaction.id,
            "hcp_id": resolution.hcp.id,
            "hcp_name": resolution.hcp.full_name,
            "interaction_type": interaction_type.value,
            "visit_date": visit_dt.isoformat(),
            "follow_up_date": follow_up.isoformat() if follow_up else None,
            "discussion_summary": args.discussion_summary,
            "products_discussed": args.products_discussed,
            "samples_given": args.samples_given,
            "sentiment": sentiment.value if sentiment else None,
            "next_action": args.next_action,
        },
    }

# ---------------------------------------------------------------------------
# 2. Edit Interaction
# ---------------------------------------------------------------------------
def edit_interaction(db: Session, user_id: str, args: EditInteractionArgs) -> dict:
    repo = InteractionRepository(db)

    interaction: Interaction | None = None
    if args.interaction_id:
        interaction = repo.get(args.interaction_id)
    elif args.hcp_name:
        resolution = resolve_hcp_by_name(db, args.hcp_name)
        if resolution.needs_clarification:
            return _clarification_response(resolution.candidates)
        if resolution.not_found:
            return _not_found_response(args.hcp_name)
        interaction = repo.get_latest_for_user(user_id, hcp_id=resolution.hcp.id)
    else:
        interaction = repo.get_latest_for_user(user_id)

    if interaction is None:
        return {
            "status": "error",
            "message": "I couldn't find an existing interaction to edit. "
            "Could you tell me which HCP or give me the interaction details again?",
            "data": None,
        }

    update_fields = args.model_dump(exclude={"hcp_name", "interaction_id"}, exclude_unset=True)
    if "follow_up_date" in update_fields and update_fields["follow_up_date"]:
        resolved = resolve_date_phrase(update_fields["follow_up_date"])
        update_fields["follow_up_date"] = date.fromisoformat(resolved) if resolved else None
    if "sentiment" in update_fields and update_fields["sentiment"]:
        try:
            update_fields["sentiment"] = Sentiment(update_fields["sentiment"].lower()).value
        except ValueError:
            update_fields.pop("sentiment")

    if not update_fields:
        return {
            "status": "error",
            "message": "You didn't mention anything to change — what would you like me to update?",
            "data": None,
        }

    service = InteractionService(db)
    updated = service.update_interaction(
        interaction.id,
        InteractionUpdate(**update_fields),
        changed_by=user_id,
        source=ChangeSource.ai_chat,
    )

    changes = ", ".join(f"{k} → {v}" for k, v in update_fields.items())
    return {
        "status": "ok",
        "message": f"Updated the interaction: {changes}.",
        "data": {"interaction_id": updated.id},
    }


# ---------------------------------------------------------------------------
# 3. Search HCP
# ---------------------------------------------------------------------------
def search_hcp(db: Session, args: SearchHCPArgs) -> dict:
    repo = HCPRepository(db)
    matches, total = repo.list(page=1, page_size=10, search=args.query)

    if not matches:
        return {
            "status": "ok",
            "message": f"No HCPs found matching '{args.query}'.",
            "data": {"results": []},
        }

    results = [
        {
            "id": m.id,
            "full_name": m.full_name,
            "specialization": m.specialization,
            "hospital_name": m.hospital_name,
            "city": m.city,
            "tier": m.tier.value if hasattr(m.tier, "value") else m.tier,
        }
        for m in matches
    ]
    names = ", ".join(m.full_name for m in matches)
    return {
        "status": "ok",
        "message": f"Found {total} HCP(s) matching '{args.query}': {names}.",
        "data": {"results": results},
    }


# ---------------------------------------------------------------------------
# 4. Schedule Follow-up
# ---------------------------------------------------------------------------
def schedule_follow_up(db: Session, user_id: str, args: ScheduleFollowUpArgs) -> dict:
    repo = InteractionRepository(db)

    interaction: Interaction | None = None
    if args.interaction_id:
        interaction = repo.get(args.interaction_id)
    elif args.hcp_name:
        resolution = resolve_hcp_by_name(db, args.hcp_name)
        if resolution.needs_clarification:
            return _clarification_response(resolution.candidates)
        if resolution.not_found:
            return _not_found_response(args.hcp_name)
        interaction = repo.get_latest_for_user(user_id, hcp_id=resolution.hcp.id)
    else:
        interaction = repo.get_latest_for_user(user_id)

    if interaction is None:
        return {
            "status": "error",
            "message": "I couldn't find an interaction to attach that follow-up to.",
            "data": None,
        }

    resolved_date = resolve_date_phrase(args.follow_up_date)
    try:
        follow_up_date = date.fromisoformat(resolved_date)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": f"I couldn't understand the follow-up date '{args.follow_up_date}'.",
            "data": None,
        }

    service = InteractionService(db)
    updated = service.update_interaction(
        interaction.id,
        InteractionUpdate(follow_up_date=follow_up_date),
        changed_by=user_id,
        source=ChangeSource.ai_chat,
    )

    return {
        "status": "ok",
        "message": f"Follow-up scheduled for {follow_up_date.isoformat()}.",
        "data": {"interaction_id": updated.id, "follow_up_date": follow_up_date.isoformat()},
    }


# ---------------------------------------------------------------------------
# 5. Generate Visit Summary
# ---------------------------------------------------------------------------
def generate_visit_summary(db: Session, args: GenerateVisitSummaryArgs) -> dict:
    repo = InteractionRepository(db)

    if args.interaction_id:
        interaction = repo.get(args.interaction_id)
        interactions = [interaction] if interaction else []
    elif args.hcp_name:
        resolution = resolve_hcp_by_name(db, args.hcp_name)
        if resolution.needs_clarification:
            return _clarification_response(resolution.candidates)
        if resolution.not_found:
            return _not_found_response(args.hcp_name)
        interactions, _total = repo.list(
            page=1, page_size=args.limit, hcp_id=resolution.hcp.id, sort_by="visit_date", sort_dir="desc"
        )
    else:
        return {
            "status": "error",
            "message": "Which HCP or interaction would you like a summary for?",
            "data": None,
        }

    if not interactions:
        return {"status": "ok", "message": "No interactions found to summarize.", "data": {"summary": ""}}

    lines = []
    for i in interactions:
        products = ", ".join(i.products_discussed) if i.products_discussed else "no specific products noted"
        line = (
            f"- {i.visit_date.strftime('%b %d, %Y')} ({i.interaction_type.value}): "
            f"{i.discussion_summary or 'no summary recorded'}. Products: {products}. "
            f"Samples given: {i.samples_given}. Sentiment: {i.sentiment.value if i.sentiment else 'not recorded'}."
        )
        if i.follow_up_date:
            line += f" Follow-up: {i.follow_up_date.isoformat()}."
        lines.append(line)

    summary_text = "\n".join(lines)
    return {
        "status": "ok",
        "message": f"Here is the visit summary:\n{summary_text}",
        "data": {"summary": summary_text, "count": len(interactions)},
    }
