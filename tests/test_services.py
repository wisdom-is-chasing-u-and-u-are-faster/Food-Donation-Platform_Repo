import pytest
from app.services.matching_service import haversine_distance_km, find_matched_recipients, reserve_donation
from app.services.haccp_service import evaluate_haccp_temperature, calculate_safe_transit_window
from app.services.dispatch_service import initiate_or_transition_dispatch, get_dispatch_status
from app.services.custody_service import verify_and_append_handshake, get_custody_trail
from app.services.esg_service import calculate_esg_metrics


def test_haversine_distance():
    # San Francisco Market St to Ellis St (~0.8 - 1.2 km)
    dist = haversine_distance_km(37.7935, -122.3965, 37.7852, -122.4116)
    assert 0.5 <= dist <= 2.5, f"Expected distance ~1.5km, got {dist}"


def test_haccp_evaluation_rules():
    # Cold compliant
    comp, status, _ = evaluate_haccp_temperature(38.0, is_perishable=True)
    assert comp is True
    assert status == "COMPLIANT"

    # Hot compliant
    comp, status, _ = evaluate_haccp_temperature(140.0, is_perishable=True)
    assert comp is True
    assert status == "COMPLIANT"

    # Danger zone violation (e.g. 75°F)
    comp, status, msg = evaluate_haccp_temperature(75.0, is_perishable=True)
    assert comp is False
    assert status == "VIOLATION"


def test_safe_transit_window():
    remaining = calculate_safe_transit_window(
        "2026-10-26 12:00:00", max_window_minutes=120.0)
    assert isinstance(remaining, float)
    assert remaining >= 0.0


def test_matching_service():
    res = find_matched_recipients("don_1001", max_distance_km=15.0)
    assert res["donation_id"] == "don_1001"
    assert len(res["matched_recipients"]) >= 1
    assert res["match_latency_ms"] < 30000.0  # Sub-30s P99 latency


def test_dispatch_state_and_3pl_failover():
    # Volunteer dispatch
    d_vol = initiate_or_transition_dispatch(
        "don_1003", dispatch_mode="VOLUNTEER")
    assert d_vol["fleet_type"] == "VOLUNTEER"
    assert d_vol["status"] == "ACCEPTED"

    # 3PL failover
    d_3pl = initiate_or_transition_dispatch(
        "don_1003", dispatch_mode="3PL_DOORDASH", force_3pl=True)
    assert d_3pl["fleet_type"] == "3PL_DOORDASH"
    assert "DoorDash" in d_3pl["provider"]


def test_custody_ledger_and_verification():
    trail_before = get_custody_trail("don_1001")
    assert trail_before["chain_valid"] is True
    initial_blocks = trail_before["blocks_count"]

    res = verify_and_append_handshake(
        "don_1001",
        "RECIPIENT_FINAL_DELIVERY",
        "OTP-9988",
        "SIG_TEST_01",
        "KEY_RECIP")
    assert res["verified"] is True
    assert len(res["ledger_hash"]) == 64  # SHA-256 length

    trail_after = get_custody_trail("don_1001")
    assert trail_after["chain_valid"] is True
    assert trail_after["blocks_count"] == initial_blocks + 1


def test_esg_calculations():
    esg = calculate_esg_metrics()
    assert esg["total_rescued_lbs"] > 0
    assert esg["co2_emissions_avoided_kg"] > 0
    assert esg["meals_served"] > 0
