#!/usr/bin/env python
"""Formatting: composable `batchUpdate` request builders.

`read.py` and `write.py` cover values and structure. This module covers the
*presentation* layer: freezing, merging, banding, number formats, gradients,
column widths.

Every function returns a plain request dict - compose a list, then hand it to
`apply()`. Nothing here talks to the network except `apply()`.

    from sheets import format as F
    reqs = [
        F.freeze(gid, rows=1, cols=2),
        F.header_row(gid, ncols=7),
        F.number_format(gid, col=2, pattern='0.0"%"', end_row=n),
        F.banding(gid, nrows=n, ncols=7),
        F.gradient_3stop(gid, col=2, end_row=n),
    ]
    F.apply(svc, SS, reqs)          # per-request isolation; returns a report

Colours below provide a consistent high-contrast presentation palette.
"""

from __future__ import annotations

from typing import Any

HEADER = {"red": 0.039215688, "green": 0.28627452, "blue": 0.5764706}
BAND2 = {"red": 0.9490196, "green": 0.95686275, "blue": 0.9764706}
SECT = {"red": 0.84705883, "green": 0.8980392, "blue": 0.96862745}
WHITE = {"red": 1, "green": 1, "blue": 1}
GREEN = {"red": 0.85, "green": 0.92, "blue": 0.83}
GMIN = {"red": 0.85882354, "green": 0.2, "blue": 0.2}
GMID = {"red": 0.9764706, "green": 0.7490196, "blue": 0.54901963}
DRED = {"red": 0.7764706, "green": 0.14901961, "blue": 0.14901961}

PCT = '0.0"%"'
COUNT = "#,##0"
ID = "0"
MONEY = "$#,##0.00"
FRACTION_PCT = "0.00%"


def cs(c: dict) -> dict:
    return {"rgbColor": c}


def grid(gid: int, sr: int, er: int, sc: int, ec: int) -> dict:
    """0-based, half-open GridRange."""
    return {"sheetId": gid, "startRowIndex": sr, "endRowIndex": er,
            "startColumnIndex": sc, "endColumnIndex": ec}


def freeze(gid: int, rows: int = 1, cols: int = 0) -> dict:
    """Freeze header rows/columns.

    ⚠️ `cols > 0` makes Sheets REJECT any mergeCells that spans the frozen
    boundary. If the tab has full-width merged section headers, pass cols=0.
    """
    return {"updateSheetProperties": {
        "properties": {"sheetId": gid,
                       "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}}


def header_row(gid: int, ncols: int, row: int = 0, color: dict = HEADER) -> dict:
    return {"repeatCell": {
        "range": grid(gid, row, row + 1, 0, ncols),
        "cell": {"userEnteredFormat": {
            "backgroundColorStyle": cs(color),
            "textFormat": {"bold": True, "foregroundColorStyle": cs(WHITE)},
            "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP"}},
        "fields": ("userEnteredFormat(backgroundColorStyle,textFormat,"
                   "horizontalAlignment,verticalAlignment,wrapStrategy)")}}


def number_format(gid: int, col: int, pattern: str, end_row: int,
                  start_row: int = 1, align: str = "RIGHT") -> dict:
    return {"repeatCell": {
        "range": grid(gid, start_row, end_row, col, col + 1),
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "NUMBER", "pattern": pattern},
            "horizontalAlignment": align}},
        "fields": "userEnteredFormat(numberFormat,horizontalAlignment)"}}


