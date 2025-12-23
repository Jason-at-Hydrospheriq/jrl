#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine

from core_components.store import GameStore
from core_components.display import Display
from core_components.loop import GameLoop
from type_protocols import StateStoreObject

class GameEngine:
    """
    The Game updates the game state in the main loop. It is has States that it passes to the Game AI. 
    The GameAI converts states to a sequence of actions that the Game performs in the main game loop.

    Duck Types: StatefulObject, StateReferenceObject
    """
    machine: Machine
    loop: GameLoop | None
    store: GameStore | None
    display: Display | None

    def __init__(self, loop: GameLoop | None = None, display: Display | None = None, store: GameStore | None = None) -> None:
        self.loop = loop
        self.display = display
        self.store = store

        states = [{'name': 'idle', 'on_exit': '_play'}, 
                  {'name': 'playing'},
                  {'name': 'paused', 'on_enter': '_pause', 'on_exit': '_play'},
                  {'name': 'shutdown', 'on_enter': '_shutdown', 'on_exit': '_initialize'},
                  ]
        transitions =[
            {'trigger': 'start', 'source': 'shutdown', 'dest': 'idle'},
            {'trigger': 'play', 'source': 'idle', 'dest': 'playing'},
            {'trigger': 'play', 'source': 'paused', 'dest': 'playing'},
            {'trigger': 'pause', 'source': 'playing', 'dest': 'paused'},
            {'trigger': 'stop', 'source': 'idle', 'dest': 'shutdown'},
            {'trigger': 'stop', 'source': 'playing', 'dest': 'shutdown'},
            {'trigger': 'reset', 'source': 'playing', 'dest': 'idle', 'after': '_reset'},
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='shutdown')

    def _initialize(self) -> None:
        """Initializes the game state, including the portfolio, atlas, and display."""
        print("Initializing the game.")
        if not self.store:
            self.store = GameStore()
        if not self.display:
            self.display = Display()
        if not self.loop:
            self.loop = GameLoop()

        stores = []
        x = self

        while self._get_store_components(x):   
            new_stores = self._get_store_components(x)
            for store in new_stores:
                x = store
                stores.append(x)

        for store in stores:
            store.store = self.store

        if self.display and self.display.state != 'started': # type: ignore
            self.display.start() # type: ignore

        if self.loop and self.loop.state != 'started':  # type: ignore
            self.loop.start() # type: ignore

        print(f"Game is {self.state}.") # type: ignore
    
    def _play(self) -> None:
        """Starts the main game loop, processing events and updating the game state."""
        print("Starting the game.")
        if self.store and self.store.state != 'started': # type: ignore
            self.store.start() # type: ignore
        if self.loop and self.loop.state != 'started':  # type: ignore
            self.loop.start() # type: ignore

        print(f"Game is {self.state}.") # type: ignore

    def _pause(self) -> None:
        """Pauses the game loop, halting event processing and state updates."""
        print("Pausing the game.")
        if self.store and self.store.state != 'stopped': # type: ignore
            self.store.stop() # type: ignore
        if self.loop and self.loop.state != 'paused':  # type: ignore
            self.loop.pause() # type: ignore

        print(f"Game is {self.state}.") # type: ignore

    def _shutdown(self) -> None:
        """Cleans up resources and stops the game loop."""
        print("Shutting down the game.")
        if self.store and self.store.state != 'stopped': # type: ignore
            self.store.stop() # type: ignore
        if self.loop and self.loop.state != 'stopped':  # type: ignore
            self.loop.stop() # type: ignore
        if self.display and self.display.state != 'stopped':  # type: ignore
            self.display.stop() # type: ignore

        print(f"Game is {self.state}.") # type: ignore

    def _reset(self) -> None:
        """Resets the game state to its initial configuration."""
        print("Resetting the game.")
        self._initialize()
        self.play() # type: ignore

        print(f"Game is {self.state}.") # type: ignore
    
    def _get_store_components(self, obj: object) -> list[StateStoreObject]:
        found_stores = []
        for attribute in dir(obj):
            y = getattr(obj, attribute)
            if isinstance(y, StateStoreObject):
                found_stores.append(y)
        return found_stores

