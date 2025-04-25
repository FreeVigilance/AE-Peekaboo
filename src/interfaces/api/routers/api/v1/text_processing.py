from ahocorasick import Automaton
from fastapi import APIRouter, Depends

from src.infrastructure.schemas.text_processing import TextRequest
from src.application.services.text_processing import TextProcessingService
from src.interfaces.api.dependencies.automaton import get_automaton

router = APIRouter()


@router.post("/find_medications/")
async def find_medications(
    request: TextRequest,
    service: TextProcessingService = Depends(),
    automaton: Automaton = Depends(get_automaton),
):
    highlighted_text = await service.highlight_medications_in_text(automaton, request.text)
    # highlighted_text = await service.highlight_medications_in_text(request.text)
    return {"highlighted_text": highlighted_text}
