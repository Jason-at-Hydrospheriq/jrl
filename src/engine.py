#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set

from components import roster, game_map, ui, ai
from resources.events import BaseGameEvent

class Engine:
    """
    The Engine updates the game state in the main loop. It is has a roster of entities, the game map, the UI manager, and the AI manager. It passes the state of the entities, game map, and UI 
    to the AI manager. The AI Manager returns a sequence of actions that the Engine then performs to update the state.  
    """

    roster: roster.Roster
    game_map: game_map.GameMap
    ui: ui.UIDisplay
    ai: ai.GameAI
    game_events: Set[BaseGameEvent]
    game_over: bool = False

    def __init__(self, roster: roster.Roster, game_map: game_map.GameMap, ui: ui.UIDisplay, ai: ai.GameAI) -> None:
        self.roster = roster
        self.game_map = game_map
        self.ui = ui
        self.ai = ai
        self.game_events = set()

    def update(self) -> None:
        """
        Update the engine state
        """
        actions = self.ai.get_actions(self)
        for action in actions:
            action.perform()
