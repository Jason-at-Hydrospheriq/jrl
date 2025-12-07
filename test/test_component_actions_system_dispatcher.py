import pytest
import numpy as np
import sys

# Ensure the src directory is on sys.path so src can be imported
SRC_DIR = r'C:\Users\jason\workspaces\repos\jrl' or ".."

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.components.actions.dispatchers import SystemDispatcher
from src.state import GameState


def test_system_dispatcher_ev_methods():
    # Arrange
    dispatcher = SystemDispatcher()
    dummy_state = GameState()  # Assuming GameState can be instantiated without parameters

    # Act & Assert
    try:
        quit_event = tcod.event.Quit()
        actions = dispatcher._ev_quit(quit_event, dummy_state)
        assert isinstance(actions, list), "_ev_quit should return a list of actions."
        assert all(hasattr(action, 'state') for action in actions), "All actions should have a 'state' attribute."
    

