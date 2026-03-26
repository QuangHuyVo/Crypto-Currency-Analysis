import { useEffect, useMemo, useRef, useState } from "react";

const shell = {
  bg: "#141414",
  border: "#333",
  text: "#e5e5e5",
  muted: "#8c8c8c",
  accent: "#e50914",
};

type Props = {
  symbols: string[];
  /** When set, empty search shows these first (e.g. top by 24h volume). */
  topSymbols?: string[];
  value: string;
  onChange: (symbol: string) => void;
};

export function SymbolSearch({ symbols, topSymbols = [], value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toUpperCase();
    if (!q) {
      if (topSymbols.length > 0) return topSymbols.slice(0, 100);
      return symbols.slice(0, 50);
    }
    return symbols.filter((s) => s.toUpperCase().includes(q)).slice(0, 50);
  }, [symbols, query, topSymbols]);

  return (
    <div ref={rootRef} style={{ position: "relative", minWidth: 200, width: "100%", maxWidth: 520 }}>
      <input
        aria-label="Search symbol"
        aria-expanded={open}
        aria-controls="symbol-search-list"
        value={open ? query : value}
        placeholder="Search USDT pair…"
        onChange={(e) => {
          setQuery(e.target.value);
          if (!open) setOpen(true);
        }}
        onFocus={() => {
          setQuery("");
          setOpen(true);
        }}
        style={{
          width: "100%",
          padding: "0.45rem 0.6rem",
          borderRadius: 4,
          border: `1px solid ${shell.border}`,
          background: shell.bg,
          color: shell.text,
          outline: "none",
        }}
      />
      {open && (
        <ul
          id="symbol-search-list"
          role="listbox"
          style={{
            position: "absolute",
            zIndex: 20,
            top: "100%",
            left: 0,
            right: 0,
            margin: "4px 0 0",
            padding: 0,
            listStyle: "none",
            maxHeight: 240,
            overflowY: "auto",
            background: shell.bg,
            border: `1px solid ${shell.border}`,
            borderRadius: 4,
            boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
          }}
        >
          {filtered.length === 0 && (
            <li style={{ padding: "0.5rem 0.75rem", color: shell.muted }}>No matches</li>
          )}
          {filtered.map((s) => (
            <li key={s}>
              <button
                type="button"
                role="option"
                aria-selected={s === value}
                onClick={() => {
                  onChange(s);
                  setOpen(false);
                  setQuery("");
                }}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "0.45rem 0.75rem",
                  border: "none",
                  background: s === value ? "rgba(229, 9, 20, 0.15)" : "transparent",
                  color: shell.text,
                  cursor: "pointer",
                  fontSize: "0.9rem",
                }}
              >
                {s}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
