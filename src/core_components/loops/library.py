from __future__ import annotations
from time import sleep
from typing import TYPE_CHECKING, cast
import tcod

from core_components.entities.library import BaseGameEntity, Character, AICharacter, MobileEntity, TargetingEntity
from core_components.loops.base import BaseActionOnDestination, BaseGameAction, BaseGameEvent, BaseActionOnEntity
from core_components.loops.custom_types import StateActionObject, StateHandler
from core_components.maps.tiles.base import TileCoordinate

if TYPE_CHECKING:
    from core_components.store import GameStore
    from core_components.loops.handlers import GameLoopHandler, MobLoopHandler


class SystemEvent(BaseGameEvent):
    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
        super().__init__(store, handler)

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class InputEvent(BaseGameEvent):
    _input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: GameLoopHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
        super().__init__(store, handler)
        self._input_event = input_event

    @property
    def input_event(self) -> tcod.event.Event | None:
        return self._input_event

    @input_event.setter
    def input_event(self, value: tcod.event.Event | None) -> None:
        if value is not None and not isinstance(value, tcod.event.Event):
            raise TypeError("input_event must be an instance of tcod.event.Event or None")
        self._input_event = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class KeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: GameLoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
        super().__init__(store, handler)
        self.input_event = input_event

    def perform(self) -> None:
        if isinstance(self.input_event, tcod.event.KeyboardEvent):
            key_sim = self.input_event.sym if self.input_event else None
            destination = (0, 0)

            if self.store and self.store.portfolio.player and key_sim is not None:  # type: ignore | The store for this action must be GameStore.
                if self.store.portfolio.player.location:  # type: ignore | The store for this action must be GameStore.
                    destination = (self.store.portfolio.player.location.x, self.store.portfolio.player.location.y) # type: ignore | The store for this action must be GameStore.

                # Parse movement keys
                match key_sim:
                    case tcod.event.KeySym.LEFT:
                        destination = (destination[0] - 1, destination[1])
                    case tcod.event.KeySym.A:
                        destination = (destination[0] - 1, destination[1])
                    case tcod.event.KeySym.RIGHT:
                        destination = (destination[0] + 1, destination[1])
                    case tcod.event.KeySym.D:
                        destination = (destination[0] + 1, destination[1])
                    case tcod.event.KeySym.UP:
                        destination = (destination[0], destination[1] - 1)
                    case tcod.event.KeySym.W:
                        destination = (destination[0], destination[1] - 1)
                    case tcod.event.KeySym.DOWN:
                        destination = (destination[0], destination[1] + 1)
                    case tcod.event.KeySym.S:
                        destination = (destination[0], destination[1] + 1)
                
                if destination != (0,0):      
                    self.handler.send(EntityMoveAction(store=self.store, handler=self.handler, entity=self.store.portfolio.player,  # type: ignore | The store for this action must be GameStore.
                                                           destination=TileCoordinate.from_tuple(destination, parent_map_size=self.store.atlas.active.grid.size)))  # type: ignore | The store for this action must be GameStore.


