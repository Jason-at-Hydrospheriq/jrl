#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine

from engine_components import GameStore
from engine_components import GameDisplay
from engine_components  import GameAI
from protocols import StoredStateObject

class GameEngine:
    """
    The Game updates the game state in the main loop. It is has States that it passes to the Game AI. 
    The GameAI converts states to a sequence of actions that the Game performs in the main game loop.

    Duck Types: StatefulObject, StoredStateObject
    """
    machine: Machine
    ai: GameAI | None
    store: GameStore | None
    display: GameDisplay | None

    def __init__(self, ai: GameAI | None = None, display: GameDisplay | None = None, store: GameStore | None = None) -> None:
        self.ai = ai
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
            self.display = GameDisplay()
        if not self.ai:
            self.ai = GameAI()

        # Propagate the store to all StoredStateObjects
        stores = self._get_all_stores(self)
        for store in self._get_all_stores(self.store):
            stores.append(store)
            print(len(stores))
        
        for store in stores:
            store.store = self.store

        # Start components
        if self.store and self.store.state != 'initialized': # type: ignore
            self.store._initialize() # type: ignore
            self.store.start() # type: ignore
            #TODO connect mobloops to portfolio here
            
        if self.display and self.display.state != 'started': # type: ignore
            self.display.start() # type: ignore

        if self.ai and self.ai.state != 'started':  # type: ignore
            self.ai.start() # type: ignore

        print(f"Game is {self.state}.") # type: ignore
    
    def _play(self) -> None:
        """Starts the main game loop, processing events and updating the game state."""
        print("Starting the game.")
        if self.store and self.store.state != 'started': # type: ignore
            self.store.start() # type: ignore
        if self.ai and self.ai.state != 'started':  # type: ignore
            self.ai.start() # type: ignore
        self.store.portfolio.player.update_fov()  # type: ignore

    def _pause(self) -> None:
        """Pauses the game loop, halting event processing and state updates."""
        print("Pausing the game.")
        if self.store and self.store.state != 'stopped': # type: ignore
            self.store.stop() # type: ignore
        if self.ai and self.ai.state != 'paused':  # type: ignore
            self.ai.pause() # type: ignore

    def _shutdown(self) -> None:
        """Cleans up resources and stops the game loop."""
        print("Shutting down the game.")
        if self.store and self.store.state != 'stopped': # type: ignore
            self.store.stop() # type: ignore
        if self.ai and self.ai.state != 'stopped':  # type: ignore
            self.ai.stop() # type: ignore
        if self.display and self.display.state != 'stopped':  # type: ignore
            self.display.stop() # type: ignore

    def _reset(self) -> None:
        """Resets the game state to its initial configuration."""
        print("Resetting the game.")
        if self.store.log: # type: ignore 
            self.store.log.messages.clear()  # type: ignore 
        self.store.initialize()  # type: ignore | State machine attribute created dynamically
        self.play() # type: ignore | State machine attribute created dynamically
    
    def _get_store_components(self, obj: object) -> list[StoredStateObject]:
        try:
            found_stores = []
            for attribute in dir(obj):
                y = getattr(obj, attribute)
                if isinstance(y, StoredStateObject) and y.store is None:
                    found_stores.append(y)
            return found_stores
        
        except Exception as e:
            raise Exception(f"Error getting store components: {e}")
        
    def _get_all_stores(self, obj: object) -> list[StoredStateObject]:
        try:
            found_stores = []
            x = obj
            while self._get_store_components(x):   
                new_stores = self._get_store_components(x)
                for store in new_stores:
                    x = store
                    found_stores.append(x)
            
            return found_stores
        
        except Exception as e:
            raise Exception(f"Error getting all stores: {e}")