#!/usr/bin/env python
"""Google Sheets CLI - a thin argparse shell over the `sheets` package.

All logic lives in sheets/{client,read,write,format}.py; this file only parses
arguments and prints JSON. Run it with a Python environment that has google-auth and google-api-python-client installed:

    python3 gsheet.py tabs <spreadsheetId>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sheets  # noqa: E402
from sheets.client import SheetError  # noqa: E402

WRITE_CMDS = {"write", "append", "clear", "delete-cols", "delete-cols-by-header",
              "insert-cols", "ensure-tab"}


def _load(path: str) -> list[list]:
    with open(path) as fh:
        values = json.load(fh)
    if not isinstance(values, list) or not all(isinstance(r, list) for r in values):
        raise SheetError(f"{path} must contain a JSON array of arrays")
    return values


def cmd_tabs(a, svc):
    return sheets.tab_map(svc, a.spreadsheet)


def cmd_read(a, svc):
    rows = sheets.read_range(svc, a.spreadsheet, a.range, gid=a.gid, tab=a.tab,
                             squared=not a.raw, unformatted=a.unformatted)
    return {"tab": sheets.resolve_tab(svc, a.spreadsheet, a.gid, a.tab),
            "range": a.range, "row_count": len(rows),
            "col_count": len(rows[0]) if rows else 0, "rows": rows}


def cmd_records(a, svc):
    recs = sheets.read_records(svc, a.spreadsheet, a.range, gid=a.gid, tab=a.tab,
                               header_row=a.header_row)
    return {"tab": sheets.resolve_tab(svc, a.spreadsheet, a.gid, a.tab),
            "record_count": len(recs), "records": recs[: a.limit] if a.limit else recs}


def cmd_require_tabs(a, svc):
    sheets.require_tabs(svc, a.spreadsheet, a.tabs)
    return {"ok": True, "present": a.tabs}


def cmd_write(a, svc):
    values = _load(a.values_file)
    if a.dry_run:
        before = sheets.read_range(svc, a.spreadsheet, a.range, gid=a.gid, tab=a.tab)
        return {"dry_run": True, "range": a.range,
                "rows_currently_present": len(before), "rows_to_write": len(values)}
    if a.table:
        return sheets.write_table(svc, a.spreadsheet, values, gid=a.gid, tab=a.tab,
                                  start=a.range.split(":")[0], clear_first=not a.no_clear,
                                  value_input_option=a.value_input_option)
    out = sheets.write_range(svc, a.spreadsheet, a.range, values, gid=a.gid, tab=a.tab,
                             value_input_option=a.value_input_option)
    out["readback"] = out["readback"][: a.readback]
    return out


def cmd_append(a, svc):
    return sheets.append_rows(svc, a.spreadsheet, _load(a.values_file),
                              gid=a.gid, tab=a.tab)


def cmd_clear(a, svc):
    return sheets.clear_range(svc, a.spreadsheet, a.range, gid=a.gid, tab=a.tab)


def cmd_ensure_tab(a, svc):
    return sheets.ensure_tab(svc, a.spreadsheet, a.title)


def cmd_delete_cols(a, svc):
    if a.dry_run:
        return {"dry_run": True, "gid": a.gid, "would_delete_0based": [a.start, a.end]}
    return sheets.delete_columns(svc, a.spreadsheet, a.gid, a.start, a.end)


def cmd_delete_cols_by_header(a, svc):
    if a.dry_run:
        row = sheets.read_range(svc, a.spreadsheet, f"A{a.header_row}:ZZ{a.header_row}",
                                gid=a.gid, squared=False)
        present = [str(h).strip() for h in (row[0] if row else [])]
        return {"dry_run": True,
                "would_delete": [h for h in a.headers if h in present],
                "not_found": [h for h in a.headers if h not in present]}
    return sheets.delete_columns_by_header(svc, a.spreadsheet, a.gid, a.headers,
                                           header_row=a.header_row)


def cmd_insert_cols(a, svc):
    return sheets.insert_columns(svc, a.spreadsheet, a.gid, a.start, a.count)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def with_tab(sp):
        sp.add_argument("spreadsheet", help="id from /spreadsheets/d/<THIS>/edit")
        sp.add_argument("--gid", type=int, help="gid from the URL fragment")
        sp.add_argument("--tab", help="tab title (alternative to --gid)")
        return sp

    sp = sub.add_parser("tabs", help="list gid -> title")
    sp.add_argument("spreadsheet")

    sp = with_tab(sub.add_parser("read", help="read a range as rows"))
    sp.add_argument("--range", default="A1:Z5000")
    sp.add_argument("--raw", action="store_true", help="do not square ragged rows")
    sp.add_argument("--unformatted", action="store_true",
                    help="underlying numbers instead of display strings")

    sp = with_tab(sub.add_parser("records", help="read a range as header-keyed dicts"))
    sp.add_argument("--range", default="A1:Z5000")
    sp.add_argument("--header-row", type=int, default=0)
    sp.add_argument("--limit", type=int, default=0)

    sp = sub.add_parser("require-tabs", help="assert tabs exist, else fail loudly")
    sp.add_argument("spreadsheet")
    sp.add_argument("tabs", nargs="+")

    sp = with_tab(sub.add_parser("write", help="overwrite a range from a JSON file"))
    sp.add_argument("--range", required=True, help="explicit full range, e.g. A1:L44")
    sp.add_argument("--values-file", required=True)
    sp.add_argument("--table", action="store_true",
                    help="size the range from the data and clear the tab first")
    sp.add_argument("--no-clear", action="store_true", help="with --table, skip the clear")
    sp.add_argument("--value-input-option", default="USER_ENTERED",
                    choices=["USER_ENTERED", "RAW"])
    sp.add_argument("--readback", type=int, default=3)
    sp.add_argument("--dry-run", action="store_true")

    sp = with_tab(sub.add_parser("append", help="append rows after the last one"))
    sp.add_argument("--values-file", required=True)

    sp = with_tab(sub.add_parser("clear", help="clear a range"))
    sp.add_argument("--range", required=True)

    sp = sub.add_parser("ensure-tab", help="create a tab if absent; print its gid")
    sp.add_argument("spreadsheet")
    sp.add_argument("title")

    sp = sub.add_parser("delete-cols", help="delete a 0-based half-open column range")
    sp.add_argument("spreadsheet")
    sp.add_argument("--gid", type=int, required=True)
    sp.add_argument("--start", type=int, required=True, help="0-based inclusive (A=0)")
    sp.add_argument("--end", type=int, required=True, help="0-based exclusive")
    sp.add_argument("--dry-run", action="store_true")

    sp = sub.add_parser("delete-cols-by-header",
                        help="delete columns by header text (right-to-left, index-safe)")
    sp.add_argument("spreadsheet")
    sp.add_argument("--gid", type=int, required=True)
    sp.add_argument("--headers", nargs="+", required=True)
    sp.add_argument("--header-row", type=int, default=1, help="1-based sheet row")
    sp.add_argument("--dry-run", action="store_true")

    sp = sub.add_parser("insert-cols", help="insert blank columns")
    sp.add_argument("spreadsheet")
    sp.add_argument("--gid", type=int, required=True)
    sp.add_argument("--start", type=int, required=True, help="0-based insert position")
    sp.add_argument("--count", type=int, default=1)
    return p


HANDLERS = {
    "tabs": cmd_tabs, "read": cmd_read, "records": cmd_records,
    "require-tabs": cmd_require_tabs, "write": cmd_write, "append": cmd_append,
    "clear": cmd_clear, "ensure-tab": cmd_ensure_tab, "delete-cols": cmd_delete_cols,
    "delete-cols-by-header": cmd_delete_cols_by_header, "insert-cols": cmd_insert_cols,
}


def main() -> int:
    a = build_parser().parse_args()
    writes = a.cmd in WRITE_CMDS and not getattr(a, "dry_run", False)
    try:
        svc = sheets.service(read_only=not writes)
        print(json.dumps(HANDLERS[a.cmd](a, svc), indent=2, ensure_ascii=False))
    except SheetError as exc:
        print(str(exc), file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
