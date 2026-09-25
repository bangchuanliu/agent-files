---
name: gsheet
kind: leaf
description: "Sheets: read, write, restructure, and format Google Sheets from the terminal with Application Default Credentials or GSHEET_CLIENT_MODULE. Covers gid-to-title resolution, ragged rows, full-range rewrites, column insert/delete, tab creation, and batchUpdate formatting. Use when: read a Google Sheet, write a Google Sheet, update a tab, spreadsheetId, gid, append rows, delete a column, freeze headers, conditional formatting, gid not found, impact sheet, or tracking sheet."
---

# Google Sheets read/write

Use the bundled `sheets` package for repeatable sheet work. Prefer it over host-specific integrations; drop to raw API calls only for operations it does not implement.

## Authentication

By default, `sheets.service()` uses Google Application Default Credentials via `google.auth.default` and `googleapiclient.discovery.build`.

A company or local layer may override client construction by setting `GSHEET_CLIENT_MODULE` to an importable module that defines:

```python
def get_client(read_only: bool): ...
```

The returned object must expose `sheets_service` and `drive_service` attributes. Provider import and construction stdout is captured and replayed to stderr so CLI JSON output stays clean.

```
scripts/
  gsheet.py            thin argparse CLI - no logic
  test_sheets.py       corruption regressions (`python3 scripts/test_sheets.py`, no network)
  sheets/
    client.py          auth, gid <-> title, A1 helpers
    read.py            ranges, header-keyed records, assertions, value parsing
    write.py           values, tabs, column structure
    format.py          batchUpdate presentation layer
```

Run `test_sheets.py` after touching `client.py`, `read.py` or `write.py` - it pins the range-bounds guard, ragged-row padding and rectangle maths that keep writes from silently corrupting a live sheet.

## CLI

Run with a Python environment that has `google-auth` and `google-api-python-client` installed and has ADC configured:

```bash
PYBIN=python3
export SKILL_DIR=<this skill's directory>   # the Python snippets below read it too
G="$SKILL_DIR/scripts/gsheet.py"
```

All subcommands print JSON on stdout; noise goes to stderr, so `2>/dev/null` is safe. A refused operation exits **4** with the reason on stderr.

```bash
# ALWAYS start here - map gid -> tab title
"$PYBIN" $G tabs <SS>

# Read: rows (squared to the range width) or header-keyed dicts
"$PYBIN" $G read    <SS> --gid 111222333 --range A1:L200
"$PYBIN" $G read    <SS> --gid 111222333 --range C2:C99 --unformatted   # numbers, not strings
"$PYBIN" $G records <SS> --tab "Data check" --limit 5

# Assert the tabs you depend on exist, before running anything expensive
"$PYBIN" $G require-tabs <SS> "Summary" "Detail"

# Write: --table sizes the range from the data and clears leftovers (preferred)
"$PYBIN" $G write <SS> --gid 111222333 --range A1 --values-file rows.json --table --dry-run
"$PYBIN" $G write <SS> --gid 111222333 --range A1 --values-file rows.json --table
"$PYBIN" $G write <SS> --gid 111222333 --range A1:L44 --values-file rows.json  # exact rectangle

"$PYBIN" $G append     <SS> --tab "Log" --values-file new_rows.json
"$PYBIN" $G clear      <SS> --gid 111222333 --range A2:L999
"$PYBIN" $G ensure-tab <SS> "Review output"          # idempotent, prints the gid

# Columns. By header is safer than by index - it deletes right-to-left.
"$PYBIN" $G delete-cols-by-header <SS> --gid 111222333 --headers "Old %" "Old count" --dry-run
"$PYBIN" $G delete-cols <SS> --gid 111222333 --start 1 --end 2     # 0-based, half-open = col B
"$PYBIN" $G insert-cols <SS> --gid 111222333 --start 7 --count 1
```

`write` reads the range back and returns `rows_after_readback` plus a sample. Check it - an update that reports `updatedRows` can still have landed in the wrong place.

## Python API

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["SKILL_DIR"], "scripts"))
import sheets
from sheets import format as F

svc = sheets.service(read_only=False)          # read_only=True for read scope

sheets.require_tabs(svc, SS, ["Summary", "Detail"])   # fail fast on a renamed tab
rows = sheets.read_records(svc, SS, gid=111222333)      # [{header: cell}, ...]
pct  = sheets.to_number(rows[0]["Change %"])           # '-22.9%' -> -22.9
key  = sheets.account_urn(rows[0]["Account ID"])        # -> account:<id>

