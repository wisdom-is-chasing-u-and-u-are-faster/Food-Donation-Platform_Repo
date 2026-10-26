from fastapi import APIRouter, HTTPException
from app.models.schemas import HandshakeRequest, HandshakeResponse, CustodyLedgerResponse
from app.services.custody_service import verify_and_append_handshake, get_custody_trail

router = APIRouter(prefix="/custody", tags=["Custody & Verification"])


@router.post("/handshake", response_model=HandshakeResponse)
def perform_handshake(payload: HandshakeRequest):
    """
    Verifies ECDSA / OTP handshake and appends verified block to chain-of-custody ledger.
    """
    return verify_and_append_handshake(
        payload.donation_id,
        payload.step,
        payload.otp_token,
        payload.signature,
        payload.verifier_public_key
    )


@router.get("/ledger/{donation_id}", response_model=CustodyLedgerResponse)
def get_ledger(donation_id: str):
    """
    Retrieves full cryptographic audit trail for a donation.
    """
    return get_custody_trail(donation_id)
