import pytest
import numpy as np
import sys
import tcod.event

# Ensure the src directory is on sys.path so src can be imported
SRC_DIR = r'C:\Users\jason\workspaces\repos\jrl' or ".."

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.components.actions.dispatchers import SystemDispatcher
from src.state import GameState


def test_dispatcher_ev_gamestart():
    state = GameState()
    dispatcher = SystemDispatcher()
    
    from src.components.events.library import GameStart
    event = GameStart(message='Game Started')
    
    actions = dispatcher.dispatch(event, state)
    
    try:
        assert len(actions) == 1
        assert actions[0].__class__.__name__ == "GameStartAction"
        assert actions[0].state == state

    except AssertionError:
        pytest.fail("SystemDispatcher did not handle GameStart event correctly")

def test_dispatcher_ev_gameover():
    state = GameState()
    dispatcher = SystemDispatcher()
    
    from src.components.events.library import GameOver
    event = GameOver(message='Game Over')
    
    actions = dispatcher.dispatch(event, state)
    
    try:
        assert len(actions) == 1
        assert actions[0].__class__.__name__ == "GameOverAction"
        assert actions[0].state == state

    except AssertionError:
        pytest.fail("SystemDispatcher did not handle GameOver event correctly")

def test_dispatcher_ev_keydown():
    state = GameState()
    dispatcher = SystemDispatcher()

    event = tcod.event.KeyDown(
        scancode=tcod.event.Scancode.ESCAPE,
        sym=tcod.event.KeySym.ESCAPE,
        mod=tcod.event.Modifier.NONE
    )
    
    actions = dispatcher.dispatch(event, state)
    
    try:
        assert len(actions) == 2  # NoAction + SystemExitAction
        assert actions[0].__class__.__name__ == "NoAction"
        assert actions[1].__class__.__name__ == "SystemExitAction"
        assert actions[0].state == state
        assert actions[1].state == state

    except AssertionError:
        pytest.fail("SystemDispatcher did not handle KeyDown event correctly")

