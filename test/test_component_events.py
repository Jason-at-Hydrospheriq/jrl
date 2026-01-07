import pytest
from sys import path

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from store_components.atlas import Atlas
from store_components import Portfolio
from atlas_components.tiles.base import TileCoordinate
from entities.base import BaseGameEntity
from entities.library import AICharacter, Character, PlayerCharacter
from game_types import StatefulObject, StoredStateObject
from game_types import GameLoopObject, StateActionObject, StateHandler, EventTransformer
from ai_components.base import BaseGameEvent
from engine_components.ai import LoopHandler
from ai_components.library import SystemEvent, InputEvent, EntityEvent, PlayerCharacterEvent, AICharacterEvent, NoAction, KeyDownAction
from engine_components.store import GameStore
from tcod.event import Event
import tcod

def test_component_base_game_event():
    try:
        # Arrange
        store = GameStore()
        handler = LoopHandler()
        event = BaseGameEvent(store=store, handler=handler)

        # Act
        with pytest.raises(NotImplementedError, match="Subclasses must implement the trigger method."):
            event.trigger()

        # Assert
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_system_event():
    try:
        # Arrange        
        store = GameStore()
        behaviors = set((('systemevent', NoAction()),))
        handler = LoopHandler(behaviors=behaviors)
        event = SystemEvent(store=store, handler=handler)
        handler.start()  # type: ignore
        
        # Act
        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize() 
        event.trigger()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()

        # Assert
        assert isinstance(event, SystemEvent), "Expected event to be instance of SystemEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"

        assert isinstance(handler.actions.get_nowait(), NoAction), "Expected action in handler's action queue to be instance of NoAction"
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_input_event():
    try:
        # Arrange        
        store = GameStore()
        behaviors = set((('inputevent', KeyDownAction()),))
        handler = LoopHandler(behaviors=behaviors)
        event = InputEvent(store=store, handler=handler)

        handler.start()  # type: ignore

        # Act
        with pytest.raises(TypeError):
            event.input_event = BaseGameEvent()  # type: ignore
        event.input_event = Event()
        input_event = event.input_event

        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize() 
        event.trigger()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()

        # Assert
        assert isinstance(event, InputEvent), "Expected event to be instance of InputEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(input_event, Event), "Expected input_event to be instance of tcod.event.Event"

        assert isinstance(handler.actions.get_nowait(), KeyDownAction), "Expected action in handler's action queue to be instance of KeyDownAction"
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_entity_event():
    try:
        # Arrange        
        store = GameStore()
        behaviors = set((('entityevent', NoAction()),))
        handler = LoopHandler(behaviors=behaviors)
        event = EntityEvent(store=store, handler=handler)
        
        handler.start()  # type: ignore

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = BaseGameEntity()
        entity = event.entity
        
        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize() 
        event.trigger()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()

        # Assert
        assert isinstance(event, EntityEvent), "Expected event to be instance of EntityEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"   
        
        assert isinstance(handler.actions.get_nowait(), NoAction), "Expected action in handler's action queue to be instance of NoAction"
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_player_character_event():
    try:
        # Arrange        
        store = GameStore()
        behaviors = set((('playercharacterevent', NoAction()),))
        handler = LoopHandler(behaviors=behaviors)
        event = PlayerCharacterEvent(store=store, handler=handler)
        handler.start()  # type: ignore

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = PlayerCharacter()
        entity = event.entity

        with pytest.raises(TypeError):
            event.target = BaseGameEvent()  # type: ignore
        event.target = PlayerCharacter()
        target = event.target
        
        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize()
        event.trigger()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()

        # Assert
        assert isinstance(event, PlayerCharacterEvent), "Expected event to be instance of PlayerCharacterEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, Character), "Expected entity to be instance of BaseGameEntity"   
        assert isinstance(target, Character), "Expected target to be instance of BaseGameEntity"   

        assert isinstance(handler.actions.get_nowait(), NoAction), "Expected action in handler's action queue to be instance of NoAction"
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_ai_character_event():
    try:
        # Arrange        
        store = GameStore()
        behaviors = set((('aicharacterevent', NoAction()),))
        handler = LoopHandler(behaviors=behaviors)
        event = AICharacterEvent(store=store, handler=handler)
        handler.start()  # type: ignore

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = AICharacter()
        entity = event.entity
        
        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize()
        event.trigger()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()

        # Assert
        assert isinstance(event, AICharacterEvent), "Expected event to be instance of AICharacterEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, Character), "Expected entity to be instance of Character"   

        assert isinstance(handler.actions.get_nowait(), NoAction), "Expected action in handler's action queue to be instance of NoAction"
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

