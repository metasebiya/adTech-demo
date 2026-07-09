from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.copilot_service import CopilotService
from core.permissions.dependencies import require_permissions
from core.schemas.copilot import CopilotQueryRequest, CopilotQueryResponse, CopilotSuggestedQuestion
from infra.db.session import get_db_session

router = APIRouter()


@router.get("/suggested-questions", response_model=list[CopilotSuggestedQuestion])
def get_suggested_questions(
    _: Annotated[User, Depends(require_permissions("use_copilot"))],
    session: Session = Depends(get_db_session),
) -> list[CopilotSuggestedQuestion]:
    return CopilotService(session).get_suggested_questions()


@router.post("/query", response_model=CopilotQueryResponse)
def query_copilot(
    payload: CopilotQueryRequest,
    _: Annotated[User, Depends(require_permissions("use_copilot"))],
    session: Session = Depends(get_db_session),
) -> CopilotQueryResponse:
    return CopilotService(session).answer_query(payload.query)
