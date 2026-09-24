#!/usr/bin/env python3
"""Regression fixtures for the gsheet helpers.

    python3 scripts/test_sheets.py

Every case here is a corruption bug caught in review before the skill shipped.
They are all pure-function cases - no network, no credentials - because the
whole point of this module is that the dangerous paths are decidable offline.

Exit 0 = all pass, 1 = failures.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sheets.client import a1, col_index, col_letter, has_row_bounds  # noqa: E402
from sheets.read import pad  # noqa: E402

CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def half_open_range_is_not_bounded():
    """`A1:L` names no end row, so update() leaves every row below stale."""
    assert has_row_bounds("A1:L") is False
    assert has_row_bounds("A:L10") is False
    assert has_row_bounds("A:L") is False


@case
def fully_bounded_range_is_accepted():
    assert has_row_bounds("A1:L10") is True
    assert has_row_bounds("AA2:ZZ100") is True


@case
def single_cell_is_bounded():
    assert has_row_bounds("A1") is True


@case
def apostrophe_in_tab_title_is_doubled():
    """`'Q3'25'!A1` is a malformed reference; the quote must be doubled."""
    assert a1("Q3'25 data", "A1:B2") == "'Q3''25 data'!A1:B2"
    assert a1("Summary", "A1:B2") == "'Summary'!A1:B2"


@case
def ragged_rows_are_squared_to_the_range_width():
    """Short rows must be padded, or their tail columns keep the old values."""
    assert pad([[1, 2], [1, 2, 3, 4]], 4) == [[1, 2, "", ""], [1, 2, 3, 4]]


@case
def pad_never_truncates_an_overwide_row():
    """Widening past the range fails loudly at the API; silent truncation would not."""
    assert pad([[1, 2, 3]], 2) == [[1, 2, 3]]


def _rect(start, values):
    """Mirror of write_table's rectangle computation."""
    m = re.match(r"^([A-Za-z]+)(\d+)$", start)
    c0, r0 = col_index(m.group(1)), int(m.group(2))
    ncols = max(len(r) for r in values)
    return f"{start}:{col_letter(c0 + ncols - 1)}{r0 + len(values) - 1}"


@case
def table_rect_offsets_both_ends_by_start():
    """Computing the end from the origin instead wrote C5:C10 for a 10x3 block."""
    data = [[1, 2, 3]] * 10
    assert _rect("A1", data) == "A1:C10"
    assert _rect("C5", data) == "C5:E14"


def main():
    failed = 0
    for fn in CASES:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc or 'assertion failed'}")
        else:
            print(f"PASS  {fn.__name__}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
