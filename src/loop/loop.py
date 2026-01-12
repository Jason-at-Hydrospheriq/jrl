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
from display.display import GameDisplay
from entities.behaviors.mob import mob_behaviors
from entities.behaviors.player import player_behaviors
from loop.components import SubLoopHandler
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
    display: GameDisplay | None
    machine: Machine
    inputs_loop_handler: SubLoopHandler | None
    mob_loop_handler: SubLoopHandler | None
    threads: List[threading.Thread | None]
    stop_signal: threading.Event
    last_event_time: dict = {}

    def __init__(self, store: GameStore | None = None, display: GameDisplay | None = None) -> None:
        self.store = store
        self.display = display
        # Add loop handler and thread for viewer later
        self.inputs_loop_handler = SubLoopHandler(store=store, behaviors=player_behaviors)
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
            self.inputs_loop_handler.start() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.start()  # type: ignore | State machine attribute created dynamically
            self.stop_signal.clear()

            if not self.threads:
                self.threads.append(threading.Thread(target=self.display_loop, daemon=True))
                self.threads.append(threading.Thread(target=self.ai_main_loop, daemon=True))
                self.threads.append(threading.Thread(target=self.inputs_subloop, daemon=True))
                self.threads.append(threading.Thread(target=self.mob_subloop, daemon=True))

                for thread in self.threads:
                    if thread is not None:
                        thread.start()

            print("Game loops started.")

        except Exception as e:
            print(f"Error starting loops: {e}")

    def _pause(self) -> None:
        self.inputs_loop_handler.stop()  # type: ignore | State machine attribute created dynamically
        self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

    def _stop(self) -> None:
        """Stops the loop threads."""
        try:
            self.stop_signal.set()
            for thread in self.threads:
                if thread is not None:
                    thread.join()
            
            print("Game loops stopped.")

            self.inputs_loop_handler.stop() # type: ignore | State machine attribute created dynamically
            self.mob_loop_handler.stop()  # type: ignore | State machine attribute created dynamically

        except Exception as e:
            print(f"Error stopping loops: {e}")
    
    def loop_throttle(self) -> bool:
        """Throttle the loop to prevent it from running too fast."""
        global GLOBAL_COOLDOWN_TIME

        try:
            time.sleep(GLOBAL_COOLDOWN_TIME / 1000)
            return True
        
        except Exception as e:
            print(f"Error in loop throttle: {e}")
            return False
        
    def display_loop(self) -> None:
        """Main display loop that runs in a separate thread."""
        last_beat = time.time()
        ctr = 0

        try:
            while not self.stop_signal.is_set():
                ctr += 1
    
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if ctr % 100 == 0:
                        print(f"Display Loop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        print(f"Display Loop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time

                if self.display and self.display.is_started():  # type: ignore
                    self.display.render()

        except Exception as e:
            print(f"Display loop encountered an error: {e}")
            traceback.print_exc()

    def ai_main_loop(self) -> None:
        """Main AI loop that runs in a separate thread."""
        while not self.stop_signal.is_set():  # type: ignore
            try:
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                # Process AI logic here
                if self.loop_throttle():
                    self.update()

            except Exception as e:
                print(f"AI main loop encountered an error: {e}")
                traceback.print_exc()

    def inputs_subloop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        last_beat = 0.0
        ctr = 0

        try:
            while not self.stop_signal.is_set():  # type: ignore
                ctr += 1
                next_event = None
                next_action = None

                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if ctr % 100 == 0:
                        # print(f"Player SubLoop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        pass
                        # print(f"Player SubLoop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time
                    
                if self.inputs_loop_handler and self.inputs_loop_handler.events is not None:
                    if not self.inputs_loop_handler.events.empty(): 
                        next_event = self.inputs_loop_handler.events.get_nowait()

                    if next_event is not None and isinstance(next_event, GameEvent):
                            next_event.trigger()

                if self.inputs_loop_handler and self.inputs_loop_handler.actions is not None:
                    if not self.inputs_loop_handler.actions.empty():
                        next_action = self.inputs_loop_handler.actions.get_nowait()

                    if next_action is not None and isinstance(next_action, GameAction):
                            next_action.perform()

        except BaseException as e:
            print(f"Error processing player sub loop item: {e}")
            traceback.print_exc()

    def mob_subloop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():  # type: ignore
            ctr = 0
            last_beat = 0.0
            next_action = None
            try:
                ctr += 1
                next_event = None
                next_event = None
    
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if not ctr % 100 == 0:
                        #print(f"Mob SubLoop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        pass #print(f"Mob SubLoop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time

                if self.mob_loop_handler and self.mob_loop_handler.events is not None:
                    if not self.mob_loop_handler.events.empty(): 
                        next_event = self.mob_loop_handler.events.get_nowait()

                    if next_event is not None and isinstance(next_event, GameEvent):
                            next_event.trigger()
                
                if self.mob_loop_handler and self.mob_loop_handler.actions is not None:
                    if not self.mob_loop_handler.actions.empty():
                        next_action = self.mob_loop_handler.actions.get_nowait()

                    if next_action is not None and isinstance(next_action, GameAction):
                            next_action.perform()

            except BaseException as e:
                print(f"Error processing mob sub loop item: {e}")
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