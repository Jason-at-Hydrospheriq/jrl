#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import traceback
from transitions import Machine
import threading
from typing import TYPE_CHECKING, List
import time
import queue

from delays import GLOBAL_ACTION_COOLDOWN_TIME, GLOBAL_COOLDOWN_TIME
from loop.components import SubLoopHandler, game_behaviors, mob_behaviors
from game_types import GameAction, GameEvent, StateActionObject

if TYPE_CHECKING:
    from store import GameStore

class GameLoops:
    """
    The GameHandler manages all of the game loops, processing events and actions in separate threads. It has a list of managed threads and provides an API for starting and stopping the loops. 
    It uses a GameLoopHandler to handle the transformation and dispatching of events and actions.

    Duck Types: StatefulObject, StoredStateObject
    """
    store: GameStore | None
    machine: Machine
    player_loop_handler: SubLoopHandler | None
    mob_loop_handler: SubLoopHandler | None
    threads: List[threading.Thread | None]
    stop_signal: threading.Event
    last_event_time: dict = {}

    def __init__(self, store: GameStore | None = None) -> None:
        self.store = store
        self.player_loop_handler = SubLoopHandler(store=store, behaviors=game_behaviors)
        self.mob_loop_handler = SubLoopHandler(store=store, behaviors=mob_behaviors)
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
            self.player_loop_handler.start() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.start()  # type: ignore | State machine attribute created dynamically
            self.stop_signal.clear()

            if not self.threads:
                self.threads.append(threading.Thread(target=self.player_event_loop))
                self.threads.append(threading.Thread(target=self.player_action_loop))
                self.threads.append(threading.Thread(target=self.mob_event_loop))
                self.threads.append(threading.Thread(target=self.mob_action_loop))
                for thread in self.threads:
                    if thread is not None:
                        thread.start()
            print("Game loops started.")

        except Exception as e:
            print(f"Error starting loops: {e}")

    def _pause(self) -> None:
        self.player_loop_handler.stop()  # type: ignore | State machine attribute created dynamically
        self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

    def _stop(self) -> None:
        """Stops the loop threads."""
        try:
            self.stop_signal.set()
            for thread in self.threads:
                if thread is not None:
                    thread.join()
            self.player_loop_handler.stop() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

        except Exception as e:
            print(f"Error stopping loops: {e}")
    
    def is_spam(self, loop_item: StateActionObject) -> bool:
        event_type = type(loop_item)
        current_time = time.time()
        
        # Check if this event type is on cooldown
        if event_type in self.last_event_time:
            time_diff = current_time - self.last_event_time[event_type]

            if time_diff < GLOBAL_ACTION_COOLDOWN_TIME / 1000:
                print(f"Ignoring spam event: {loop_item}, dt: {(time_diff*1000):.2f}ms")
                return True # Ignore the event (spam)

        # Process the event and update the last event time
        self.last_event_time[event_type] = current_time
        print(f"Processing event: {loop_item}")
        return False

    def player_event_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        last_beat = 0.0
        ctr = 0

        try:
            while not self.stop_signal.is_set():  # type: ignore
                ctr += 1
                next_event = None
    
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if ctr % 100 == 0:
                        print(f"Player Event Loop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        print(f"Player Event Loop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time
                    

                if self.player_loop_handler and self.player_loop_handler.events is not None:
                    if not self.player_loop_handler.events.empty(): 
                        next_event = self.player_loop_handler.events.get_nowait()

                if next_event is not None and isinstance(next_event, GameEvent):
                    if not self.is_spam(next_event):
                        next_event.trigger()

                time.sleep(0.005)

        except BaseException as e:
            print(f"Error processing player event: {e}")
            traceback.print_exc()

    def player_action_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue
                next_action = None
                if self.player_loop_handler and self.player_loop_handler.actions is not None:
                    if not self.player_loop_handler.actions.empty():
                        next_action = self.player_loop_handler.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
                    if not self.is_spam(next_action):
                        next_action.perform()
                
            except queue.Empty:
                time.sleep(0.005)

            except BaseException as e:
                print(f"Error processing player action: {e}")
                traceback.print_exc()
                break

    def mob_event_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            ctr = 0
            last_beat = 0.0
            
            try:
                ctr += 1
                next_event = None
    
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if not ctr % 100 == 0:
                        print(f"Mob Event Loop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        print(f"Mob Event Loop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time

                next_event = None
                if self.mob_loop_handler and self.mob_loop_handler.events is not None:
                    if not self.mob_loop_handler.events.empty(): 
                        next_event = self.mob_loop_handler.events.get_nowait()
                if next_event is not None and isinstance(next_event, GameEvent):
                    if not self.is_spam(next_event):
                        next_event.trigger()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing mob event: {e}")
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
                    if not self.mob_loop_handler.actions.empty():
                        next_action = self.mob_loop_handler.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
                    if not self.is_spam(next_action):
                        next_action.perform()
                
            except queue.Empty:
                time.sleep(0.005)

            except BaseException as e:
                
                print(f"Error processing mob action: {e}")
                traceback.print_exc()
                break

    def threaded_exception_handler(self, args):
        print(f"Thread failed: {args.thread.name}")
        print(f"Exception type: {args.exc_type}")
        print(f"Exception value: {args.exc_value}")
        print(f"Exception traceback: {args.exc_traceback}")

    def update(self) -> None:
        if self.store and self.store.portfolio:
            self.store.portfolio.update()