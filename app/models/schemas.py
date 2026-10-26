from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    service: str = "food-donation-platform"
    version: str = "1.0.0"
    timestamp: str


class DonationCreate(BaseModel):
    donor_id: str
    food_category: str
    description: str
    weight_lbs: float
    initial_temp_f: float
    is_perishable: bool = True
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: str
    expiration_minutes: int = 180


class DonationResponse(BaseModel):
    donation_id: str
    status: str
    haccp_status: str
    created_at: str
    qr_handshake_payload: str


class DonationDetail(BaseModel):
    donation_id: str
    donor_id: str
    food_category: str
    description: str
    weight_lbs: float
    initial_temp_f: float
    is_perishable: bool
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: str
    status: str
    haccp_status: str
    expiration_minutes: int
    created_at: str


class MatchRequest(BaseModel):
    donation_id: str
    max_distance_km: float = 15.0


class MatchRecipientResult(BaseModel):
    recipient_id: str
    name: str
    address: str
    distance_km: float
    capacity_remaining_lbs: float
    match_score: float


class MatchResponse(BaseModel):
    donation_id: str
    matched_recipients: List[MatchRecipientResult]
    match_latency_ms: float


class ReservationRequest(BaseModel):
    donation_id: str
    recipient_id: str


class ReservationResponse(BaseModel):
    reservation_id: str
    donation_id: str
    recipient_id: str
    status: str
    reserved_at: str


class DispatchRequest(BaseModel):
    donation_id: str
    dispatch_mode: str = "VOLUNTEER"
    force_3pl: bool = False


class DispatchResponse(BaseModel):
    dispatch_id: str
    donation_id: str
    fleet_type: str
    provider: str
    status: str
    ttl_remaining_seconds: int
    tracking_url: str


class HandshakeRequest(BaseModel):
    donation_id: str
    step: str
    otp_token: str
    signature: str
    verifier_public_key: str


class HandshakeResponse(BaseModel):
    verified: bool
    ledger_hash: str
    handover_timestamp: str


class CustodyLedgerResponse(BaseModel):
    donation_id: str
    chain_valid: bool
    blocks_count: int
    ledger_trail: List[Dict[str, Any]]


class ThermalLogRequest(BaseModel):
    donation_id: str
    temp_f: float
    ambient_temp_f: float
    sensor_id: str


class ThermalLogResponse(BaseModel):
    donation_id: str
    temp_f: float
    is_compliant: bool
    haccp_status: str
    safe_transit_window_remaining_minutes: float
    warning: Optional[str] = None


class AdminTelemetryResponse(BaseModel):
    active_donations: int
    match_latency_p99_seconds: float
    claim_fulfillment_rate_percent: float
    safe_transit_compliance_percent: float
    total_pounds_rescued: float
    co2_offset_kg: float
    active_3pl_failovers: int
    haccp_violations_count: int
    system_status: str
    recent_dispatches: List[Dict[str, Any]]


class DonorTelemetryResponse(BaseModel):
    donor_id: str
    donor_name: str
    total_donations_count: int
    pounds_donated_month: float
    meals_provided: int
    active_listings: List[Dict[str, Any]]
    esg_carbon_saved_kg: float


class RecipientTelemetryResponse(BaseModel):
    recipient_id: str
    organization_name: str
    storage_capacity_used_percent: float
    meals_distributed: int
    incoming_deliveries: List[Dict[str, Any]]
    safe_window_timer_seconds: int


class ESGAnalyticsResponse(BaseModel):
    total_rescued_lbs: float
    co2_emissions_avoided_kg: float
    water_saved_gallons: float
    equivalent_vehicles_off_road_days: float
    meals_served: int
    historical_monthly_data: List[Dict[str, Any]]
