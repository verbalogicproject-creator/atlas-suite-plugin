from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI(title="Frozen task contract")
bearer = HTTPBearer(auto_error=False)


class Task(BaseModel):
    id: int
    title: str


async def require_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    if credentials is None or credentials.credentials != "fixture-token":
        raise HTTPException(status_code=401, detail="unauthorized")
    return credentials.credentials


@app.get("/api/tasks", response_model=list[Task], responses={401: {"description": "unauthorized"}})
async def list_tasks(_token: str = Depends(require_token)) -> list[Task]:
    return [Task(id=1, title="Write qualification")]
