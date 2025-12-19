#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import time
from typing import List, Tuple
import queue
from queue import Queue
import tcod
import threading

# from core_components import roster, atlas, ui
from core_components.actions.library import GeneralAction
from core_components.events.library import BaseGameEvent
from core_components.graphics import colors
from core_components.actions.base import BaseGameAction
from core_components.dispatchers.base import BaseEventDispatcher
from core_components.dispatchers.library import SystemDispatcher, InputDispatcher, AIDispatcher
from core_components.events.library import *
from core_components.roster import Roster
from core_components.atlas import Atlas
from core_components.ui import UIDisplay

class GameState:
    """
    The States class has a roster of entities, the game map, and the UI states. It is used by the Engine to pass the state of the entities, game map, and UI 
    to the GameAI. The GameAI returns a sequence of actions that the Engine then performs to update the state.  
    """
    GAMESTART = GameStartEvent(message="Game has started!")
    GAMEOVER = GameOverEvent(message="Game Over!")

    __slots__ = ("roster", "map","ui", "events", "actions", "dispatchers", "game_over", "log")
    
    ui: UIDisplay
    events: Queue[BaseGameEvent | tcod.event.Event]
    actions: Queue[GeneralAction]
    dispatchers: List[BaseEventDispatcher]
    game_over: threading.Event
    roster: Roster
    map: Atlas  
    log: MessageLog

    def __init__(self) -> None:

        self.roster = Roster(state=self)
        self.map = Atlas(state=self)
        self.ui = UIDisplay()
        self.ui.state = self
        
        self.events = Queue()
        self.actions = Queue()
        self.game_over = threading.Event()
        self.dispatchers = [SystemDispatcher(), InputDispatcher(), AIDispatcher()]   
        self.log = MessageLog()
        
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

                self.events.put(FOVUpdateEvent(""))

                for entity in self.roster.live_ai_actors:
                    if entity:  
                        entity.ai.update_state() # type: ignore
                
            except queue.Empty:
                time.sleep(0.05)


class Message:
    """ A single message for the message log. """
    def __init__(self, text: str, fg: Tuple[int, int, int] = colors.white) -> None:
        self.plain_text = text
        self.fg= fg
        self.count = 1
        if self.count > 1:
            self.text = f"{self.plain_text} (x{self.count})"


class MessageLog:
    """ A simple message log widget to display game messages. """
    def __init__(self) -> None:
        self.messages: list[Message] = []
        
    def add(self, text: str, fg: Tuple[int, int, int] = colors.white, stack: bool = True) -> None:
        """Add a message to this log.
        `text` is the message text, `fg` is the text color.
        If `stack` is True then the message can stack with a previous message
        of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))    
