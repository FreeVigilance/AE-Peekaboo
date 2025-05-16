import ahocorasick
from fastapi import Request


async def get_automaton(request: Request) -> ahocorasick.Automaton:
    return request.app.state.automaton
