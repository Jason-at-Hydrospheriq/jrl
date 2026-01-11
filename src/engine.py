#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine

from store import GameStore
from display import GameDisplay, colors
from loop  import GameLoops
from game_types import StoredStateObject

class GameEngine:
    """
    The Game updates the game state in the main loop. It is has States that it passes to the Game AI. 
    The GameAI converts states to a sequence of actions that the Game performs in the main game loop.

    Duck Types: StatefulObject, StoredStateObject
    """
    machine: Machine
    loop: GameLoops | None
    store: GameStore | None
    display: GameDisplay | None

    def __init__(self, ai: GameLoops | None = None, display: GameDisplay | None = None, store: GameStore | None = None) -> None:
        self.loop = ai
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

        # Provision Engine Components
        self.store = GameStore()
        self.display = GameDisplay(store=self.store)
        self.loop = GameLoops(store=self.store)

        # Set GameAI for Portfolio spawing
        if self.store and self.loop and self.store.portfolio:
            self.store.portfolio.game_ai = self.loop

        # Set Display for GameAI
        if self.loop and self.display:
            self.loop.display = self.display

        # Propagate the store to all StoredStateObjects
        stores = self._get_all_stores(self)
        for store in self._get_all_stores(self.store):
            stores.append(store)
            print(len(stores))   
        for store in stores:
            store = self.store

        # Initialize Maps and Entities in the GameStore
        if self.store and self.store.state != 'initialized': # type: ignore | State machine attribute created dynamically
            self.store.initialize() # type: ignore | State machine attribute created dynamically
            self.store.log.add("Welcome to JRL - Jay's Roguelike!", fg=colors.welcome_text)  # type: ignore
            self.store.log.add("Press P to Play/Pause, ESC to Reset, and Q to Quit.", fg=colors.welcome_text)  # type: ignore

        # Start Display
        if self.display and self.display.state != 'started':  # type: ignore | State machine attribute created dynamically
            self.display.start() # type: ignore | State machine attribute created dynamically

        # Start Game Loop
        if self.loop and self.loop.state != 'started':  # type: ignore | State machine attribute created dynamically
            self.loop.start() # type: ignore | State machine attribute created dynamically
            self.loop.pause()  # type: ignore | State machine attribute created dynamically

        print(f"Game is {self.state}.") # type: ignore
    
    def _play(self) -> None:
        """Starts the main game loop, processing events and updating the game state."""
        print("Starting the game.")
        if self.store and self.store.state != 'started': # type: ignore | State machine attribute created dynamically
            self.store.start() # type: ignore | State machine attribute created dynamically
        if self.loop and self.loop.state != 'started':  # type: ignore | State machine attribute created dynamically
            self.loop.start() # type: ignore | State machine attribute created dynamically
        if self.store and self.store.portfolio and self.store.portfolio.player:
            self.store.portfolio.player.update_fov()  # type: ignore | The class for this action must be PlayerCharacter.

    def _pause(self) -> None:
        """Pauses the game loop, halting event processing and state updates."""
        print("Pausing the game.")
        if self.store and self.store.state != 'stopped': # type: ignore | State machine attribute created dynamically
            self.store.stop() # type: ignore | State machine attribute created dynamically
        if self.loop and self.loop.state != 'paused':  # type: ignore | State machine attribute created dynamically
            self.loop.pause() # type: ignore | State machine attribute created dynamically

    def _shutdown(self) -> None:
        """Cleans up resources and stops the game loop."""
        print("Shutting down the game.")
        if self.store and self.store.state != 'stopped': # type: ignore | State machine attribute created dynamically
            self.store.stop() # type: ignore | State machine attribute created dynamically
        if self.loop and self.loop.state != 'stopped':  # type: ignore | State machine attribute created dynamically
            self.loop.stop() # type: ignore | State machine attribute created dynamically
        if self.display and self.display.state != 'stopped':  # type: ignore | State machine attribute created dynamically
            self.display.stop() # type: ignore | State machine attribute created dynamically

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
        