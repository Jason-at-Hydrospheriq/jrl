#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine
import threading
from typing import List
from queue import Queue
import tcod
import time
import queue


class GameLoop:
    machine: Machine
    events: Queue[GameEvent | tcod.event.Event] | None
    actions: Queue[GameAction] | None
    handler: GameLoopHandler | None
    threads: List[threading.Thread | None]
    stop_signal: threading.Event

    def __init__(self) -> None:
        self.events = Queue()
        self.actions = Queue()
        self.handler = None
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
                if self.actions is not None:
                    next_action = self.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
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
                if self.events is not None:
                    next_event = self.events.get_nowait()
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
