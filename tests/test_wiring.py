import os
from pathlib import Path


def test_api_client_endpoints_coverage():
    repo_root = Path(__file__).resolve().parent.parent
    api_js = (
        repo_root /
        "public" /
        "js" /
        "api.js").read_text(
        encoding="utf-8")

    expected_methods = [
        "checkHealth",
        "getAdminTelemetry",
        "getDonorTelemetry",
        "getRecipientTelemetry",
        "createDonation",
        "listDonations",
        "findRecipients",
        "reserveDonation",
        "updateDispatch",
        "verifyHandshake",
        "getCustodyLedger",
        "logThermalReading",
        "getESGAnalytics"
    ]

    for m in expected_methods:
        assert m in api_js, f"api.js must implement client method: {m}"


def test_dashboard_controller_auto_refresh_wiring():
    repo_root = Path(__file__).resolve().parent.parent
    dash_js = (
        repo_root /
        "public" /
        "js" /
        "dashboard.js").read_text(
        encoding="utf-8")

    assert "startAutoRefresh" in dash_js
    assert "updateCountdownUI" in dash_js
    assert "loadActiveViewData" in dash_js
    assert "setInterval" in dash_js
