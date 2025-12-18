#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import time
from typing import List, Set
import queue
from queue import Queue
import tcod
import threading

# from core_components import roster, atlas, ui
from core_components.events.library import BaseGameEvent, SystemEvent
from core_components.actions.base import BaseGameAction
from core_components.dispatchers.base import BaseEventDispatcher
from core_components.dispatchers.library import SystemDispatcher, InputDispatcher, EntityDispatcher
from core_components.events.library import *
from core_components.roster import Roster
from core_components.atlas import Atlas

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
    events: Queue[BaseGameEvent | tcod.event.Event]
    actions: Queue[BaseGameAction]
    dispatchers: List[BaseEventDispatcher]
    game_over: threading.Event

    def __init__(self) -> None:

        self.roster = Roster()
        self.map = Atlas()
        # self.ui = ui.UIDisplay()
        self.events = Queue()
        self.actions = Queue()
        self.game_over = threading.Event()
        self.dispatchers = [SystemDispatcher(), InputDispatcher(), EntityDispatcher()]   


    def dispatch(self) -> None:

        while True:
            try:
                event = self.events.get_nowait()

                for dispatcher in self.dispatchers:
                    dispatcher.dispatch(event, self.actions, self)
            
            except queue.Empty:
                time.sleep(0.05)
                
            except BaseException as e:
                print(f"Error dispatching event: {e}")
                break

    
    def update(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while True:
            try:
                action = self.actions.get_nowait()
                next_action = action.perform()
                if next_action is not None:
                    self.actions.put(next_action)
                        
            except queue.Empty:
                time.sleep(0.05)

    
