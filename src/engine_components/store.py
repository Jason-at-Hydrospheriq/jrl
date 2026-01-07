#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine

from store_components import Portfolio
from store_components import Atlas
from display_components.widgets import MessageLog

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

        states = [{'name': 'initialized', 'on_enter': '_initialize'},
                  {'name': 'started', 'on_enter': '_start'}, 
                  {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'initialize', 'source': ['started', 'stopped'], 'dest': 'initialized'},
            {'trigger': 'start', 'source': ['initialized', 'stopped'], 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')
        
        self.log = MessageLog()
        
    def _initialize(self):
        """Starts the game loop and prepares the game state for play."""
        if self.atlas and self.portfolio:
            self._start()

            map = None
            if self.atlas is not None:
                self.atlas.create_map()
                map = self.atlas.active

            if self.portfolio and map is not None:
                self.portfolio.spawn_player(map)
                self.portfolio.initialize_random_mobs(map, max_mobs_per_area=3)

            self.log.add("Welcome to JRL - Jay's Roguelike!", fg=(255, 255, 0))

    def _start(self):
        pass

    def _stop(self):
        pass
