-- ============================================================
-- AI-First CRM — Database Schema (MySQL 8.x)
-- Module: HCP (Healthcare Professional) — Log Interaction
-- ============================================================
-- Charset/collation chosen for full unicode + emoji support in
-- free-text fields (chat messages, notes, summaries).

CREATE DATABASE IF NOT EXISTS ai_crm
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_crm;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- users — sales reps / medical reps who log interactions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              CHAR(36)     NOT NULL PRIMARY KEY,      -- UUID
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL,
    role            ENUM('rep', 'manager', 'admin') NOT NULL DEFAULT 'rep',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    territory       VARCHAR(150) NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- hcps — Healthcare Professionals (doctors, pharmacists, etc.)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hcps (
    id              CHAR(36)     NOT NULL PRIMARY KEY,      -- UUID
    full_name       VARCHAR(150) NOT NULL,
    specialization  VARCHAR(150) NULL,
    hospital_name   VARCHAR(200) NULL,
    phone           VARCHAR(30)  NULL,
    email           VARCHAR(255) NULL,
    city            VARCHAR(120) NULL,
    tier            ENUM('A', 'B', 'C') NOT NULL DEFAULT 'B',
    notes           TEXT         NULL,
    created_by      CHAR(36)     NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_hcps_created_by FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE SET NULL,
    FULLTEXT INDEX ftx_hcps_search (full_name, hospital_name, city),
    INDEX idx_hcps_name (full_name)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- interactions — the core "Log Interaction" record
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interactions (
    id                  CHAR(36)     NOT NULL PRIMARY KEY,  -- UUID
    hcp_id              CHAR(36)     NOT NULL,
    user_id             CHAR(36)     NOT NULL,
    interaction_type    ENUM('visit', 'call', 'email', 'virtual_meeting', 'event')
                                     NOT NULL DEFAULT 'visit',
    visit_date          DATETIME     NOT NULL,
    follow_up_date      DATE         NULL,
    discussion_summary  TEXT         NULL,
    products_discussed  JSON         NULL,                  -- array of product names
    samples_given       INT          NOT NULL DEFAULT 0,
    sentiment           ENUM('positive', 'neutral', 'negative') NULL,
    next_action         VARCHAR(255) NULL,
    notes               TEXT         NULL,
    created_via         ENUM('form', 'ai_chat') NOT NULL DEFAULT 'form',
    created_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_interactions_hcp  FOREIGN KEY (hcp_id)
        REFERENCES hcps(id)  ON DELETE CASCADE,
    CONSTRAINT fk_interactions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_interactions_hcp (hcp_id),
    INDEX idx_interactions_user (user_id),
    INDEX idx_interactions_visit_date (visit_date),
    INDEX idx_interactions_follow_up (follow_up_date),
    INDEX idx_interactions_sentiment (sentiment),
    FULLTEXT INDEX ftx_interactions_summary (discussion_summary, notes)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- interaction_history — full audit trail of edits to an
-- interaction (e.g. "Actually it was 10 samples.")
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interaction_history (
    id              CHAR(36)  NOT NULL PRIMARY KEY,         -- UUID
    interaction_id  CHAR(36)  NOT NULL,
    changed_by      CHAR(36)  NOT NULL,
    change_source   ENUM('form', 'ai_chat') NOT NULL DEFAULT 'form',
    field_name      VARCHAR(100) NOT NULL,
    old_value       TEXT      NULL,
    new_value       TEXT      NULL,
    changed_at      DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_interaction FOREIGN KEY (interaction_id)
        REFERENCES interactions(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_user FOREIGN KEY (changed_by)
        REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_history_interaction (interaction_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- conversation_logs — one row per chat "session" with the
-- LangGraph CRM assistant
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_logs (
    id          CHAR(36)  NOT NULL PRIMARY KEY,             -- UUID
    user_id     CHAR(36)  NOT NULL,
    title       VARCHAR(255) NULL,
    started_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at    DATETIME  NULL,
    CONSTRAINT fk_conv_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conv_user (user_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- ai_messages — individual messages within a conversation,
-- including tool calls made by the agent
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_messages (
    id              CHAR(36)  NOT NULL PRIMARY KEY,          -- UUID
    conversation_id CHAR(36)  NOT NULL,
    role            ENUM('user', 'assistant', 'tool', 'system') NOT NULL,
    content         TEXT      NOT NULL,
    tool_name       VARCHAR(100) NULL,
    tool_input      JSON      NULL,
    tool_output     JSON      NULL,
    model_used      VARCHAR(100) NULL,                       -- primary/fallback model
    created_at      DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_msg_conversation FOREIGN KEY (conversation_id)
        REFERENCES conversation_logs(id) ON DELETE CASCADE,
    INDEX idx_msg_conversation (conversation_id),
    INDEX idx_msg_created_at (created_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- audit_logs — system-wide audit trail (auth events, CRUD on
-- any entity, permission checks)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id          CHAR(36)  NOT NULL PRIMARY KEY,              -- UUID
    user_id     CHAR(36)  NULL,
    action      VARCHAR(100) NOT NULL,                       -- e.g. 'LOGIN', 'CREATE_INTERACTION'
    entity_type VARCHAR(100) NULL,                           -- e.g. 'interaction'
    entity_id   CHAR(36)  NULL,
    ip_address  VARCHAR(64)  NULL,
    metadata    JSON      NULL,
    created_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created_at (created_at)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
