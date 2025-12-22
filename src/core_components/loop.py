#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine
import threading
from typing import TYPE_CHECKING, List
import time
import queue

from core_components.loops.handlers import GameLoopHandler
from core_components.loops.base import BaseGameEvent, BaseGameAction

if TYPE_CHECKING:
    from core_components.store import GameStore

class GameLoop:
    """
    The GameLoop manages the main game loop, processing events and actions in separate threads. It has a list of managed threads and provides an API for starting and stopping the loop. 
    It uses a GameLoopHandler to handle the transformation and dispatching of events and actions.

    Duck Types: StatefulObject
    """
    machine: Machine
    handler: GameLoopHandler | None
    threads: List[threading.Thread | None]
    stop_signal: threading.Event

    def __init__(self, store: GameStore | None = None) -> None:
        self.handler = GameLoopHandler(store=store) if store else GameLoopHandler()
        self.threads = []
        self.stop_signal = threading.Event()
        threading.excepthook = self.threaded_exception_handler

        states = ['idle', 
                  {'name': 'started', 'on_enter': '_start'}, 
                  {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

        self.threads.append(threading.Thread(target=self.event_loop))
        self.threads.append(threading.Thread(target=self.action_loop))

    def _start(self) -> None:
        """Starts the game loop threads."""
        self.stop_signal.clear()
        for thread in self.threads:
            if thread is not None and not thread.is_alive():
                thread.start()
        print("Game loop has started.")

    def _stop(self) -> None:
        """Stops the game loop threads."""
        try:
            self.stop_signal.set()
            for thread in self.threads:
                if thread is not None and not thread.is_alive():
                    thread.join()
            print("Game loop has stopped.")

        except Exception as e:
            print(f"Error stopping game loop: {e}")
            
    def action_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():
            try:
                next_action = None
                if self.handler and self.handler.actions is not None:
                    next_action = self.handler.actions.get_nowait()
                if next_action is not None and isinstance(next_action, BaseGameAction):
                    next_action.perform()
                
            except queue.Empty:
                time.sleep(0.05)

            except BaseException as e:
                print(f"Error processing action: {e}")
                break
    
    def event_loop(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while not self.stop_signal.is_set():
            try:
                next_event = None
                if self.handler and self.handler.events is not None:
                    next_event = self.handler.events.get_nowait()
                if next_event is not None and isinstance(next_event, BaseGameEvent):
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
