from fastapi import APIRouter, HTTPException
from app.models.schemas import MatchRequest, MatchResponse, ReservationRequest, ReservationResponse
from app.services.matching_service import find_matched_recipients, reserve_donation

router = APIRouter(prefix="/matching", tags=["Matching"])


@router.post("/find-recipients", response_model=MatchResponse)
def match_recipients(payload: MatchRequest):
    """
    Executes PostGIS proximity spatial matching and capacity ranking for a donation.
    """
    try:
        return find_matched_recipients(
            payload.donation_id, payload.max_distance_km)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reserve", response_model=ReservationResponse)
def reserve(payload: ReservationRequest):
    """
    Reserves a donation for a recipient organization.
    """
    try:
        return reserve_donation(payload.donation_id, payload.recipient_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
