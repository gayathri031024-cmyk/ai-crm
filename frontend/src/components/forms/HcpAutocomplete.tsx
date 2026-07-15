import { useEffect, useState } from "react";
import { Autocomplete, TextField, CircularProgress } from "@mui/material";
import { hcpApi } from "@/api/hcpApi";
import type { HCP } from "@/types";

interface HcpAutocompleteProps {
  value: string;
  onChange: (hcpId: string) => void;
  error?: boolean;
  helperText?: string;
}

export default function HcpAutocomplete({ value, onChange, error, helperText }: HcpAutocompleteProps) {
  const [options, setOptions] = useState<HCP[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    const timer = setTimeout(() => {
      hcpApi
        .list({ search: inputValue || undefined, page_size: 20 })
        .then((res) => {
          if (active) setOptions(res.items);
        })
        .finally(() => active && setLoading(false));
    }, 250);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [inputValue]);

  const selected = options.find((o) => o.id === value) ?? null;

  return (
    <Autocomplete
      options={options}
      value={selected}
      getOptionLabel={(o) => `${o.full_name}${o.hospital_name ? " · " + o.hospital_name : ""}`}
      isOptionEqualToValue={(o, v) => o.id === v.id}
      loading={loading}
      onInputChange={(_, val) => setInputValue(val)}
      onChange={(_, newValue) => onChange(newValue?.id ?? "")}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Healthcare Professional"
          error={error}
          helperText={helperText}
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <>
                {loading ? <CircularProgress color="inherit" size={16} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
    />
  );
}
