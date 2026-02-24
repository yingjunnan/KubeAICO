from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_ai_service, get_current_user
from app.db.session import get_db
from app.schemas.ai import AIAnalyzeRequest, AIAnalyzeTaskRead, AIAnalyzeTaskResponse, AIAnalyzeResult

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze", response_model=AIAnalyzeTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze(
    payload: AIAnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_ai_service),
) -> AIAnalyzeTaskResponse:
    task_id = await service.create_task(db=db, payload=payload)
    background_tasks.add_task(service.process_task, task_id)
    return AIAnalyzeTaskResponse(task_id=task_id, status="pending")


@router.get("/tasks/{task_id}", response_model=AIAnalyzeTaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    service=Depends(get_ai_service),
) -> AIAnalyzeTaskRead:
    task = await service.get_task(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    result = None
    if task.result_payload:
        result = AIAnalyzeResult.model_validate(task.result_payload)

    return AIAnalyzeTaskRead(
        task_id=task.id,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        result=result,
        error=task.error,
    )