def align(gid: int, col: int, end_row: int, how: str = "LEFT",
          start_row: int = 1, wrap: bool = False) -> dict:
    fmt: dict[str, Any] = {"horizontalAlignment": how}
    fields = "userEnteredFormat.horizontalAlignment"
    if wrap:
        fmt["wrapStrategy"] = "WRAP"
        fields = "userEnteredFormat(horizontalAlignment,wrapStrategy)"
    return {"repeatCell": {"range": grid(gid, start_row, end_row, col, col + 1),
                           "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def bold_row(gid: int, row: int, ncols: int, color: dict | None = GREEN) -> dict:
    fmt: dict[str, Any] = {"textFormat": {"bold": True}}
    fields = "userEnteredFormat.textFormat.bold"
    if color:
        fmt["backgroundColorStyle"] = cs(color)
        fields = "userEnteredFormat(backgroundColorStyle,textFormat.bold)"
    return {"repeatCell": {"range": grid(gid, row, row + 1, 0, ncols),
                           "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def col_width(gid: int, col: int, px: int) -> dict:
    return {"updateDimensionProperties": {
        "range": {"sheetId": gid, "dimension": "COLUMNS",
                  "startIndex": col, "endIndex": col + 1},
        "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def row_height(gid: int, row: int, px: int) -> dict:
    return {"updateDimensionProperties": {
        "range": {"sheetId": gid, "dimension": "ROWS",
                  "startIndex": row, "endIndex": row + 1},
        "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def merge(gid: int, row: int, ncols: int) -> dict:
    """Merge one full-width row. A merge keeps ONLY the top-left cell's value -
    never merge a row whose other cells carry data."""
    return {"mergeCells": {"range": grid(gid, row, row + 1, 0, ncols),
                           "mergeType": "MERGE_ALL"}}


def section_row(gid: int, row: int, ncols: int) -> list[dict]:
    return [merge(gid, row, ncols),
            {"repeatCell": {
                "range": grid(gid, row, row + 1, 0, ncols),
                "cell": {"userEnteredFormat": {
                    "backgroundColorStyle": cs(SECT),
                    "textFormat": {"bold": True, "fontSize": 11},
                    "horizontalAlignment": "LEFT", "verticalAlignment": "MIDDLE",
                    "wrapStrategy": "WRAP"}},
                "fields": ("userEnteredFormat(backgroundColorStyle,textFormat,"
                           "horizontalAlignment,verticalAlignment,wrapStrategy)")}}]


def banding(gid: int, nrows: int, ncols: int) -> dict:
    """Zebra striping. Fails if the range ALREADY has banding - apply once, or
    clear existing bandedRanges first (see `clear_formatting`)."""
    return {"addBanding": {"bandedRange": {
        "range": grid(gid, 0, nrows, 0, ncols),
        "rowProperties": {"headerColorStyle": cs(HEADER),
                          "firstBandColorStyle": cs(WHITE),
                          "secondBandColorStyle": cs(BAND2)}}}}


def gradient_3stop(gid: int, col: int, end_row: int, start_row: int = 1,
                   lo: str = "-100", mid: str = "-30", hi: str = "0") -> dict:
    return {"addConditionalFormatRule": {"rule": {
        "ranges": [grid(gid, start_row, end_row, col, col + 1)],
        "gradientRule": {
            "minpoint": {"colorStyle": cs(GMIN), "type": "NUMBER", "value": lo},
            "midpoint": {"colorStyle": cs(GMID), "type": "NUMBER", "value": mid},
            "maxpoint": {"colorStyle": cs(WHITE), "type": "NUMBER", "value": hi}}},
        "index": 0}}


def gradient_min_to_zero(gid: int, col: int, end_row: int, start_row: int = 1) -> dict:
    return {"addConditionalFormatRule": {"rule": {
        "ranges": [grid(gid, start_row, end_row, col, col + 1)],
        "gradientRule": {"minpoint": {"colorStyle": cs(DRED), "type": "MIN"},
                         "maxpoint": {"colorStyle": cs(WHITE), "type": "NUMBER",
                                      "value": "0"}}},
        "index": 0}}


def clear_formatting(gid: int, nrows: int, ncols: int) -> list[dict]:
    """Reset a tab so formatting can be reapplied from scratch.

    Re-running a format pass over an already-formatted tab compounds merges and
    duplicate banding. Unmerge and clear first.
    """
    r = grid(gid, 0, nrows, 0, ncols)
    return [{"unmergeCells": {"range": r}},
            {"repeatCell": {"range": r, "cell": {"userEnteredFormat": {}},
                            "fields": "userEnteredFormat"}}]


def apply(svc, spreadsheet_id: str, requests: list[dict],
          isolate: bool = True) -> dict:
    """Send requests. `isolate=True` sends them one at a time so a single bad
    request (e.g. duplicate banding) cannot roll back the whole batch."""
    if not isolate:
        svc.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
        return {"applied": len(requests), "failed": []}

    failed = []
    for i, req in enumerate(requests):
        try:
            svc.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": [req]}).execute()
        except Exception as exc:  # noqa: BLE001 - report, don't abort the pass
            failed.append({"index": i, "kind": next(iter(req)), "error": str(exc)[:300]})
    return {"applied": len(requests) - len(failed), "failed": failed}
