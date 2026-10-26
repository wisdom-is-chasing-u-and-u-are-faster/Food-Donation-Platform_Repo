import os
from pathlib import Path


def test_frontend_files_exist():
    repo_root = Path(__file__).resolve().parent.parent
    public_dir = repo_root / "public"

    assert (public_dir / "index.html").exists(), "public/index.html must exist"
    assert (public_dir / "pages" /
            "administrator.html").exists(), "administrator.html must exist"
    assert (public_dir / "pages" / "donor.html").exists(), "donor.html must exist"
    assert (public_dir / "pages" /
            "recipient.html").exists(), "recipient.html must exist"
    assert (public_dir / "css" / "style.css").exists(), "style.css must exist"
    assert (public_dir / "js" / "api.js").exists(), "api.js must exist"
    assert (public_dir / "js" / "dashboard.js").exists(), "dashboard.js must exist"


def test_frontend_html_references_scripts():
    repo_root = Path(__file__).resolve().parent.parent
    public_dir = repo_root / "public"

    html_files = [
        public_dir / "index.html",
        public_dir / "pages" / "administrator.html",
        public_dir / "pages" / "donor.html",
        public_dir / "pages" / "recipient.html"
    ]

    for f in html_files:
        content = f.read_text(encoding="utf-8")
        assert "api.js" in content, f"{f.name} must reference api.js"
        assert "dashboard.js" in content, f"{f.name} must reference dashboard.js"
        assert "refreshTimerDisplay" in content, f"{f.name} must include refresh countdown timer element"
