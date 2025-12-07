import pytest
import numpy as np
import sys


# Ensure the src directory is on sys.path so dataset can be imported
SRC_DIR = r'C:\Users\jason\workspaces\repos\jrl' or ".."

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.components.ai import GameAI
from src.components.queues.event_lib import GameOver
from src.components.state import GameState

def test_game_over_event_handling():
    state = GameState()
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
    state = GameState()
    game_ai = GameAI(state)
    
    try:
        assert game_ai.state == state
        assert isinstance(game_ai, GameAI)

    except AssertionError:
        pytest.fail("GameAI did not initialize correctly with GameState")

def test_game_ai_no_events():
    state = GameState()
    game_ai = GameAI(state)
    
    actions = game_ai.get_actions()
    
    try:
        assert isinstance(actions, list)
        assert len(actions) == 0  # No events should result in no actions

    except AssertionError:
        pytest.fail("GameAI returned actions when there were no events")    

def test_game_ai_multiple_events():
    state = GameState()
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
    state = GameState()
    game_ai = GameAI(state)
    
    game_ai.state.game_events.post(GameOver(message='Game Over'))
    
    actions_first_call = game_ai.get_actions()
    actions_second_call = game_ai.get_actions()
    
    try:
        assert len(actions_first_call) == 1
        assert len(actions_second_call) == 0  # Events should be cleared after first call

    except AssertionError:
        pytest.fail("GameAI did not clear events after processing")

