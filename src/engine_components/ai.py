#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from queue import Queue
from transitions import Machine
import threading
from typing import TYPE_CHECKING, List, AbstractSet, Tuple, TypeVar
import time
import queue

from loop_components import *
from game_types import StatefulObject, StateActionObject,  GameAction, GameEvent

if TYPE_CHECKING:
    from store import GameStore

GLOBAL_LOOP_COOLDOWN_TIME = 25  # Global cooldown time in milliseconds

game_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
    ('inputevent', KeyDownAction()),
}

mob_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('entitywaitevent', EntityWaitAction()),
}

class BaseGameLoop:
    store: StatefulObject | None
    events: Queue[StateActionObject]
    actions: Queue[StateActionObject]

    def __init__(self, store: StatefulObject | None = None) -> None:
        self.store = store
        self.events = Queue()
        self.actions = Queue()

    def send(self, loop_item: StateActionObject)  -> bool:
        try:

            if isinstance(loop_item, GameEvent):
                self.events.put(loop_item)
                return True

            elif isinstance(loop_item, GameAction):
                self.actions.put(loop_item)
                return True

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


class LoopHandler(BaseGameLoop, BaseGameTransformer):
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


class GameAI:
    """
    The GameHandler manages all of the game loops, processing events and actions in separate threads. It has a list of managed threads and provides an API for starting and stopping the loops. 
    It uses a GameLoopHandler to handle the transformation and dispatching of events and actions.

    Duck Types: StatefulObject, StoredStateObject
    """
    store: GameStore | None
    machine: Machine
    game_loop_handler: LoopHandler | None
    mob_loop_handler: LoopHandler | None
    threads: List[threading.Thread | None]
    stop_signal: threading.Event

    def __init__(self, store: GameStore | None = None) -> None:
        self.store = store
        self.game_loop_handler = LoopHandler(store=store, behaviors=game_behaviors)
        self.mob_loop_handler = LoopHandler(store=store, behaviors=mob_behaviors)
        self.threads = []
        self.stop_signal = threading.Event()
        #threading.excepthook = self.threaded_exception_handler

        states = ['idle', 
                  {'name': 'started', 'on_enter': '_start'},
                  {'name': 'paused', 'on_enter': '_pause'},
                  {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'},
            {'trigger': 'pause', 'source': 'started', 'dest': 'paused'},
            {'trigger': 'start', 'source': 'paused', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'paused', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

    def _start(self) -> None:
        """Starts the loop threads."""
        try:
            self.game_loop_handler.start() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.start()  # type: ignore | State machine attribute created dynamically
            self.stop_signal.clear()

            if not self.threads:
                self.threads.append(threading.Thread(target=self.game_event_loop))
                self.threads.append(threading.Thread(target=self.game_action_loop))
                self.threads.append(threading.Thread(target=self.mob_event_loop))
                self.threads.append(threading.Thread(target=self.mob_action_loop))
                for thread in self.threads:
                    if thread is not None:
                        thread.start()
            print("Game loops started.")

        except Exception as e:
            print(f"Error starting loops: {e}")

    def _pause(self) -> None:
        self.game_loop_handler.stop()  # type: ignore | State machine attribute created dynamically
        self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

    def _stop(self) -> None:
        """Stops the loop threads."""
        try:
            self.stop_signal.set()
            for thread in self.threads:
                if thread is not None:
                    thread.join()
            self.game_loop_handler.stop() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

        except Exception as e:
            print(f"Error stopping loops: {e}")
    
    def game_action_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue
                next_action = None
                if self.game_loop_handler and self.game_loop_handler.actions is not None:
                    next_action = self.game_loop_handler.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
                    next_action.perform()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing action: {e}")
                break
    
    def mob_action_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue
                next_action = None
                if self.mob_loop_handler and self.mob_loop_handler.actions is not None:
                    next_action = self.mob_loop_handler.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
                    next_action.perform()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing action: {e}")
                break

    def game_event_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue
                next_event = None
                if self.game_loop_handler and self.game_loop_handler.events is not None:
                    next_event = self.game_loop_handler.events.get_nowait()
                if next_event is not None and isinstance(next_event, GameEvent):
                    next_event.trigger()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing event: {e}")
                break

    def mob_event_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue
                next_event = None
                if self.mob_loop_handler and self.mob_loop_handler.events is not None:
                    next_event = self.mob_loop_handler.events.get_nowait()
                if next_event is not None and isinstance(next_event, GameEvent):
                    next_event.trigger()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing event: {e}")
                break

    def threaded_exception_handler(self, args):
        print(f"Thread failed: {args.thread.name}")
        print(f"Exception type: {args.exc_type}")
        print(f"Exception value: {args.exc_value}")
        print(f"Exception traceback: {args.exc_traceback}")
