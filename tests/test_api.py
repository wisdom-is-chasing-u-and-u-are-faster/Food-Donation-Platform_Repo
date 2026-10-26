import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "food-donation-platform"


def test_admin_telemetry_endpoint():
    res = client.get("/api/v1/telemetry/admin")
    assert res.status_code == 200
    data = res.json()
    assert "active_donations" in data
    assert "match_latency_p99_seconds" in data
    assert data["system_status"] == "OPERATIONAL"


def test_donor_telemetry_endpoint():
    res = client.get("/api/v1/telemetry/donor?donor_id=org_donor_001")
    assert res.status_code == 200
    data = res.json()
    assert data["donor_id"] == "org_donor_001"
    assert "active_listings" in data


def test_recipient_telemetry_endpoint():
    res = client.get("/api/v1/telemetry/recipient?recipient_id=org_recip_001")
    assert res.status_code == 200
    data = res.json()
    assert data["recipient_id"] == "org_recip_001"
    assert "storage_capacity_used_percent" in data


def test_donations_crud_endpoints():
    # Ingest surplus donation
    new_don = {
        "donor_id": "org_donor_001",
        "food_category": "Prepared Meals",
        "description": "25 Trays Warm Pasta & Salad",
        "weight_lbs": 95.0,
        "initial_temp_f": 140.0,
        "is_perishable": True,
        "pickup_latitude": 37.7935,
        "pickup_longitude": -122.3965,
        "pickup_address": "101 Market St, San Francisco, CA",
        "expiration_minutes": 180
    }
    create_res = client.post("/api/v1/donations", json=new_don)
    assert create_res.status_code == 201
    created = create_res.json()
    assert "donation_id" in created
    assert created["haccp_status"] == "COMPLIANT"

    # List donations
    list_res = client.get("/api/v1/donations")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Single donation
    get_res = client.get(f"/api/v1/donations/{created['donation_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["donation_id"] == created["donation_id"]


def test_matching_and_reservation_endpoints():
    match_res = client.post(
        "/api/v1/matching/find-recipients",
        json={
            "donation_id": "don_1001",
            "max_distance_km": 20.0})
    assert match_res.status_code == 200
    matched = match_res.json()
    assert len(matched["matched_recipients"]) >= 1

    res_res = client.post(
        "/api/v1/matching/reserve",
        json={
            "donation_id": "don_1002",
            "recipient_id": "org_recip_002"})
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESERVED"


def test_dispatch_and_failover_endpoint():
    res = client.post(
        "/api/v1/dispatch/state",
        json={
            "donation_id": "don_1001",
            "dispatch_mode": "3PL_UBER",
            "force_3pl": True})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACCEPTED"
    assert "3PL" in data["fleet_type"]


def test_custody_and_handshake_endpoints():
    hs_res = client.post("/api/v1/custody/handshake", json={
        "donation_id": "don_1002",
        "step": "VOLUNTEER_PICKUP_VERIFIED",
        "otp_token": "OTP-1122",
        "signature": "SIG_TEST_ECDSA",
        "verifier_public_key": "PUBKEY_VOLUNTEER_01"
    })
    assert hs_res.status_code == 200
    assert hs_res.json()["verified"] is True

    ledger_res = client.get("/api/v1/custody/ledger/don_1002")
    assert ledger_res.status_code == 200
    assert ledger_res.json()["chain_valid"] is True


def test_thermal_log_endpoint():
    res = client.post("/api/v1/telemetry/thermal-log", json={
        "donation_id": "don_1001",
        "temp_f": 139.0,
        "ambient_temp_f": 68.0,
        "sensor_id": "IOT_PROBE_API_TEST"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["is_compliant"] is True
    assert data["haccp_status"] == "COMPLIANT"


def test_esg_analytics_endpoint():
    res = client.get("/api/v1/analytics/esg")
    assert res.status_code == 200
    data = res.json()
    assert data["total_rescued_lbs"] > 0
    assert data["co2_emissions_avoided_kg"] > 0
