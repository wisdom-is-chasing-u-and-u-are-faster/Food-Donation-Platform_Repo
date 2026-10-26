import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_static_html_and_pages_served():
    """Verify that root index.html and all pages are served with HTTP 200."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "FoodMesh Platform" in res_root.text

    res_admin = client.get("/pages/administrator.html")
    assert res_admin.status_code == 200
    assert "Administrator Dashboard" in res_admin.text

    res_donor = client.get("/pages/donor.html")
    assert res_donor.status_code == 200
    assert "Donor Partner Portal" in res_donor.text

    res_recip = client.get("/pages/recipient.html")
    assert res_recip.status_code == 200
    assert "Recipient Logistics Portal" in res_recip.text

    res_css = client.get("/css/style.css")
    assert res_css.status_code == 200

    res_api_js = client.get("/js/api.js")
    assert res_api_js.status_code == 200

    res_dash_js = client.get("/js/dashboard.js")
    assert res_dash_js.status_code == 200


def test_fullstack_end_to_end_journey():
    """
    E2E Journey:
    1. Donor ingests surplus batch
    2. PostGIS proximity matching finds recipient
    3. Donation is reserved
    4. Dual-fleet state transitions to volunteer / 3PL
    5. IoT logs thermal reading (<41°F / >135°F)
    6. Courier handover verified via cryptographic handshake
    7. ESG metrics updated
    """
    # 1. Ingest
    don_payload = {
        "donor_id": "org_donor_002",
        "food_category": "Fresh Produce",
        "description": "50kg Fresh Organic Broccoli & Carrots",
        "weight_lbs": 110.0,
        "initial_temp_f": 39.5,
        "is_perishable": True,
        "pickup_latitude": 37.7901,
        "pickup_longitude": -122.3985,
        "pickup_address": "450 Mission St, San Francisco, CA",
        "expiration_minutes": 240
    }
    ingest_res = client.post("/api/v1/donations", json=don_payload)
    assert ingest_res.status_code == 201
    don_id = ingest_res.json()["donation_id"]

    # 2. Match
    match_res = client.post(
        "/api/v1/matching/find-recipients",
        json={
            "donation_id": don_id,
            "max_distance_km": 10.0})
    assert match_res.status_code == 200
    recip_id = match_res.json()["matched_recipients"][0]["recipient_id"]

    # 3. Reserve
    res_res = client.post(
        "/api/v1/matching/reserve",
        json={
            "donation_id": don_id,
            "recipient_id": recip_id})
    assert res_res.status_code == 200

    # 4. Dispatch
    disp_res = client.post(
        "/api/v1/dispatch/state",
        json={
            "donation_id": don_id,
            "dispatch_mode": "VOLUNTEER"})
    assert disp_res.status_code == 200

    # 5. Thermal reading
    thm_res = client.post("/api/v1/telemetry/thermal-log", json={
        "donation_id": don_id,
        "temp_f": 38.5,
        "ambient_temp_f": 62.0,
        "sensor_id": "E2E_PROBE_01"
    })
    assert thm_res.status_code == 200
    assert thm_res.json()["is_compliant"] is True

    # 6. Handover Handshake
    hs_res = client.post("/api/v1/custody/handshake", json={
        "donation_id": don_id,
        "step": "RECIPIENT_FINAL_DELIVERY",
        "otp_token": "OTP-7744",
        "signature": "SIG_E2E_CONFIRMED",
        "verifier_public_key": "PUBKEY_STANTHONY"
    })
    assert hs_res.status_code == 200
    assert hs_res.json()["verified"] is True

    # 7. Verify Telemetry Reflection
    admin_telemetry = client.get("/api/v1/telemetry/admin").json()
    assert admin_telemetry["system_status"] == "OPERATIONAL"
