import pytest
import tcod.event

from core_components.dispatchers.library import SystemDispatcher
from core_components.store import GameStore


def test_dispatcher_ev_gamestart():
    state = GameStore()
    dispatcher = SystemDispatcher()
    
    from core_components.events.library import GameStart
    event = GameStart(message='Game Started')
    
    actions = dispatcher.dispatch(event, state)
    
    try:
        assert len(actions) == 1
        assert actions[0].__class__.__name__ == "GameStartAction"
        assert actions[0].state == state

    except AssertionError:
        pytest.fail("SystemDispatcher did not handle GameStart event correctly")

def test_dispatcher_ev_gameover():
    state = GameStore()
    dispatcher = SystemDispatcher()
    
    from core_components.events.library import GameOver
    event = GameOver(message='Game Over')
    
    actions = dispatcher.dispatch(event, state)
    
    try:
        assert len(actions) == 1
        assert actions[0].__class__.__name__ == "GameOverAction"
        assert actions[0].state == state

    except AssertionError:
        pytest.fail("SystemDispatcher did not handle GameOver event correctly")

def test_dispatcher_ev_keydown():
    state = GameStore()
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

