#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set

from core_components import roster, atlas, ui
from core_components.queues.library import MainEventQueue

class GameState:
    """
    The States class has a roster of entities, the game map, and the UI states. It is used by the Engine to pass the state of the entities, game map, and UI 
    to the GameAI. The GameAI returns a sequence of actions that the Engine then performs to update the state.  
    """
    
    roster: roster.Roster
    map: atlas.Atlas
    ui: ui.UIDisplay
    game_events: MainEventQueue
    game_over: bool = False

    def __init__(self) -> None:

        self.roster = roster.Roster()
        self.map = atlas.Atlas()
        self.ui = ui.UIDisplay()
        
        self.game_events = MainEventQueue()