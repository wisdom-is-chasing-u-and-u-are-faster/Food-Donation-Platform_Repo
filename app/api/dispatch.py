from fastapi import APIRouter, HTTPException
from app.models.schemas import DispatchRequest, DispatchResponse
from app.services.dispatch_service import initiate_or_transition_dispatch, get_dispatch_status

router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


@router.post("/state", response_model=DispatchResponse)
def handle_dispatch(payload: DispatchRequest):
    """
    Transitions dispatch state to Volunteer fleet or triggers 3PL failover (DoorDash/Uber Direct).
    """
    try:
        return initiate_or_transition_dispatch(
            payload.donation_id,
            payload.dispatch_mode,
            payload.force_3pl
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{dispatch_id}")
def get_status(dispatch_id: str):
    """
    Retrieves dispatch tracking details and courier status.
    """
    try:
        return get_dispatch_status(dispatch_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
