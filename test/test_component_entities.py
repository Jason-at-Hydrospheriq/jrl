import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np
from transitions import Machine 

from core_components.entities.base  import BaseGameSubState, BaseGameEntity, BaseParentState
from core_components.entities.library import *
from core_components.entities.types import GameEntity, EntityParentState
from core_components.maps.tiles.base import TileCoordinate
from core_components.store import GameStore

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

def test_base_game_entity():
    try:
        # Arrange
        store = GameStore()

        # Act 
        entity = BaseGameEntity(store=store, name='test_entity')
        entity.machine = Machine()

        # Assert
        assert isinstance(entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert isinstance(entity, BaseParentState), "Expected entity be an instance of BaseParentState"
        assert isinstance(entity, GameEntity), "Expected entity to duck type to GameEntity"
        assert isinstance(entity, EntityParentState), "Expected entity to duck type to EntityParentState"

        assert entity.name == 'test_entity'
        assert entity.state_vector == {'on_map': False}
        assert len(entity._substates_manifest) == 1
        assert isinstance(entity.substates[0], BaseGameSubState)
        assert entity.location == None
        assert entity.blocks_movement == True
        assert entity.spawn.is_not_in_play() == True # type: ignore

        entity.location = TileCoordinate.from_tuple((0,0))
        entity.update()

        assert entity.state_vector == {'on_map': True}
        assert isinstance(entity.location, TileCoordinate)
        assert entity.spawn.is_in_play() == True # type: ignore 


    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

# def test_