class EntityEvent(BaseGameEvent):
    _entity: BaseGameEntity | None

    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity

    @property
    def entity(self) -> BaseGameEntity | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: BaseGameEntity | None) -> None:
        if value is not None and not isinstance(value, BaseGameEntity):
            raise TypeError("entity must be an instance of BaseGameEntity or None")
        self._entity = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class PlayerCharacterEvent(BaseGameEvent):
    _entity: Character | None
    _target: Character | None
    
    def __init__(self, store: GameStore | None = None, handler: GameLoopHandler | None = None, entity: Character | None = None, target: Character | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity
        self._target = target

    @property
    def entity(self) -> Character | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: Character | None) -> None:
        if value is not None and not isinstance(value, Character):
            raise TypeError("entity must be an instance of Character or None")
        self._entity = value
    
    @property
    def target(self) -> Character | None:
        return self._target
    
    @target.setter
    def target(self, value: Character | None) -> None:
        if value is not None and not isinstance(value, Character):
            raise TypeError("target must be an instance of Character or None")
        self._target = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class AICharacterEvent(BaseGameEvent):
    _entity: AICharacter | None
    _target: Character | None

    def __init__(self, store: GameStore | None = None, handler: MobLoopHandler | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
        super().__init__(store, handler)
        self._entity = entity
        self._target = target
    
    @property
    def entity(self) -> AICharacter | None:
        return self._entity
    
    @entity.setter
    def entity(self, value: AICharacter | None) -> None:
        if value is not None and not isinstance(value, AICharacter):
            raise TypeError("entity must be an instance of AICharacter or None")
        self._entity = value

    @property
    def target(self) -> Character | None:
        return self._target
    
    @target.setter
    def target(self, value: Character | None) -> None:
        if value is not None and not isinstance(value, Character):
            raise TypeError("target must be an instance of Character or None")
        self._target = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class NonEvent(BaseGameEvent):
    pass


class NoAction(BaseGameAction):

    def perform(self) -> None:
        pass


class WaitEvent(SystemEvent):
    wait_time: int

    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, wait_time: int = 0) -> None:
        super().__init__(store, handler)
        self.wait_time = wait_time

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class WaitAction(BaseGameAction):
    wait_time: int = 0  # Time to wait in milliseconds

    def __init__(self, wait_time: int = 0) -> None:
        super().__init__()
        self.wait_time = wait_time

    def perform(self) -> None:
        sleep(self.wait_time / 1000.0) # Convert milliseconds to seconds
        self.handler.handle(None) # type: ignore
        

class EntityWaitEvent(EntityEvent, WaitEvent):
    
    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, wait_time: int = 0) -> None:
        EntityEvent.__init__(self, store, handler, entity)
        WaitEvent.__init__(self, store, handler, wait_time)