gid = sheets.ensure_tab(svc, SS, "Review output")["gid"]
sheets.write_table(svc, SS, [header] + data, gid=gid)   # sizes + clears; no stale rows
F.apply(svc, SS, [F.freeze(gid), F.header_row(gid, len(header))])
```

| Need | Call |
|---|---|
| gid to title map | `sheets.tab_map(svc, SS)` |
| resolve gid **or** title → title | `sheets.resolve_tab(svc, SS, gid=..., tab=...)` |
| rows, squared to the range width | `sheets.read_range(...)` |
| header-keyed dicts | `sheets.read_records(...)` |
| several ranges, one round trip | `sheets.read_batch(svc, SS, ["'A'!A1:C9", "'B'!A1:B2"])` |
| assert tabs exist | `sheets.require_tabs(...)` |
| whole table, auto-sized + cleared | `sheets.write_table(...)` |
| exact rectangle | `sheets.write_range(...)` |
| add rows without overwriting | `sheets.append_rows(...)` |
| create a tab if absent | `sheets.ensure_tab(...)` |
| delete columns by header | `sheets.delete_columns_by_header(...)` |
| formatting | `from sheets import format as F` |

Every refusal raises `sheets.SheetError` with a message safe to show the user.

## Raw API recipe

For anything the script does not cover:

```python
import os, sys
sys.path.insert(0, os.path.join(os.environ["SKILL_DIR"], "scripts"))
import sheets

client = sheets.client(read_only=False)        # True = read scope, False = write scope
svc    = client.sheets_service
SS     = "<spreadsheetId>"                    # /spreadsheets/d/<THIS>/edit#gid=<gid>

# gid -> title. The API addresses ranges by TITLE; the URL carries a gid. Always map.
meta   = svc.spreadsheets().get(
            spreadsheetId=SS, fields="sheets.properties(sheetId,title)").execute()
by_gid = {s["properties"]["sheetId"]: s["properties"]["title"] for s in meta["sheets"]}
```

| Operation | Call |
|---|---|
| Read one range | `svc.spreadsheets().values().get(spreadsheetId=SS, range=f"'{title}'!A1:Z5000")` |
| Read many ranges in one round trip | `svc.spreadsheets().values().batchGet(spreadsheetId=SS, ranges=[...])` |
| Overwrite a range | `svc.spreadsheets().values().update(..., valueInputOption="USER_ENTERED", body={"values": rows})` |
| Append after the last row | `svc.spreadsheets().values().append(..., insertDataOption="INSERT_ROWS")` |
| Clear a range | `svc.spreadsheets().values().clear(spreadsheetId=SS, range=...)` |
| Structure - insert/delete rows or columns, add/rename/delete a tab, formatting, freeze | `svc.spreadsheets().batchUpdate(spreadsheetId=SS, body={"requests": [...]})` |
| Create a spreadsheet | `svc.spreadsheets().create(body={"properties": {"title": ...}})` |
| Delete a spreadsheet | `client.drive_service.files().delete(fileId=SS)` |

`batchUpdate` requests address a tab by **`sheetId` (the gid)**, not by title - the opposite of `values()` calls. Common shapes:

```python
{"deleteDimension": {"range": {"sheetId": gid, "dimension": "COLUMNS",
                               "startIndex": 7, "endIndex": 10}}}   # 0-based, half-open: H,I,J
{"insertDimension": {"range": {"sheetId": gid, "dimension": "COLUMNS",
                               "startIndex": 7, "endIndex": 8}, "inheritFromBefore": True}}
{"addSheet": {"properties": {"title": "New tab"}}}
```

`valueInputOption`: `USER_ENTERED` parses like a human typing (so `=SUM(A1:A9)` becomes a formula and `5%` becomes a number) - the right default. `RAW` stores the literal string; use it when a value must not be reinterpreted, e.g. an ID with leading zeros.

## Formatting (`sheets/format.py`)

`read.py`/`write.py` handle values and structure. `format.py` handles everything the
`batchUpdate` presentation layer does - freeze,
merge, banding, number formats, gradients, widths. Every function returns a **request dict**;
compose a list and hand it to `apply()`.

```python
import os, sys; sys.path.insert(0, os.path.join(os.environ["SKILL_DIR"], "scripts"))
from sheets import format as F

n = len(rows)                                     # incl. header
reqs = [
    F.freeze(gid, rows=1, cols=2),
    F.header_row(gid, ncols=7),
    F.number_format(gid, col=2, pattern=F.PCT,   end_row=n),
    F.number_format(gid, col=6, pattern=F.MONEY, end_row=n),
    F.col_width(gid, 1, 105),
    F.banding(gid, nrows=n, ncols=7),
    F.gradient_3stop(gid, col=2, end_row=n),      # -100 red -> -30 orange -> 0 white
    F.gradient_min_to_zero(gid, col=3, end_row=n),
    F.bold_row(gid, row=n - 1, ncols=7),          # TOTAL row
]
print(F.apply(svc, SS, reqs))    # {"applied": 9, "failed": []}
```

`apply()` sends requests **one at a time by default**, so one bad request (a duplicate banding,
say) cannot roll back the whole pass - it returns a `failed` list naming the request kind and
the error. Pass `isolate=False` for a single atomic batch when you want all-or-nothing.

Constants provided: `HEADER` / `BAND2` / `SECT` / `WHITE` / `GREEN` / `GMIN` / `GMID` / `DRED`,
and patterns `PCT` (`0.0"%"`), `COUNT` (`#,##0`), `ID` (`0`), `MONEY` (`$#,##0.00`),
`FRACTION_PCT` (`0.00%`, for values stored as fractions).

