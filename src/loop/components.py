#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from typing import AbstractSet, Tuple, TypeVar
from transitions import Machine
from queue import Queue, Full

from game_types import GameAction, GameEvent, StateActionObject, StatefulObject
from entities.behaviors import *

class BaseGameLoop:
    store: StatefulObject | None
    events: Queue[StateActionObject]
    actions: Queue[StateActionObject]

    def __init__(self, store: StatefulObject | None = None) -> None:
        self.store = store
        self.events = Queue(maxsize=5)
        self.actions = Queue(maxsize=5)

    def send(self, loop_item: StateActionObject)  -> bool:
        try:

            if isinstance(loop_item, GameEvent):
                self.events.put_nowait(loop_item)
                return True

            elif isinstance(loop_item, GameAction):
                self.actions.put_nowait(loop_item)
                return True

            return False

        except Full:
            return False

        except Exception as e:
            raise e


class BaseGameTransformer:
    """The BaseGameTransformer is responsible for tranforming Game Inputs and AI Actions into Game Events."""
    store: StatefulObject | None
    behaviors: AbstractSet[Tuple[str, GameAction]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.
    T = TypeVar('T', bound=StateActionObject)

    def __init__(self, store: StatefulObject | None = None, behaviors: AbstractSet[Tuple[str, GameAction]] | None = None) -> None:
        self.store = store
        self.behaviors = behaviors

    def transform(self, event: StateActionObject) -> GameAction | None:
        """Should NOT be overidden by subclasses. Retrieves a behavior (Event or Action) by name from the behaviors set."""
        name = event.__class__.__name__.lower()
        if self.behaviors is not None and self.is_started(): # type: ignore
            for behavior in self.behaviors:
                if name == behavior[0]:
                    action = behavior[1]
                    action = deepcopy(action)
                    attributes = dir(event)
                    attributes = [attr for attr in attributes if not attr.startswith('_') and not callable(getattr(event, attr))]
                    for attr in attributes:
                        if hasattr(action, attr):
                            setattr(action, attr, getattr(event, attr))
                    return action
            raise ValueError(f"Behavior not found for event: {name}")
        raise ValueError(f"State behaviors object not found: {name}")


class SubLoopHandler(BaseGameLoop, BaseGameTransformer):
    """The LoopHandler is responsible for tranforming Game Inputs and AI Actions into Game Events
    and sending them to the appropriate Queue."""
    machine: Machine

    def __init__(self, store: StatefulObject | None = None, behaviors: AbstractSet[Tuple[str, GameAction]] | None = None) -> None:
        super().__init__(store=store)
        BaseGameTransformer.__init__(self, store=store, behaviors=behaviors) # type: ignore
        states = ['started', 'stopped']
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]

        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

    def handle(self, event: StateActionObject | None = None) -> bool:
        if self.is_started() and event is not None:  # type: ignore | State machine method is dynamically added
            behavior = self.transform(event) # type: ignore
            if behavior is not None:
                return self.send(behavior)
        return False


mob_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    entitywait, update_focus, investigate, pursue, acquire_target, entityattack
}
game_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    entitywait, entityattack,
    ('inputevent', KeyDownAction()),
}