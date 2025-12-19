import pytest
from sys import path
import numpy as np

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.entities.ai import BaseAI, AIStateTableDict, manifest_example
from core_components.entities.library import AICharactor
from core_components.events.library import AIEvent, EntityEvent
from state import GameState

def test_component_base_ai_empty_init():
    # Arrange & Act
    ai = BaseAI(entity=None, state=None, state_table=None)

    # Assert
    try:
        assert not hasattr(ai, 'entity'), "Entity should be None"
        assert not hasattr(ai, 'state'), "State should be None"
        assert not hasattr(ai, 'state_table'), "State table should be None"
        assert not hasattr(ai, '_state_matrix'), "State matrix should be None"
        assert not hasattr(ai, '_state_mapping'), "State mapping should be None"

    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")

    # Atavise
    finally:
        del ai

def test_component_base_ai_full_init():
    # Arrange
    mock_entity = AICharactor(symbol='A', color=(255,0,0), name="TestAI")
    mock_state = GameState()  # Assuming GameState can be instantiated like this
    custom_state_table: AIStateTableDict = {'bits': ('is_alive',),
                                            'vector_tuples': ((0,), (1,)),
                                            'mapping': (None, AIEvent)}
    # Act
    ai = BaseAI(entity=mock_entity, state=mock_state, state_table=custom_state_table)

    # Assert
    try:    
        assert ai.entity == mock_entity, "Entity should match the mock entity"
        assert ai.state == mock_state, "State should match the mock state"
        assert ai.state_table == custom_state_table, "State table should match the custom state table"
        assert isinstance(ai._state_matrix, np.ndarray), "State matrix should be a numpy ndarray"
        assert isinstance(ai._state_mapping, np.ndarray), "State mapping should be a numpy ndarray"

    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai

def test_component_base_ai_get_state_vector():
    # Arrange
    mock_entity = AICharactor(symbol='A', color=(255,0,0), name="TestAI")
    mock_entity.is_alive = True
    mock_entity.is_spotted = False
    mock_entity.is_spotting = True
    mock_entity.is_targeting = False

    ai = BaseAI(entity=mock_entity)

    # Act
    state_vector = ai.get_state_vector()

    # Assert
    try:
        expected_vector = np.array([1, 0, 1, 0])
        assert np.array_equal(state_vector, expected_vector), f"State vector should be {expected_vector.tolist()}, got {state_vector.tolist()}"
    
    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai

def test_component_base_ai_get_event_from_state_vector():
    # Arrange
    mock_entity = AICharactor(symbol='A', color=(255,0,0), name="TestAI")
    ai = BaseAI(entity=mock_entity)

    # Act & Assert
    try:
        test_vectors = {
            (0, 0, 0, 0): 0,
            (0, 0, 1, 0): 0,
            (1, 0, 1, 0): AIEvent,
            (1, 0, 1, 1): EntityEvent,
        }

        for vec_tuple, expected_event in test_vectors.items():
            state_vector = np.array(vec_tuple)
            event = ai.get_event_from_state_vector(state_vector)
            if isinstance(expected_event, float) and np.isnan(expected_event):
                assert isinstance(event, float) and np.isnan(event), f"Expected NaN for state vector {vec_tuple}, got {event}"

    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai

def test_component_base_ai_set_state_matrix():
    # Arrange
    mock_entity = AICharactor(symbol='A', color=(255,0,0), name="TestAI")
    ai = BaseAI(entity=mock_entity)

    # Act
    ai._set_state_matrix()

    # Assert
    try:
        expected_matrix = np.array(manifest_example['vector_tuples'])
        assert np.array_equal(ai._state_matrix, expected_matrix), "State matrix does not match expected matrix"
    
    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai

def test_component_base_ai_create_event():
    # Arrange
    mock_entity = AICharactor(symbol='A', color=(255,0,0), name="TestAI")
    mock_target = AICharactor(symbol='T', color=(0,255,0), name="TargetAI")
    mock_state = GameState()
    ai = BaseAI(entity=mock_entity, state=mock_state)

    ai_event_type = AIEvent()
    entity_event_type = EntityEvent() 
    
    # Act
    created_ai_event = ai.create_event(ai_event_type, target=mock_target, state=mock_state) #type: ignore
    created_entity_event = ai.create_event(entity_event_type, target=mock_target, state=mock_state) #type: ignore

    # Assert
    try:
        assert isinstance(created_ai_event, AIEvent), "Created event should be an instance of AIEvent"
        assert created_ai_event.entity == mock_entity, "AIEvent entity should match mock entity"
        assert created_ai_event.message == "AI Event Triggered", "AIEvent message should match"

        assert isinstance(created_entity_event, EntityEvent), "Created event should be an instance of EntityEvent"
        assert created_entity_event.entity == mock_entity, "EntityEvent entity should match mock entity"
        assert created_entity_event.message == "Entity Event Triggered", "EntityEvent message should match"

    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai

def test_component_base_ai_update_state():
    # Arrange
    mock_entity = AICharactor(name="Test", color=(255, 255, 255), symbol='@')
    mock_entity.is_spotting = True
    mock_entity.is_targeting = False
    mock_entity.target = mock_entity

    ai = BaseAI(entity=mock_entity)
    mock_state = GameState()
    ai.state = mock_state
    mock_entity._ai = ai  # type: ignore

    # Act
    ai.update_state()
    
    # Assert
    try:
        assert mock_state.events.qsize() == 1, "State event queue should have one event"
    
    except AssertionError as e:
        pytest.fail(f"Assertion failed: {e}")
    # Atavise
    finally:
        del ai
