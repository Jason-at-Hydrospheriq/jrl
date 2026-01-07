import pytest
from sys import path
import time
from typing import cast
import threading
import tcod
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from store_components.portfolio import Portfolio
from store_components.atlas import Atlas
from protocols import StoredStateObject
from engine_components.store import GameStore
from entities.base import BaseGameEntity
from engine_components.ai import LoopHandler
from protocols import StateActionObject
from ai_components.base import BaseActionOnEntity, BaseActionOnTarget, BaseGameAction, BaseActionOnDestination
from ai_components.library import NoAction, WaitAction, EntityWaitAction, AIAcquireTargetAction, EntityMoveAction, BaseGameEvent, KeyDownAction
from atlas_components.tiles.base import TileCoordinate
from entities.library import AICharacter, PlayerCharacter


class DummyTarget:
    target: BaseGameEntity | None = None
    targeter: BaseGameEntity | None = None
    location: TileCoordinate | None = None
    hp: int = 0
    max_hp: int = 0

    def set_targeter(self, targeter: BaseGameEntity) -> None:
        self.targeter = targeter

    def clear_targeter(self) -> None:
        self.targeter = None

    def take_damage(self, damage: int) -> None:
        self.hp = max(0, self.hp - damage)


def test_component_base_game_action():
    try:
        # Arrange
        action = BaseGameAction()

        # Act
        with pytest.raises(NotImplementedError, match="Subclasses must implement the perform method."):
            action.perform()

        # Assert
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to be duck type as StoredStateObject Protocol"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_base_action_on_entity():
    try:
        # Arrange        
        action = BaseActionOnEntity()
        action.entity = BaseGameEntity()

        # Act 
        with pytest.raises(NotImplementedError, match="Subclasses must implement the perform method."):
            action.perform()

        # Assert
        assert isinstance(action, BaseActionOnEntity), "Expected action to be instance of BaseActionOnEntity"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_base_action_on_target():
    try:
        # Arrange        
        action = BaseActionOnTarget()
        action.entity = BaseGameEntity()
        action.target = BaseGameEntity()

        # Act 
        with pytest.raises(NotImplementedError, match="Subclasses must implement the perform method."):
            action.perform()

        # Assert
        assert isinstance(action, BaseActionOnTarget), "Expected action to be instance of BaseActionOnTarget"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert action.target is not None, "Expected target to be set"
        assert isinstance(action.target, BaseGameEntity), "Expected target to be instance of BaseGameEntity"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_base_action_on_destination():
    try:
        # Arrange        
        action = BaseActionOnDestination()
        action.entity = BaseGameEntity()
        action.destination = TileCoordinate.from_tuple((5, 10))

        # Act 
        with pytest.raises(NotImplementedError, match="Subclasses must implement the perform method."):
            action.perform()

        # Assert
        assert isinstance(action, BaseActionOnDestination), "Expected action to be instance of BaseActionOnDestination"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert action.destination is not None, "Expected destination to be set"
        assert isinstance(action.destination, TileCoordinate), "Expected destination to be instance of TileCoordinate"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_no_action():
    try:
        # Arrange        
        action = NoAction()
        
        # Act
        action.perform()
        
        # Assert
        assert isinstance(action, NoAction), "Expected action to be instance of NoAction"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_wait_action():
    try:
        # Arrange        
        wait_time = 500  # 500 milliseconds
        handler = LoopHandler()
        handler.start()  # type: ignore
        store = GameStore()  
        action = WaitAction(wait_time=wait_time)
        action.store = store
        action.handler = handler

        # Act
        start_time = time.time()
        action.perform()
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Assert
        assert isinstance(action, WaitAction), "Expected action to be instance of WaitAction"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.wait_time == wait_time, f"Expected wait_time to be {wait_time}, got {action.wait_time}"
        assert elapsed_time >= wait_time, f"Expected elapsed time to be at least {wait_time} ms, got {elapsed_time} ms"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_entity_wait_action():
    try:
        # Arrange        
        wait_time = 300  # 300 milliseconds
        handler = LoopHandler()
        handler.start()  # type: ignore
        store = GameStore()  
        entity = BaseGameEntity()
        action = EntityWaitAction(wait_time=wait_time)
        action.store = store
        action.handler = handler
        action.entity = entity

        # Act
        thread = threading.Thread(target=action.perform)
        initial_lock = entity.action_locked  # type: ignore
        start_time = time.time()
        thread.start()
        action_locked = entity.action_locked  # type: ignore
        entity.hp = 10
        update_hp_locked = entity.hp  # type: ignore
        thread.join()
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        final_lock = entity.action_locked  # type: ignore
        entity.hp = 8
        update_hp_unlocked = entity.hp  # type: ignore

        # Assert
        assert isinstance(action, EntityWaitAction), "Expected action to be instance of EntityWaitAction"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.wait_time == wait_time, f"Expected wait_time to be {wait_time}, got {action.wait_time}"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert elapsed_time >= wait_time, f"Expected elapsed time to be at least {wait_time} ms, got {elapsed_time} ms"

        assert initial_lock == False, "Expected entity action_locked to be False before wait"
        assert action_locked == True, "Expected entity action_locked to be True during wait"
        assert update_hp_locked == 0, "Expected entity hp to be the default value (locked) during wait"
        assert final_lock == False, "Expected entity action_locked to be False after wait"
        assert update_hp_unlocked == 8, "Expected entity hp to be updated value (unlocked) after wait"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_entity_acquire_target_action():
    try:
        # Arrange        
        action = AIAcquireTargetAction()
        action.store = GameStore()
        action.handler = LoopHandler()
        action.handler.start()  # type: ignore
        action.store.atlas = Atlas()
        tile_layout = action.store.atlas.active.get_tile_layout('floor')
        if tile_layout is not None:
            tile_layout[0:10,0:10] = True
        action.store.atlas.active.set_tiles(tile_layout, graphic_name='floor')
        action.store.portfolio = Portfolio()

        action.entity = AICharacter() 
        action.entity.name = "Test AI Character"
        action.entity.store = action.store
        action.entity.location = TileCoordinate.from_tuple((0, 0))
        action.entity.update()

        target = PlayerCharacter()
        target.name = "Test Player Character"
        target.store = action.store
        target.location = TileCoordinate.from_tuple((3, 3))

        action.store.portfolio.entities.add(action.entity)
        action.store.portfolio.entities.add(cast(PlayerCharacter, target))

        # Act 
        initial_entity_target = action.entity.target
        initial_focus_state = action.entity.focus.state  # type: ignore
        initial_event_queue_size = action.handler.events.qsize()
        initial_action_queue_size = action.handler.actions.qsize()
        initial_store_log_size = len(action.store.log.messages)  # type: ignore
        
        action.perform()
        
        final_entity_target = action.entity.target
        final_focus_state = action.entity.focus.state  # type: ignore
        final_event_queue_size = action.handler.events.qsize()
        final_action_queue_size = action.handler.actions.qsize()
        final_store_log_size = len(action.store.log.messages)  # type: ignore

        # Assert
        assert isinstance(action, AIAcquireTargetAction), "Expected action to be instance of EntityAcquireTargetAction"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"

        assert initial_entity_target == None, "Expected entity's target to remain unchanged after acquire target action"
        assert initial_focus_state ==  'idle', "Expected entity's focus state to be 'idle' before acquire target action"
        assert initial_event_queue_size == 0, "Expected initial event queue size to be 0"
        assert initial_action_queue_size == 0, "Expected initial action queue size to be 0"
        assert initial_store_log_size == 0, "Expected initial store log size to be 0"

        assert final_entity_target == target, "Expected entity's target to be set to the target character after acquire target action"
        assert final_focus_state == 'tracking', "Expected entity's focus state to be 'tracking' after acquire target action"
        assert final_event_queue_size == initial_event_queue_size + 1, "Expected final event queue size to be +1 added by acquire target action"
        assert final_action_queue_size == initial_action_queue_size, "Expected final action queue size to be unchanged by acquire target action"
        assert final_store_log_size == initial_store_log_size + 1, "Expected final store log size to be +1 added by acquire target action"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_move_action():
    try:
        # Arrange        
        action = EntityMoveAction()
        action.store = GameStore()
        action.handler = LoopHandler()
        action.handler.start()  # type: ignore
        action.store.atlas = Atlas()
        tile_layout = action.store.atlas.active.get_tile_layout('floor')
        if tile_layout is not None:
            tile_layout[0:3,0:3] = True
            action.store.atlas.active.set_tiles(tile_layout, graphic_name='floor')

        action.entity = AICharacter() 
        action.entity.name = "Test AI Character"
        action.entity.store = action.store
        action.entity.location = TileCoordinate.from_tuple((0, 0), parent_map_size=action.store.atlas.active.grid.size)
        action.entity.update()

        colliding_entity = PlayerCharacter()
        colliding_entity.name = "Colliding Player Character"
        colliding_entity.store = action.store
        colliding_entity.location = TileCoordinate.from_tuple((2, 2), parent_map_size=action.store.atlas.active.grid.size)
        action.store.portfolio = Portfolio()
        action.store.portfolio.entities.add(action.entity)
        action.store.portfolio.entities.add(colliding_entity)

        move_destination = TileCoordinate.from_tuple((1, 1), parent_map_size=action.store.atlas.active.grid.size)
        wall_destination = TileCoordinate.from_tuple((3, 3), parent_map_size=action.store.atlas.active.grid.size)
        boundary_destination = TileCoordinate.from_tuple((-1, 0), parent_map_size=action.store.atlas.active.grid.size)
        entity_destination = TileCoordinate.from_tuple((2, 2), parent_map_size=action.store.atlas.active.grid.size)

        # Act 
        initial_location = action.entity.location
        action.destination = move_destination
        action.perform()
        move_location = action.entity.location

        action.destination = wall_destination
        action.perform()
        wall_location = action.entity.location

        action.destination = boundary_destination
        action.perform()
        boundary_location = action.entity.location

        action.destination = entity_destination
        action.perform()
        entity_location = action.entity.location
        entity_target = action.entity.target

        action.destination = move_destination
        thread = threading.Thread(target=action.perform)
        initial_lock = action.entity.action_locked  # type: ignore
        action.entity.speed = -100  # Slow down for test
        start_time = time.time()
        thread.start()
        time.sleep(0.005)  # Ensure the thread has started
        print(f"During move: Lock = {action.entity.action_locked}")  # type: ignore
        action_locked = action.entity.action_locked  # type: ignore
        action.entity.hp = 10
        update_hp_locked = action.entity.hp  # type: ignore
        thread.join()
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        final_lock = action.entity.action_locked  # type: ignore
        action.entity.hp = 8
        update_hp_unlocked = action.entity.hp  # type: ignore

        # Assert
        assert isinstance(action, EntityMoveAction), "Expected action to be instance of EntityMoveAction"
        assert isinstance(action, BaseGameAction), "Expected action to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected action to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected action to duck type as StoredStateObject Protocol"
        assert action.entity is not None, "Expected entity to be set"
        assert isinstance(action.entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert action.destination is not None, "Expected destination to be set"
        assert isinstance(action.destination, TileCoordinate), "Expected destination to be instance of TileCoordinate"

        assert initial_location == TileCoordinate.from_tuple((0, 0), parent_map_size=action.store.atlas.active.grid.size), "Expected entity's initial location to be (0,0)"
        assert move_location == move_destination, "Expected entity to have moved to the move destination"
        assert wall_location == move_location, "Expected entity's location to remain unchanged when moving into a wall"
        assert boundary_location == move_location, "Expected entity's location to remain unchanged when moving out of bounds"
        assert entity_location == move_location, "Expected entity's location to remain unchanged when moving into another entity"
        assert entity_target == colliding_entity, "Expected entity's target to be set to the colliding entity after move attempt"

        assert initial_lock == False, "Expected entity action_locked to be False before move"
        assert action_locked == True, "Expected entity action_locked to be True during move"
        assert update_hp_locked == 0, "Expected entity hp to be the default value (locked) during move"
        assert final_lock == False, "Expected entity action_locked to be False after move"
        assert update_hp_unlocked == 8, "Expected entity hp to be updated value (unlocked) after move"
        assert elapsed_time >= 100, "Expected move action to take at least 100 ms"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_keydown_action():
    try:
        # Arrange        
        store = GameStore()
        store.atlas = Atlas()
        store.portfolio = Portfolio()
        handler = LoopHandler()
        player = PlayerCharacter(store=store, location=TileCoordinate.from_tuple((1, 1), parent_map_size=store.atlas.active.grid.size))

        store.portfolio.player = player
        action = KeyDownAction(store=store, handler=handler)

        handler.start()  # type: ignore

        # Act
        action.input_event = tcod.event.KeyDown(sym=tcod.event.K_LEFT, mod=0, scancode=0)
        input_event = action.input_event
        initial_event_queue_size = handler.events.qsize()
        initial_action_queue_size = handler.actions.qsize() 
        action.perform()
        final_event_queue_size = handler.events.qsize()
        final_action_queue_size = handler.actions.qsize()
        final_action = handler.actions.get_nowait()

        # Assert
        assert isinstance(final_action, EntityMoveAction), "Expected event to be instance of KeyDownAction"
        assert isinstance(action, BaseGameAction), "Expected event to be instance of BaseGameAction"
        assert isinstance(action, StateActionObject), "Expected event to duck type as StateActionObject Protocol"
        assert isinstance(action, StoredStateObject), "Expected event to be duck type as StoredStateObject Protocol"

        assert final_action.destination == TileCoordinate.from_tuple((0, 1), parent_map_size=action.store.atlas.active.grid.size), "Expected action's destination to be the same (x - 1, y)"  # type: ignore
        assert final_event_queue_size == initial_event_queue_size, "Expected no event to be added to handler's event queue"
        assert final_action_queue_size == initial_action_queue_size + 1, "Expected an action to be added to handler's action queue"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

