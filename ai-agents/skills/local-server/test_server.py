#!/usr/bin/env python3
"""Regression tests for local-server path safety."""

from __future__ import annotations

import http.client
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from server import make_handler, save_file  # noqa: E402


class LocalServerPathSafetyTest(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(__file__).resolve().parent / ".test-work"
        self.scratch.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="local-server-", dir=self.scratch)
        self.root = Path(self.tmp.name)
        self.serve_dir = self.root / "served"
        self.serve_dir.mkdir()
        self.secret = self.root / "secret.html"
        self.secret.write_text("<html>secret</html>", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()
        if self.scratch.exists() and not any(self.scratch.iterdir()):
            self.scratch.rmdir()

    def test_save_file_accepts_direct_html_child(self):
        status, message = save_file(self.serve_dir, "page.html", "<html>ok</html>")

        self.assertEqual(status, "ok")
        self.assertEqual(message, "saved page.html")
        self.assertEqual((self.serve_dir / "page.html").read_text(encoding="utf-8"),
                         "<html>ok</html>")

    def test_save_file_rejects_traversal_and_subdirectories(self):
        for bad_path in ("../secret.html", "nested/page.html", r"nested\\page.html"):
            with self.subTest(path=bad_path):
                status, message = save_file(self.serve_dir, bad_path, "x")
                self.assertEqual(status, "error")
                self.assertIn("invalid path", message)
                self.assertEqual(self.secret.read_text(encoding="utf-8"), "<html>secret</html>")

    @unittest.skipUnless(hasattr(Path, "symlink_to"), "symlink unsupported")
    def test_save_file_rejects_symlink_escape(self):
        link = self.serve_dir / "link.html"
        try:
            link.symlink_to(self.secret)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")

        status, message = save_file(self.serve_dir, "link.html", "<html>changed</html>")

        self.assertEqual(status, "error")
        self.assertIn("invalid path", message)
        self.assertEqual(self.secret.read_text(encoding="utf-8"), "<html>secret</html>")

    def test_get_rejects_encoded_parent_traversal(self):
        (self.serve_dir / "page.html").write_text("<html>ok</html>", encoding="utf-8")
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.serve_dir))
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=5)
            conn.request("GET", "/page.html")
            self.assertEqual(conn.getresponse().status, 200)
            conn.close()

            for path in ("/../secret.html", "/%2e%2e/secret.html"):
                with self.subTest(path=path):
                    conn = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=5)
                    conn.request("GET", path)
                    self.assertEqual(conn.getresponse().status, 404)
                    conn.close()
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
