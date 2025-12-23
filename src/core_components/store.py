#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Tuple
from transitions import Machine

# from core_components import portfolio, atlas, ui

from core_components import Portfolio
from core_components import Atlas
from core_components.widgets.interfaces.library import MessageLog

class GameStore:
    """
    The Game Store class has a portfolio of Game Assets and an Atlas of Game Maps. It is the object used to pass game state information
    between the game components.

    Duck Types: StatefulObject  
    """
    machine: Machine
    portfolio: Portfolio | None
    atlas: Atlas | None
    log: MessageLog

    def __init__(self) -> None:
        self.portfolio = Portfolio(store=self)
        self.atlas = Atlas(store=self)

        states = ['idle', 
                  {'name': 'started', 'on_enter': '_start'}, 
                  {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')
        
        self.log = MessageLog()
        
    def _start(self):
        """Starts the game loop and prepares the game state for play."""

        if self.atlas is not None:
            self.atlas.create_map()
            self.map = self.atlas.active

        if self.portfolio and self.map is not None:
            self.portfolio.spawn_player(self.map)
            self.portfolio.initialize_random_mobs(self.map, max_mobs_per_area=3)
            self.player = self.portfolio.player
            if self.player is not None:
                self.player.fov_radius = 6
            self.mobs = self.portfolio.live_ai_actors

        self.log.add("Welcome to JRL - Jay's Roguelike!", fg=(255, 255, 0))

        print(f"Game Store is {self.state}.") # type: ignore

    def _stop(self):
        """Handles any cleanup or finalization needed when the game stops."""
        # if self.atlas is not None:
        #     self.atlas.stop() # type: ignore
        # if self.portfolio is not None:
        #     self.portfolio.stop() # type: ignore
        print(f"Game Store is {self.state}.") # type: ignore

        # self.portfolio = None
        # self.atlas = None
        # self.loop.stop.set() # Confirm all threads terminate. 
