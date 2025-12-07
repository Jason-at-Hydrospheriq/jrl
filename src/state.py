#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set

from components import roster, game_map, ui
from components.events.queues import MainEventQueue

class GameState:
    """
    The States class has a roster of entities, the game map, and the UI states. It is used by the Engine to pass the state of the entities, game map, and UI 
    to the GameAI. The GameAI returns a sequence of actions that the Engine then performs to update the state.  
    """
    
    roster: roster.Roster
    map: game_map.GameMap
    ui: ui.UIDisplay
    game_events: MainEventQueue
    game_over: bool = False

    def __init__(self) -> None:

        self.roster = roster.Roster()
        self.map = game_map.GameMap()
        self.ui = ui.UIDisplay()
        self.game_events = MainEventQueue()