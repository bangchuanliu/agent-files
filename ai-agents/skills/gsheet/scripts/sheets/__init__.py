"""Google Sheets I/O using the configured Google client provider.

    import sys
    sys.path.insert(0, "<skill-dir>/scripts")
    import sheets
    from sheets import format as F

    svc = sheets.service(read_only=False)
    sheets.require_tabs(svc, SS, ["Summary", "Detail"])
    rows = sheets.read_records(svc, SS, gid=111222333)
    sheets.write_table(svc, SS, values, tab="Summary")
    F.apply(svc, SS, [F.freeze(gid), F.header_row(gid, 7)])

Layout:
  client.py  auth, gid<->title, A1 helpers        read.py   ranges, records, assertions
  write.py   values, tabs, columns                format.py batchUpdate presentation
"""

from .client import (SheetError, a1, client, col_index, col_letter, gid_for,
                     range_width, resolve_tab, service, tab_map)
from .read import (account_urn, pad, read_batch, read_range, read_records,
                   require_tabs, to_number)
from .write import (append_rows, clear_range, delete_columns,
                    delete_columns_by_header, delete_tab, ensure_tab,
                    insert_columns, write_range, write_table)

__all__ = [
    "SheetError", "a1", "client", "col_index", "col_letter", "gid_for",
    "range_width", "resolve_tab", "service", "tab_map",
    "account_urn", "pad", "read_batch", "read_range", "read_records",
    "require_tabs", "to_number",
    "append_rows", "clear_range", "delete_columns", "delete_columns_by_header",
    "delete_tab", "ensure_tab", "insert_columns", "write_range", "write_table",
]
