"""Write operations: range writes, append, clear, tab and column structure.

Every mutating helper here is written so that the *safe* thing is the default
and the dangerous thing has to be asked for explicitly.
"""

from __future__ import annotations

import re

from .client import (A1_CELL, SheetError, a1, col_index, col_letter, gid_for,
                     has_row_bounds, range_width, resolve_tab, tab_map)
from .read import pad


def write_range(svc, spreadsheet_id: str, rng: str, values: list[list], *,
                gid: int | None = None, tab: str | None = None,
                value_input_option: str = "USER_ENTERED",
                allow_open_range: bool = False) -> dict:
    """Overwrite a range and read it back.

    Refuses a range without row bounds ("A:L") unless `allow_open_range=True`:
    `values().update` only touches the cells you send, so a short payload over a
    long range leaves the rows below it intact and now stale. Write the full
    rectangle, or `clear_range()` first.
    """
    if not has_row_bounds(rng) and not allow_open_range:
        raise SheetError(
            f"range {rng!r} has no row bounds. Write an explicit full range "
            f"(e.g. A1:{col_letter(max(len(r) for r in values) - 1) if values else 'L'}"
            f"{len(values)}) so a short payload cannot leave stale rows behind, "
            "or pass allow_open_range=True.")
    if not all(isinstance(r, list) for r in values):
        raise SheetError("values must be a list of lists")

    # `values().update` only touches the cells actually sent, so a ragged payload
    # leaves the tail columns of its short rows holding whatever was there
    # before. Square the block to the full rectangle so every cell is written.
    width = range_width(rng) or (max((len(r) for r in values), default=0))
    values = pad(values, width)

    title = resolve_tab(svc, spreadsheet_id, gid, tab)
    res = svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=a1(title, rng),
        valueInputOption=value_input_option, body={"values": values},
    ).execute()

    # An update that reports success can still land somewhere unexpected.
    after = pad(svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=a1(title, rng)
    ).execute().get("values", []), range_width(rng))
    return {"tab": title, "updatedRange": res.get("updatedRange"),
            "updatedRows": res.get("updatedRows"),
            "updatedColumns": res.get("updatedColumns"),
            "rows_after_readback": len(after), "readback": after}


def write_table(svc, spreadsheet_id: str, values: list[list], *,
                gid: int | None = None, tab: str | None = None,
                start: str = "A1", clear_first: bool = True,
                value_input_option: str = "USER_ENTERED") -> dict:
    """Write a whole table, sizing the range from the data.

    This is the shape you almost always want: it computes the exact
    `<start>:<lastcol><lastrow>` rectangle, so no stale rows or columns survive.
    `clear_first=True` also wipes anything below/right of the new block.
    """
    if not values:
        raise SheetError("values is empty")
    if not A1_CELL.match(start):
        raise SheetError(f"start {start!r} must be a single cell like 'A1'")
    title = resolve_tab(svc, spreadsheet_id, gid, tab)
    ncols = max(len(r) for r in values)
    # Offset both ends by `start`; computing them from the origin instead would
    # build the wrong rectangle for any start other than A1.
    m = re.match(r"^([A-Za-z]+)(\d+)$", start)
    c0, r0 = col_index(m.group(1)), int(m.group(2))
    rect = f"{start}:{col_letter(c0 + ncols - 1)}{r0 + len(values) - 1}"
    if clear_first:
        # Open-ended so anything below/right of the new block goes too.
        svc.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id, range=a1(title, f"{start}:ZZ"),
            body={}).execute()
    return write_range(svc, spreadsheet_id, rect, values, tab=title,
                       value_input_option=value_input_option)


def append_rows(svc, spreadsheet_id: str, values: list[list], *,
                gid: int | None = None, tab: str | None = None,
                value_input_option: str = "USER_ENTERED") -> dict:
    """Append after the last non-empty row. Never overwrites existing data."""
    title = resolve_tab(svc, spreadsheet_id, gid, tab)
    res = svc.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=a1(title, "A1"),
        valueInputOption=value_input_option, insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()
    return {"tab": title, "updatedRange": res.get("updates", {}).get("updatedRange"),
            "appendedRows": res.get("updates", {}).get("updatedRows")}


def clear_range(svc, spreadsheet_id: str, rng: str, *,
                gid: int | None = None, tab: str | None = None) -> dict:
    title = resolve_tab(svc, spreadsheet_id, gid, tab)
    svc.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=a1(title, rng), body={}).execute()
    return {"tab": title, "cleared": rng}


def ensure_tab(svc, spreadsheet_id: str, title: str, *,
               rows: int = 1000, cols: int = 26) -> dict:
    """Return the tab's gid, creating it if absent. Idempotent."""
    tabs = tab_map(svc, spreadsheet_id)
    for gid, name in tabs.items():
        if name == title:
            return {"tab": title, "gid": gid, "created": False}
    res = svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {
            "title": title,
            "gridProperties": {"rowCount": rows, "columnCount": cols}}}}]},
    ).execute()
    gid = res["replies"][0]["addSheet"]["properties"]["sheetId"]
    return {"tab": title, "gid": gid, "created": True}


def delete_tab(svc, spreadsheet_id: str, title: str) -> dict:
    gid = gid_for(svc, spreadsheet_id, title)
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"deleteSheet": {"sheetId": gid}}]}).execute()
    return {"deleted_tab": title, "gid": gid}


def delete_columns(svc, spreadsheet_id: str, gid: int, start: int, end: int) -> dict:
    """Delete columns by 0-based, half-open index. start=1,end=2 deletes B only."""
    _assert_gid(svc, spreadsheet_id, gid)
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"deleteDimension": {"range": {
            "sheetId": gid, "dimension": "COLUMNS",
            "startIndex": start, "endIndex": end}}}]},
    ).execute()
    return {"gid": gid, "deleted_0based": [start, end]}


def insert_columns(svc, spreadsheet_id: str, gid: int, start: int, count: int = 1,
                   inherit_from_before: bool = True) -> dict:
    _assert_gid(svc, spreadsheet_id, gid)
    svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"insertDimension": {
            "range": {"sheetId": gid, "dimension": "COLUMNS",
                      "startIndex": start, "endIndex": start + count},
            "inheritFromBefore": inherit_from_before}}]},
    ).execute()
    return {"gid": gid, "inserted_at_0based": start, "count": count}


def delete_columns_by_header(svc, spreadsheet_id: str, gid: int,
                             headers: list[str], header_row: int = 1) -> dict:
    """Delete columns by header text, right-to-left so indices stay valid.

    Deleting left-to-right shifts every later column and silently removes the
    wrong ones - the single most common way a tab gets corrupted.
    """
    from .read import read_range

    tabs = tab_map(svc, spreadsheet_id)
    if gid not in tabs:
        raise SheetError(f"gid {gid} not found. Existing: {tabs}")
    row = read_range(svc, spreadsheet_id, f"A{header_row}:ZZ{header_row}",
                     tab=tabs[gid], squared=False)
    present = [str(h).strip() for h in (row[0] if row else [])]
    idx = sorted((present.index(h) for h in headers if h in present), reverse=True)
    missing = [h for h in headers if h not in present]
    for i in idx:
        delete_columns(svc, spreadsheet_id, gid, i, i + 1)
    return {"gid": gid, "deleted_headers": [present[i] for i in idx],
            "deleted_0based": idx, "not_found": missing}


def _assert_gid(svc, spreadsheet_id: str, gid: int) -> None:
    tabs = tab_map(svc, spreadsheet_id)
    if gid not in tabs:
        raise SheetError(f"gid {gid} not found. Existing: {tabs}")
