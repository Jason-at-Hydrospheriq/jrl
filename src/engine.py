#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine

from core_components.store import GameStore
from core_components.display import Display
from core_components.loop import GameLoop

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

        states = [{'name': 'idle', 'on_enter': '_initialize'}, 
                  {'name': 'playing', 'on_enter': '_play'},
                  {'name': 'paused', 'on_enter': '_pause'},
                  {'name': 'resuming', 'on_enter': '_play'},
                  {'name': 'shutdown', 'on_enter': '_shutdown'},
                  {'name': 'resetting', 'on_enter': '_reset'}]
        transitions =[
            {'trigger': 'start', 'source': 'shutdown', 'dest': 'idle'},
            {'trigger': 'play', 'source': 'idle', 'dest': 'playing'},
            {'trigger': 'pause', 'source': 'playing', 'dest': 'paused'},
            {'trigger': 'resume', 'source': 'paused', 'dest': 'resuming'},
            {'trigger': 'stop', 'source': 'idle', 'dest': 'shutdown'},
            {'trigger': 'stop', 'source': 'playing', 'dest': 'shutdown'},
            {'trigger': 'reset', 'source': 'shutdown', 'dest': 'resetting'},
            {'trigger': 'reset', 'source': 'playing', 'dest': 'resetting'},
            {'trigger': 'reset', 'source': 'idle', 'dest': 'resetting'},
            {'trigger': 'restart', 'source': 'resetting', 'dest': 'idle'},
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='shutdown')

    def _initialize(self) -> None:
        """Initializes the game state, including the portfolio, atlas, and display."""
        print("Initializing the game.")
        if self.display:
            self.display.start() # type: ignore
        if self.loop:
            self.loop.start() # type: ignore

        print(f"Game is {self.state}.") # type: ignore
    
    def _play(self) -> None:
        """Starts the main game loop, processing events and updating the game state."""
        print("Starting the game.")
        if self.store:
            self.store.start() # type: ignore
    
        print(f"Game is {self.state}.") # type: ignore

    def _pause(self) -> None:
        """Pauses the game loop, halting event processing and state updates."""
        print("Pausing the game.")
        if self.store:
            self.store.stop() # type: ignore

        print(f"Game is {self.state}.") # type: ignore

    def _shutdown(self) -> None:
        """Cleans up resources and stops the game loop."""
        print("Shutting down the game.")
        if self.loop:
            self.loop.stop() # type: ignore
        if self.display:
            self.display.stop() # type: ignore

        print(f"Game is {self.state}.") # type: ignore

    def _reset(self) -> None:
        """Resets the game state to its initial configuration."""
        print("Resetting the game.")
        self.store = GameStore()
        self.restart() # type: ignore
        self.play() # type: ignore
        
        print(f"Game is {self.state}.") # type: ignore
