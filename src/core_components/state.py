#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set
from queue import Queue

# from core_components import roster, atlas, ui
from core_components.actions.base import BaseGameAction
from core_components.events.library import *

class GameState:
    """
    The States class has a roster of entities, the game map, and the UI states. It is used by the Engine to pass the state of the entities, game map, and UI 
    to the GameAI. The GameAI returns a sequence of actions that the Engine then performs to update the state.  
    """
    GAMESTART = GameStartEvent(message="Game has started!")
    GAMEOVER = GameOverEvent(message="Game Over!")

    # MAPUPDATE = MapUpdateEvent()
    # roster: roster.Roster
    # map: atlas.Atlas
    # ui: ui.UIDisplay
    events: Queue[BaseGameEvent]
    game_over: bool 

    def __init__(self) -> None:

        # self.roster = roster.Roster()
        # self.map = atlas.Atlas()
        # self.ui = ui.UIDisplay()
        self.events = Queue()
        self.events.put(self.GAMESTART)
        self.game_over = True
    
    def update_state(self, actions_q: Queue[BaseGameAction]) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while True:
            try:
                action = actions_q.get()
                action.perform()
                print(f"Action performed: {action}")
                actions_q.task_done()
                
            except:
                break
            
        self.events.queue.clear()