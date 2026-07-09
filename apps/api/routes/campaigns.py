from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.campaign_service import CampaignService
from core.permissions.dependencies import require_permissions
from core.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from infra.db.session import get_db_session

router = APIRouter()


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    current_user: Annotated[User, Depends(require_permissions("manage_campaigns"))],
    session: Session = Depends(get_db_session),
) -> list[CampaignRead]:
    del current_user
    service = CampaignService(session)
    return [CampaignRead.model_validate(campaign) for campaign in service.list_campaigns()]


@router.post("", response_model=CampaignRead, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    current_user: Annotated[User, Depends(require_permissions("manage_campaigns"))],
    session: Session = Depends(get_db_session),
) -> CampaignRead:
    service = CampaignService(session)
    campaign = service.create_campaign(payload, current_user)
    return CampaignRead.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(
    campaign_id: int,
    current_user: Annotated[User, Depends(require_permissions("manage_campaigns"))],
    session: Session = Depends(get_db_session),
) -> CampaignRead:
    del current_user
    service = CampaignService(session)
    return CampaignRead.model_validate(service.get_campaign(campaign_id))


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    current_user: Annotated[User, Depends(require_permissions("manage_campaigns"))],
    session: Session = Depends(get_db_session),
) -> CampaignRead:
    del current_user
    service = CampaignService(session)
    campaign = service.update_campaign(campaign_id, payload)
    return CampaignRead.model_validate(campaign)
