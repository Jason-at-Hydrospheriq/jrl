import pytest
from sys import path

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.entities.base import BaseGameEntity
from core_components.entities.library import AICharacter, Character, PlayerCharacter
from protocols import StatefulObject, StoredStateObject
from core_components.loops.custom_types import GameLoopObject, StateActionObject, StateHandler, EventTransformer
from core_components.loops.base import BaseGameEvent, BaseGameHandler
from core_components.loops.handlers import GameLoopHandler, MobLoopHandler
from core_components.loops.events import SystemEvent, InputEvent, EntityEvent, PlayerCharacterEvent, AICharacterEvent
from core_components.store import GameStore
from tcod.event import Event

def test_component_base_game_event():
    try:
        # Arrange
        store = GameStore()
        handler = BaseGameHandler()
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
        handler = GameLoopHandler()
        event = SystemEvent(store=store, handler=handler)

        # Act

        # Assert
        assert isinstance(event, SystemEvent), "Expected event to be instance of SystemEvent"
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

def test_component_input_event():
    try:
        # Arrange        
        store = GameStore()
        handler = GameLoopHandler()
        event = InputEvent(store=store, handler=handler)

        # Act
        with pytest.raises(TypeError):
            event.input_event = BaseGameEvent()  # type: ignore
        event.input_event = Event()
        input_event = event.input_event

        # Assert
        assert isinstance(event, InputEvent), "Expected event to be instance of InputEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(input_event, Event), "Expected input_event to be instance of tcod.event.Event"

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
        handler = GameLoopHandler()
        event = EntityEvent(store=store, handler=handler)

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = BaseGameEntity()
        entity = event.entity
        
        # Assert
        assert isinstance(event, EntityEvent), "Expected event to be instance of EntityEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"   

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
        handler = GameLoopHandler()
        event = PlayerCharacterEvent(store=store, handler=handler)

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = PlayerCharacter()
        entity = event.entity

        with pytest.raises(TypeError):
            event.target = BaseGameEvent()  # type: ignore
        event.target = PlayerCharacter()
        target = event.target
        
        # Assert
        assert isinstance(event, PlayerCharacterEvent), "Expected event to be instance of PlayerCharacterEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, Character), "Expected entity to be instance of BaseGameEntity"   
        assert isinstance(target, Character), "Expected target to be instance of BaseGameEntity"   

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
        handler = MobLoopHandler()
        event = AICharacterEvent(store=store, handler=handler)

        # Act
        with pytest.raises(TypeError):
            event.entity = BaseGameEvent()  # type: ignore
        event.entity = AICharacter()
        entity = event.entity
        
        # Assert
        assert isinstance(event, AICharacterEvent), "Expected event to be instance of AICharacterEvent"
        assert isinstance(event, BaseGameEvent), "Expected event to be instance of BaseGameEvent"
        assert isinstance(event, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(event, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"
        assert isinstance(entity, Character), "Expected entity to be instance of Character"   

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass
