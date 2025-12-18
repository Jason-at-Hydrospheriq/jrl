#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import threading
from typing import List

from state import GameState

class Engine:
    """
    The Engine updates the game state in the main loop. It is has States that it passes to the Game AI. 
    The GameAI converts states to a sequence of actions that the Engine performs in the main game loop.  
    """

    state: GameState
    threads: List[threading.Thread | None]
    
    def __init__(self) -> None:
        self.state = GameState()
        self.threads = []

        # Convenience links to the game state
        self.atlas = self.state.map
        self.roster = self.state.roster

    # def render(self) -> None:
    #     """ Render all UI components """
    #     pass
        # for element in self.state.ui.elements:
        #     element.render()
    

    def start(self) -> None:
        self.threads.append(threading.Thread(target=self.state.dispatch).start())
        self.threads.append(threading.Thread(target=self.state.update).start())

        self.atlas.create_map()
        self.map = self.atlas.active

        if self.map is not None:
            self.state.roster.spawn_player(self.map)
            self.state.roster.initialize_random_mobs(self.map, max_mobs_per_area=3)
            self.player = self.state.roster.player
            self.mobs = self.state.roster.live_ai_actors

    def stop(self) -> None:
        self.state.game_over.set()
    
    def threaded_exception_handler(self, args):
        print(f"Thread failed: {args.thread.name}")
        print(f"Exception type: {args.exc_type}")
        print(f"Exception value: {args.exc_value}")
        print(f"Exception traceback: {args.exc_traceback}")
