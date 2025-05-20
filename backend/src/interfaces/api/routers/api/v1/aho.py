import asyncio
import pickle

from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from src.application.services.aho import AhoCorasickService
from src.interfaces.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/aho/rebuild")
async def aho_rebuild(
    request: Request,
    service: AhoCorasickService = Depends(),
    # _=Depends(get_current_user),
):

    new_automation = await asyncio.to_thread(service.build_aho_corasick)
    new_automation = await new_automation
    new_automation.save("./assets/aho_corasick_medications3.model", pickle.dumps)
    request.app.state.automaton = new_automation
    return JSONResponse(status_code=200, content={"status": "success"})
