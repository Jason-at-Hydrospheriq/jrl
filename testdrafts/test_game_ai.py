import pytest

from ai import GameAI
from components.events.library import GameOver
from core_components.store import GameStore

def test_game_over_event_handling():
    state = GameStore()
    state.game_over = False
    
    game_ai = GameAI(state)
    game_ai.state.game_events.post(GameOver(message='Game Over'))
    
    actions = game_ai.get_actions()
    
    try:
        assert len(actions) == 1
        assert actions[0].__class__.__name__ == "GameOverAction"
        assert state.game_over == False  # Ensure game_over flag is not altered by action retrieval

    except AssertionError:
        pytest.fail("GameOver event was not handled correctly by GameAI")

def test_game_ai_initialization():
    state = GameStore()
    game_ai = GameAI(state)
    
    try:
        assert game_ai.state == state
        assert isinstance(game_ai, GameAI)

    except AssertionError:
        pytest.fail("GameAI did not initialize correctly with GameState")

def test_game_ai_no_events():
    state = GameStore()
    game_ai = GameAI(state)
    
    actions = game_ai.get_actions()
    
    try:
        assert isinstance(actions, list)
        assert len(actions) == 0  # No events should result in no actions

    except AssertionError:
        pytest.fail("GameAI returned actions when there were no events")    

def test_game_ai_multiple_events():
    state = GameStore()
    game_ai = GameAI(state)
    
    # Post multiple GameOver events
    for _ in range(3):
        game_ai.state.game_events.post(GameOver(message='Game Over'))
    
    actions = game_ai.get_actions()
    
    try:
        assert len(actions) == 3
        for action in actions:
            assert action.__class__.__name__ == "GameOverAction"

    except AssertionError:
        pytest.fail("GameAI did not handle multiple GameOver events correctly")

def test_game_ai_event_clearing():
    state = GameStore()
    game_ai = GameAI(state)
    
    game_ai.state.game_events.post(GameOver(message='Game Over'))
    
    actions_first_call = game_ai.get_actions()
    actions_second_call = game_ai.get_actions()
    
    try:
        assert len(actions_first_call) == 1
        assert len(actions_second_call) == 0  # Events should be cleared after first call

    except AssertionError:
        pytest.fail("GameAI did not clear events after processing")

