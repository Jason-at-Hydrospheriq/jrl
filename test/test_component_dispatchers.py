import pytest
from sys import path

import tcod

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.dispatchers.base import BaseEventDispatcher
from core_components.dispatchers.library import SystemDispatcher, InputDispatcher
from core_components.entities.library import CombatEntity, MobileEntity, PlayerCharactor, TargetableEntity
from core_components.entities.factory import spawn, PLAYER
from core_components.actions.library import EntityMoveAction, GeneralAction
from core_components.tiles.base import TileCoordinate, TileTuple
from core_components.store import GameStore

def test_input_dispatcher_initialization():
    pass

    # Arrange & Act
    dispatcher = InputDispatcher()

    from_base = False
    
    while not from_base and dispatcher is not None:
        for cls in dispatcher.__class__.mro():
            from_base = "BaseEventDispatcher" in cls.__name__
            
            if from_base:
                break

    # Assert
    try:
        assert dispatcher is not None, "InputDispatcher failed to initialize."
        assert from_base, "InputDispatcher does inherits from BaseEventDispatcher Protocol."
        assert hasattr(dispatcher, "MOVEMENT_ACTION"), "InputDispatcher missing MOVEMENT_ACTION template."
        assert hasattr(dispatcher, "MOVEMENT_KEYS"), "InputDispatcher missing MOVEMENT_KEYS constant."
        assert hasattr(dispatcher, "_ev_keydown"), "InputDispatcher missing _ev_keydown method."
        assert hasattr(dispatcher, "get_destination"), "InputDispatcher missing get_destination method."
        assert hasattr(dispatcher, "create_state_action"), "InputDispatcher missing create_state_action method."
        assert hasattr(dispatcher, "create_action_on_target"), "InputDispatcher missing create_action_on_target method."
        assert hasattr(dispatcher, "NOACTION"), "InputDispatcher missing NOACTION constant."
        assert hasattr(dispatcher, "SYSTEMEXIT"), "InputDispatcher missing SYSTEMEXIT constant."
            
    except Exception as e:
        pytest.fail(str(e))

def test_input_dispatcher_create_move_action_on_target():
    # Arrange
    dispatcher = InputDispatcher()
    dummy_state = GameStore()
    dummy_entity = MobileEntity()  # Replace with an actual entity mock or instance
    dummy_destination = TileCoordinate(TileTuple(([5], [5])), TileTuple(([80], [50])))

    # Act
    action = dispatcher.create_action_on_target(action=dispatcher.MOVEMENT_ACTION, state=dummy_state, entity=dummy_entity, target=dummy_destination)

    # Assert
    try:
        assert action is not None, "create_movement_action returned None."
        assert hasattr(action, "entity"), "Movement action missing 'entity' attribute."
        assert hasattr(action, "destination"), "Movement action missing 'destination' attribute."
        assert action.entity == dummy_entity, "Movement action 'entity' attribute not set correctly."
        assert action.destination == dummy_destination, "Movement action 'destination' attribute not set correctly."
        assert hasattr(action, "state"), "Movement action missing 'state' attribute."
        assert action.state == dummy_state, "Movement action 'state' attribute not set correctly."
        
    except Exception as e:
        pytest.fail(str(e))

def test_input_dispatcher_create_target_action_on_target():
    # Arrange
    dispatcher = InputDispatcher()
    dummy_state = GameStore()
    dummy_entity = CombatEntity()  # Replace with an actual entity mock or instance
    dummy_target = TargetableEntity()  # Replace with an actual target mock or instance

    # Act
    action = dispatcher.create_action_on_target(action=dispatcher.TARGET_ACQUISITION_ACTION, state=dummy_state, entity=dummy_entity, target=dummy_target)

    # Assert
    try:
        assert action is not None, "create_target_action returned None."
        assert hasattr(action, "entity"), "Target action missing 'entity' attribute."
        assert hasattr(action, "target"), "Target action missing 'target' attribute."
        assert action.entity == dummy_entity, "Target action 'entity' attribute not set correctly."
        assert action.target == dummy_target, "Target action 'target' attribute not set correctly."
        assert hasattr(action, "state"), "Target action missing 'state' attribute."
        assert action.state == dummy_state, "Target action 'state' attribute not set correctly."
        
    except Exception as e:
        pytest.fail(str(e))