### Formatting traps

- **A frozen column silently breaks every full-width merge.** Sheets rejects `mergeCells` that
  spans the frozen/non-frozen boundary. If the tab has merged section-header rows, use
  `F.freeze(gid, rows=1, cols=0)`.
- **A merge keeps only the top-left cell's value and destroys the rest.** Never merge a row that
  carries data in other columns.
- **Format from the in-memory row list, never from a re-read of the sheet.** Tag each row as you
  build it (`hdr | sect | desc | data | total | blank`) and format strictly by tag. Inferring
  roles from values ("col A filled and col B empty ⇒ section row") misclassifies ordinary rows -
  it will merge a real data row and delete its value. This has happened; it is not theoretical.
- **`addBanding` fails if the range already has banding.** Apply once. To re-run a formatting
  pass, `F.clear_formatting(gid, nrows, ncols)` first (unmerges + clears `userEnteredFormat`),
  rewrite the values, then reapply.
- **Numbers written as strings never format.** `'1,234'` is text; `0.0"%"` will do nothing to
  it. Write numerics as numbers (or rewrite them with a `RAW` `values().batchUpdate`) *before*
  applying number formats and gradients.
- **Percent formats depend on storage.** `0.0"%"` displays a raw `-22.9` as `-22.9%`; `0.00%`
  multiplies by 100, so it expects `-0.229`. Pick the pattern to match how you stored the value.

## Verify before you finish

After building a sheet, assert the result rather than trusting the API's success response:

- Row count written == row count of the source set (all pages pulled, nothing truncated).
- Every column header matches the spec verbatim.
- Totals reconcile against the per-row data.
- Numeric columns are stored as numbers (`valueRenderOption="UNFORMATTED_VALUE"` returns
  `int`/`float`, not `str`).
- No merge swallowed a data cell - re-read the range and check no expected value is missing.

If the sheet has a checker script alongside its prompt (e.g. `verify_sheet.py`), run it - and
when you change a tab's shape, add the matching assertion in the same change, or the checker
silently stops covering it.

## Traps

These have each cost real debugging time.

- **Ragged rows - the expensive one.** `values().get` **omits trailing empty cells**, so rows
  come back at different lengths and a fully-empty trailing column vanishes entirely. Every
  downstream index then shifts left. Never do a read-modify-write on a partial range: it
  silently drops columns. Pad to the *requested range width* (`read` does this by default), not to the
  widest row, and assert the shape before writing anything back.
- **Prefer an authoritative full-range rewrite over patching.** If you are restructuring
  columns, rebuild the whole `A1:<last-col><last-row>` block in memory, assert the row count
  and column count, then write it once. Incremental patches to a live sheet drift.
- **A short payload does not clear the rows below it.** `values().update` only touches the
  cells you send. Writing 10 rows over a 40-row range leaves rows 11–40 intact and now stale.
  Either send the full rectangle, or `clear()` first. `gsheet.py write` rejects ranges without
  row bounds (`A:L`) for this reason.
- **The gid in a URL may not exist.** Tabs get deleted and shared links go stale. A `KeyError`
  on `by_gid[gid]` is the *correct* outcome - print the real `{gid: title}` map and pick the
  right tab, or ask. **Never** silently fall back to the first tab or `Sheet1`.
- **Provider code can accidentally print warnings to *stdout*.** That will corrupt
  JSON you print. `client.py` captures stdout around provider import/construction and
  replays any noise to stderr.
- **Numbers arrive as display strings** - `'-22.9%'`, `'2,074'`, `'$1,234.00'`. Strip `%`, `,`
  and currency symbols before arithmetic. What you read back is the *formatted* value, so a
  round trip can change the stored type. Use `valueRenderOption="UNFORMATTED_VALUE"` when you
  need the underlying number.
- **`batchUpdate` column indices are 0-based and half-open**; A1 notation is 1-based and
  inclusive. `--start 1 --end 2` deletes column **B**, one column.
- **Concurrent writers corrupt ranges.** Never fan out parallel agents that each write to the
  same tab - their range maths is computed against different snapshots. Do structural edits
  yourself, serially, and let agents return values for you to write.
- Do not name a scratch file `inspect.py` (shadows stdlib), and never use
  `security find-generic-password` (blocking GUI prompt).

## Before you write to someone else's sheet

1. `tabs` first, and confirm the tab title matches what the user described.
2. Read the current range and report what is there **before** overwriting.
3. Use `--dry-run` for anything structural.
4. Read back after writing, and say what changed.

A sheet is usually a shared deliverable. Treat an overwrite as destructive, because for the
other people reading it, it is.
