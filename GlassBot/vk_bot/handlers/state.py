"""Состояния диалога по peer_id"""

_states: dict = {}


def set_state(peer_id: int, mode: str, **data):
    _states[peer_id] = {"mode": mode, **data}

def get_state(peer_id: int):
    return _states.get(peer_id)

def reset_state(peer_id: int):
    _states.pop(peer_id, None)

def in_mode(peer_id: int, *modes: str) -> bool:
    s = _states.get(peer_id)
    return s is not None and s["mode"] in modes
