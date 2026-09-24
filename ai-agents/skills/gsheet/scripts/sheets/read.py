"""Read operations: ranges, records, batch reads, tab assertions."""

from __future__ import annotations

import re
from typing import Any

from .client import SheetError, a1, range_width, resolve_tab, tab_map

_TRAILING_DIGITS = re.compile(r"(\d+)\s*$")


def pad(rows: list[list], width: int | None = None) -> list[list]:
    """Square off ragged rows.

    Sheets omits trailing empty cells, so rows come back at different lengths and
    a fully-empty trailing column disappears entirely - shifting every downstream
    index left. `width` (from the requested range) wins when it is wider than any
    row, which is what stops that shift.
    """
    if not rows:
        return rows
    w = max(width or 0, max(len(r) for r in rows))
    return [list(r) + [""] * (w - len(r)) for r in rows]


def read_range(svc, spreadsheet_id: str, rng: str = "A1:Z5000", *,
               gid: int | None = None, tab: str | None = None,
               squared: bool = True, unformatted: bool = False) -> list[list]:
    """Read one range. `squared=True` pads to the requested column span.

    `unformatted=True` returns underlying values (int/float) instead of display
    strings - use it whenever you intend to do arithmetic.
    """
    title = resolve_tab(svc, spreadsheet_id, gid, tab)
    params: dict[str, Any] = {"spreadsheetId": spreadsheet_id, "range": a1(title, rng)}
    if unformatted:
        params["valueRenderOption"] = "UNFORMATTED_VALUE"
    vals = svc.spreadsheets().values().get(**params).execute().get("values", [])
    return pad(vals, range_width(rng)) if squared else vals


def read_batch(svc, spreadsheet_id: str, ranges: list[str]) -> dict[str, list[list]]:
    """Several fully-qualified ranges ("'Tab'!A1:C9") in ONE round trip."""
    res = svc.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id, ranges=ranges).execute()
    return {vr.get("range", ranges[i]): vr.get("values", [])
            for i, vr in enumerate(res.get("valueRanges", []))}


def read_records(svc, spreadsheet_id: str, rng: str = "A1:Z5000", *,
                 gid: int | None = None, tab: str | None = None,
                 header_row: int = 0) -> list[dict]:
    """Read a tab as dicts keyed by its header row.

    Short rows are filled with "" rather than raising, so a ragged tail cannot
    turn into an IndexError halfway through a run.
    """
    rows = read_range(svc, spreadsheet_id, rng, gid=gid, tab=tab, squared=False)
    if len(rows) <= header_row:
        return []
    header = [str(h).strip() for h in rows[header_row]]
    out = []
    for r in rows[header_row + 1:]:
        if not any(str(c).strip() for c in r):
            continue
        out.append({h: (r[i] if i < len(r) else "") for i, h in enumerate(header)})
    return out


def require_tabs(svc, spreadsheet_id: str, required: list[str]) -> dict[int, str]:
    """Assert every named tab exists before doing any work.

    Failing here is much cheaper than discovering a renamed tab after a long
    query run, and the error names what is actually present.
    """
    tabs = tab_map(svc, spreadsheet_id)
    titles = set(tabs.values())
    missing = [t for t in required if t not in titles]
    if missing:
        raise SheetError(f"missing required tabs: {missing}; found: {sorted(titles)}")
    return tabs


def account_urn(value: str, prefix: str = "account:") -> str:
    """Normalize '123456789' / 'Example (123456789)' / a full key -> a full key."""
    v = str(value).strip()
    if v.startswith("urn:"):
        return v
    m = _TRAILING_DIGITS.search(v)
    return f"{prefix}{m.group(1)}" if m else v


def to_number(value: Any) -> float | None:
    """Parse a display string ('-22.9%', '2,074', '$1,234.00') into a number.

    Returns None when the cell is empty or non-numeric, so callers can filter
    rather than crash on a footnote row.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
    if not s or s in {"-", "-", "n/a", "N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None
