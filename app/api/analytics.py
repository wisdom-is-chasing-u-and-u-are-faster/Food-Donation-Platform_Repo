from fastapi import APIRouter
from app.models.schemas import ESGAnalyticsResponse
from app.services.esg_service import calculate_esg_metrics

router = APIRouter(prefix="/analytics", tags=["Analytics & ESG"])


@router.get("/esg", response_model=ESGAnalyticsResponse)
def get_esg_analytics():
    """
    Returns aggregated ESG sustainability and greenhouse gas offset metrics.
    """
    return calculate_esg_metrics()