class EntityWaitAction(WaitAction, BaseActionOnEntity):
    """
    The EntityWaitAction is the action of the Wait behavior. It is called by an EntityWaitEvent created by an entity.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None, wait_time: int = 0) -> None:
        WaitAction.__init__(self, wait_time)
        BaseActionOnEntity.__init__(self, store, handler, entity)

    def perform(self) -> None:
        if self.entity:
            self.entity.action_locked = True  # Lock the entity's actions during the wait
            sleep(self.wait_time / 1000.0) # Convert milliseconds to seconds
            self.entity.action_locked = False  # Unlock the entity's actions after the wait

        if self.handler:
            self.handler.handle(None) # type: ignore


class AIAcquireTargetEvent(EntityEvent):
    pass


class AIAcquireTargetAction(BaseActionOnEntity):
    """
    The EntityAcquireTargetAction is the action of the AcquireTarget behavior. It is called by an AIAcquireTargetEvent created by an AICharacter.
    
    Duck Types: StateActionObject, StoredStateObject
    """
    def __init__(self, store: GameStore | None = None, handler:  MobLoopHandler | None = None, entity: AICharacter | None = None) -> None:
        super().__init__(store, handler, entity)

    def perform(self) -> None:

        if isinstance(self.entity, AICharacter) and self.store is not None:
            self.entity.acquire_target()
            self.entity.update()

            if self.entity.target is not None:
                match self.entity.focus.state:  # type: ignore | State machine attribute created dynamically
                    case 'searching':
                        text = f"The {self.entity.name}'s guard is up."
                    case 'tracking':
                        text = f"The {self.entity.name} has spotted {self.entity.target.name}"  # type: ignore | Entity in this state must have a target.
                    case 'targeting':
                        text = f"The {self.entity.name} is looking at {self.entity.target.name} with malice."  # type: ignore | Entity in this state must have a target.
                    case 'idle':
                        text = f"The {self.entity.name} looks bored."
                    case _:
                        text = f"The {self.entity.name} looks confused."

                self.store.log.add(text=text)  # type: ignore | AICharacter must have a GameStore to log messages.
        
                if self.handler:
                    self.handler.send(EntityWaitEvent(wait_time=100, store=self.store, handler=self.handler, entity=self.entity))  # type: ignore


class EntityMoveAction(BaseActionOnDestination):

    def __init__(self, store: GameStore | None = None, handler:  StateHandler | None = None, entity: MobileEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
        super().__init__(store, handler, entity, destination)

    def perform(self) -> None:
        if isinstance(self.entity, MobileEntity) and self.store and self.destination:
            self.entity.destination = self.destination
            self.entity.update()

            match self.entity.collision.state:  # type: ignore | State machine attribute created dynamically
                case 'not_colliding':
                    speed = 0
                    if self.entity.speed:
                        speed = self.entity.speed

                    if self.entity.action_locked is False:
                        EntityWaitAction(wait_time=50 - speed, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.
                        self.entity.move()
                        self.entity.update()
                
                case 'colliding_with_terrain':
                    return  # Do nothing on terrain collision for now.
                
                case 'colliding_with_boundary':
                    return  # Do nothing on map boundary collision for now.
                
                case 'colliding_with_entity':
                    if isinstance(self.entity, TargetingEntity):
                        target = self.store.portfolio.get_entity_at_location(self.entity.destination)[0]  # type: ignore | The store for this action must be GameStore.
                        self.entity.set_target(target)  
                        self.entity.update()

                        if self.entity.action_locked is False:
                            speed = 0
                            if self.entity.speed:
                                speed = self.entity.speed
                            EntityWaitAction(wait_time=50 - speed, store=self.store, handler=self.handler, entity=self.entity).perform() # type: ignore | The store for this action must be GameStore.


# """These System Events are generated by the game engine itself. They are not tied to any specific entity or AI, but rather represent global game states or actions."""
# class GameStartEvent(SystemEvent):
#     pass




# class GameOverEvent(SystemEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None) -> None:
#         super().__init__(handler, state)


# class FOVUpdateEvent(SystemEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None) -> None:
#         super().__init__(handler, state)
#     """Triggers the FOV update for all entities."""


# """These Entity Events are generated by entities in response to actions or interactions."""
# class NoCollision(EntityEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: BaseGameEntity | None = None) -> None:
#         super().__init__(handler, state, entity=entity)


# class WallCollision(EntityEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: BaseGameEntity | None = None) -> None:
#         super().__init__(handler, state, entity=entity)


# class MapBoundaryCollision(EntityEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: BaseGameEntity | None = None) -> None:
#         super().__init__(handler, state, entity=entity)


# class TargetCollision(EntityEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: BaseGameEntity | None = None) -> None:
#         super().__init__(handler, state, entity=entity)
    

# class MeleeCollision(EntityEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: BaseGameEntity | None = None) -> None:
#         super().__init__(handler, state, entity=entity)


# """These Combat Events are generated during combat interactions between entities and require targeting information."""
# class EntityCombatEvent(PlayerCharacterEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: Character | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class MeleeAttackEvent(EntityCombatEvent):
#     entity: Character | None
#     target: Character | None

#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: Character | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class MissileAttackEvent(EntityCombatEvent):
#     pass


# class SpellAttackEvent(EntityCombatEvent):
#     pass


# """These AI Events are generated by AI-controlled entities to trigger AI generated behaviors."""
# class TargetedAIEvent(AICharacterEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class AttackedAIEvent(AICharacterEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class TargetAvailableAIEvent(AICharacterEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class OnTargetAIEvent(AICharacterEvent):
#     def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
#         super().__init__(handler, state, entity=entity, target=target)


# class TargetOutOfRangeAIEvent(AICharacterEvent):
    # def __init__(self, handler: GameLoopHandler | None = None, state: GameStore | None = None, entity: AICharacter | None = None, target: Character | None = None) -> None:
    #     super().__init__(handler, state, entity=entity, target=target)