np.array()
def test_input_dispatcher_get_destination():
    # Arrange
    dispatcher = InputDispatcher()
    location_tuple = TileTuple(([10], [10]))
    location_coord = TileCoordinate(location_tuple, TileTuple(([80], [50])))
    dummy_entity = MobileEntity()
    dummy_entity.location = location_coord

    class DummyEvent:
        def __init__(self, sym):
            self.sym = sym

    event = DummyEvent(tcod.event.KeySym.UP)

    expected_x = dummy_entity.location.x + dispatcher.MOVEMENT_KEYS[event.sym][0]
    expected_y = dummy_entity.location.y + dispatcher.MOVEMENT_KEYS[event.sym][1]
    expected_destination_tuple = TileTuple(([expected_x], [expected_y]))
    expected_destination = TileCoordinate(expected_destination_tuple, dummy_entity.location.parent_map_size)

    # Act
    destination = dispatcher.get_destination(event, dummy_entity)

    # Assert
    try:
        assert destination is not None, "get_destination returned None."
        assert isinstance(destination, TileCoordinate), "get_destination did not return a TileCoordinate."
        assert destination.x == expected_destination.x, "get_destination returned incorrect x coordinate."
        assert destination.y == expected_destination.y, "get_destination returned incorrect y coordinate."
        
    except Exception as e:
        pytest.fail(str(e))

def test_input_dispatcher_ev_keydown_escape():
    # Arrange
    dispatcher = InputDispatcher()
    dummy_state = GameStore()
    event = tcod.event.KeyDown(sym=tcod.event.KeySym.ESCAPE, 
                                        scancode=0x01, 
                                        mod=0)  # Simulate ESCAPE key press

    # Act
    action = dispatcher._ev_keydown(event, dummy_state)
    from_base = False
    while not from_base and action is not None:
        for cls in action.__class__.mro():
            from_base = "GeneralAction" in cls.__name__
            
            if from_base:
                break

    # Assert
    try:
        assert action is not None, "_ev_keydown returned None for ESCAPE key."
        assert isinstance(action, GeneralAction), "Returned action is not of expected type."
        assert from_base, "Returned action is not a GeneralAction."
        
    except Exception as e:
        pytest.fail(str(e))

def test_input_dispatcher_ev_keydown_movement():
    # Arrange
    dispatcher = InputDispatcher()
    dummy_state = GameStore()
    location_tuple = TileTuple(([10], [10]))
    location_coord = TileCoordinate(location_tuple, TileTuple(([80], [50])))
    dummy_entity = dummy_state.roster.spawn(PLAYER, location_coord)
    dummy_state.roster.player = dummy_entity  # The player entity
    
    event = tcod.event.KeyDown(sym=tcod.event.KeySym.UP, 
                                        scancode=0x48, 
                                        mod=0)  # Simulate UP key press

    expected_destination = dispatcher.get_destination(event, dummy_entity)
    
    # Act
    action = dispatcher._ev_keydown(event, dummy_state)

    # Assert
    try:
        assert action is not None, "_ev_keydown returned None for movement key."
        assert hasattr(action, "entity"), "Movement action missing 'entity' attribute."
        assert hasattr(action, "destination"), "Movement action missing 'destination' attribute."
        assert isinstance(action, EntityMoveAction), "Returned action is not of expected type."
        assert action.entity == dummy_entity, "Movement action 'entity' attribute not set correctly."
        assert action.destination == expected_destination, "Movement action 'destination' attribute not set correctly."
        
    except Exception as e:
        pytest.fail(str(e))