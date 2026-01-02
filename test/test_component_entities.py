import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.entities.base  import BaseGameSubState, BaseParentState, BaseGameEntity
from transitions import Machine 

class DummyGameStore:
    location: None = None
    state_vector = {}
    machine: Machine

def test_base_game_substate():
    try:
        # Arrange
        store = DummyGameStore()
        substate = BaseGameSubState(store=store, name='test')

        # Act
        substate.set_bits()
        actual_on_map_no_location = substate.is_on_map() # Expect False
        actual_not_on_map_no_location = substate.is_not_on_map() # Expect True
        substate.store.location = 'some_location' # type: ignore
        substate.set_bits()
        actual_on_map_w_location = substate.is_on_map() # Expect True
        actual_not_on_map_w_location = substate.is_not_on_map() # Expect False

        # Assert
        assert actual_on_map_no_location == False
        assert actual_not_on_map_no_location == True
        assert actual_on_map_w_location == True
        assert actual_not_on_map_w_location == False
        assert substate.store.state_vector == {'on_map': True} # type: ignore

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

    