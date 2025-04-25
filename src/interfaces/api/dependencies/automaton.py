from fastapi import Request
import ahocorasick


async def get_automaton(request: Request) -> ahocorasick.Automaton:
    return request.app.state.automaton