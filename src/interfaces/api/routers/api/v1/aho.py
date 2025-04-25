from fastapi import APIRouter, Depends
from fastapi import Request
from starlette.responses import JSONResponse

from src.application.services.aho import AhoCorasickService

router = APIRouter()


@router.post('/aho/rebuild')
async def aho_rebuild(
  request: Request,
  service: AhoCorasickService = Depends(),
):

    # TODO: REBUILD IN OTHER PROCESS
    new_automation = await service.build_aho_corasick()
    # request.app.state.automaton = new_automation
    return JSONResponse(status_code=200, content={'status': 'success'})