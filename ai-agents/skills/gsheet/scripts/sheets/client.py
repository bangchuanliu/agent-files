"""Client construction, tab resolution and A1 helpers.

Everything that needs to talk to Google goes through `service()`. Nothing else
in the package builds a client, so the stdout-noise suppression lives in exactly
one place.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import logging
import os
import re
import sys
from dataclasses import dataclass

A1_SPAN = re.compile(r"^([A-Za-z]+)\d*:([A-Za-z]+)\d*$")
# Both endpoints must carry a row number. A half-open range like "A1:L" is the
# dangerous case: it looks bounded but `values().update` still leaves every row
# below the payload intact and stale.
A1_CELL = re.compile(r"^[A-Za-z]+\d+$")
A1_BOUNDED = re.compile(r"^[A-Za-z]+\d+:[A-Za-z]+\d+$")

_CLIENT_CACHE: dict[bool, object] = {}


@dataclass(frozen=True)
class GoogleClient:
    """Small service holder matching the attributes used by this package."""

    sheets_service: object
    drive_service: object


def _scopes(read_only: bool) -> list[str]:
    if read_only:
        return [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ]
    return [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]


def _adc_client(read_only: bool) -> GoogleClient:
    """Build a Google API client from Application Default Credentials."""
    import google.auth
    from googleapiclient.discovery import build

    credentials, _ = google.auth.default(scopes=_scopes(read_only))
    return GoogleClient(
        sheets_service=build("sheets", "v4", credentials=credentials),
        drive_service=build("drive", "v3", credentials=credentials),
    )


def _provider_client(read_only: bool):
    module_name = os.environ.get("GSHEET_CLIENT_MODULE")
    if not module_name:
        return _adc_client(read_only)
    module = importlib.import_module(module_name)
    get_client = getattr(module, "get_client", None)
    if get_client is None:
        raise SheetError(f"{module_name} must define get_client(read_only: bool)")
    return get_client(read_only=read_only)


def client(read_only: bool = True):
    """Google client, cached by access level.

    By default this uses Google Application Default Credentials. Set
    GSHEET_CLIENT_MODULE to an importable module that defines
    get_client(read_only: bool) to supply a custom client. Provider imports and
    construction are stdout-captured because CLI commands print JSON on stdout.
    Any provider noise is replayed to stderr instead.
    """
    if read_only in _CLIENT_CACHE:
        return _CLIENT_CACHE[read_only]

    logging.disable(logging.INFO)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        c = _provider_client(read_only)
    noise = buf.getvalue()
    if noise.strip():
        print(noise, end="", file=sys.stderr)

    _CLIENT_CACHE[read_only] = c
    return c


def service(read_only: bool = True):
    """Sheets v4 service. Use `client(...).drive_service` for Drive operations."""
    return client(read_only).sheets_service


def tab_map(svc, spreadsheet_id: str) -> dict[int, str]:
    """{gid: title}. The API addresses ranges by TITLE; URLs carry a gid."""
    meta = svc.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets.properties(sheetId,title)"
    ).execute()
    return {s["properties"]["sheetId"]: s["properties"]["title"] for s in meta["sheets"]}


def resolve_tab(svc, spreadsheet_id: str, gid: int | None = None,
                tab: str | None = None) -> str:
    """gid or title -> title.

    A stale gid or an unknown title is a hard error that prints the real tab map.
    Never fall back to the first tab: that silently writes to the wrong place.
    """
    tabs = tab_map(svc, spreadsheet_id)
    if tab is not None:
        if tab not in tabs.values():
            raise SheetError(f"tab {tab!r} not found. Existing tabs: "
                             f"{json.dumps(tabs, indent=2)}")
        return tab
    if gid is None:
        raise SheetError("pass gid or tab")
    if gid not in tabs:
        raise SheetError(f"gid {gid} does not exist (stale link?). Existing tabs: "
                         f"{json.dumps(tabs, indent=2)}")
    return tabs[gid]


def gid_for(svc, spreadsheet_id: str, title: str) -> int:
    for gid, name in tab_map(svc, spreadsheet_id).items():
        if name == title:
            return gid
    raise SheetError(f"tab {title!r} not found")


def a1(title: str, rng: str) -> str:
    """Quote a tab title into an A1 range. Titles with spaces/symbols need this.

    A literal apostrophe in the title must be doubled, or the reference is
    malformed and every read/write against tabs like `Q3'25` fails.
    """
    return "'{}'!{}".format(title.replace("'", "''"), rng)


def col_index(letters: str) -> int:
    """'A' -> 0, 'Z' -> 25, 'AA' -> 26."""
    n = 0
    for ch in letters.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def col_letter(index: int) -> str:
    """0 -> 'A', 25 -> 'Z', 26 -> 'AA'."""
    s = ""
    n = index + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def range_width(rng: str) -> int | None:
    """Column count implied by an A1 range, or None if it has no column bounds."""
    m = A1_SPAN.match(rng)
    if not m:
        return None
    return col_index(m.group(2)) - col_index(m.group(1)) + 1


def has_row_bounds(rng: str) -> bool:
    """True only when every endpoint of `rng` names a row.

    `A1:L10` and `A1` qualify; `A1:L`, `A:L10` and `A:L` do not.
    """
    return bool(A1_BOUNDED.match(rng) or A1_CELL.match(rng))


class SheetError(RuntimeError):
    """Operation refused or impossible - message is safe to show the user."""
