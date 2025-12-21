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
from core_components.ai import GameAction, GameEvent, StateTransitionObject
from core_components.ai.handlers import Handler
from core_components.ai.events import *
from core_components.ui.graphics import colors
from core_components import Roster
from core_components import Atlas
from core_components import UIDisplay

class GameState:
    """
    The States class has a roster of entities, the game map, and the UI states. It is used by the Engine to pass the state of the entities, game map, and UI 
    to the GameAI. The GameAI returns a sequence of actions that the Engine then performs to update the state.  
    """
    # GAMESTART = GameStartEvent(message="Game has started!")
    # GAMEOVER = GameOverEvent(message="Game Over!")

    __slots__ = ("roster", "map","ui", "events", "actions", "handler", "game_over", "log")
    
    ui: UIDisplay
    events: Queue[StateTransitionObject]
    actions: Queue[StateTransitionObject]
    handler: Handler
    game_over: threading.Event
    roster: Roster
    map: Atlas  
    log: MessageLog

    def __init__(self) -> None:

        self.roster = Roster(state=self)
        self.map = Atlas(state=self)
        self.ui = UIDisplay()
        self.ui.state = self
        self.handler = Handler()
        self.events = Queue()
        self.actions = Queue()
        self.game_over = threading.Event()
        self.log = MessageLog()
        
    def handle(self) -> None:

        while True:
            try:

                next_event = self.events.get_nowait()
                if next_event is not None and isinstance(next_event, GameEvent):
                    next_event.trigger()
            
            except queue.Empty:
                time.sleep(0.05)
                
            except BaseException as e:
                print(f"Error dispatching event: {e}")
                break
    
    def dispatch(self) -> None:
        """
        Update the state of the game by processing events and updating the roster, map, and UI.
        """
        while True:
            try:
                next_action = self.actions.get_nowait()
                if next_action is not None and isinstance(next_action, GameAction):
                    next_action.perform()
                
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
