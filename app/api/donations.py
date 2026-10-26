from fastapi import APIRouter, HTTPException, Query, status
import time
from typing import Optional, List, Dict, Any
from app.db.session import query_db, execute_db, generate_unique_id
from app.models.schemas import DonationCreate, DonationResponse, DonationDetail
from app.services.haccp_service import evaluate_haccp_temperature

router = APIRouter(prefix="/donations", tags=["Donations"])


@router.post("", response_model=DonationResponse,
             status_code=status.HTTP_201_CREATED)
def create_donation(payload: DonationCreate):
    """
    Ingests surplus food donation listing with initial HACCP thermal parameters.
    """
    is_compliant, haccp_status, _ = evaluate_haccp_temperature(
        payload.initial_temp_f, payload.is_perishable)

    donation_id = generate_unique_id("don")
    qr_secret = generate_unique_id("sec_ecdsa")
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    execute_db(
        """INSERT INTO donations (donation_id, donor_id, food_category, description, weight_lbs, initial_temp_f, is_perishable, pickup_latitude, pickup_longitude, pickup_address, status, haccp_status, expiration_minutes, qr_handshake_secret, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'AVAILABLE', ?, ?, ?, ?)""",
        (donation_id,
         payload.donor_id,
         payload.food_category,
         payload.description,
         payload.weight_lbs,
         payload.initial_temp_f,
         payload.is_perishable,
         payload.pickup_latitude,
         payload.pickup_longitude,
         payload.pickup_address,
         haccp_status,
         payload.expiration_minutes,
         qr_secret,
         created_at)
    )

    return {
        "donation_id": donation_id,
        "status": "AVAILABLE",
        "haccp_status": haccp_status,
        "created_at": created_at,
        "qr_handshake_payload": f"DONATION:{donation_id}|SECRET:{qr_secret}"
    }


@router.get("", response_model=Dict[str, Any])
def list_donations(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_filter: Optional[str] = Query(None, alias="category")
):
    """
    Lists all surplus donations with optional status or category filtering.
    """
    query = "SELECT * FROM donations WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter.upper())
    if category_filter:
        query += " AND food_category = ?"
        params.append(category_filter)

    query += " ORDER BY created_at DESC"
    results = query_db(query, tuple(params))

    return {
        "total": len(results),
        "donations": [dict(r) for r in results]
    }


@router.get("/{donation_id}", response_model=DonationDetail)
def get_donation(donation_id: str):
    """
    Fetches details for a single donation.
    """
    don = query_db(
        "SELECT * FROM donations WHERE donation_id = ?",
        (donation_id,
         ),
        one=True)
    if not don:
        raise HTTPException(status_code=404,
                            detail=f"Donation {donation_id} not found.")
    return dict(don)
