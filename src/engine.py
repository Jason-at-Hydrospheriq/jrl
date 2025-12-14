#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from ai import GameAI
from state import GameState

class Engine:
    """
    The Engine updates the game state in the main loop. It is has States that it passes to the Game AI. 
    The GameAI converts states to a sequence of actions that the Engine performs in the main game loop.  
    """
    
    state: GameState
    # ai: GameAI

    def __init__(self) -> None:

        self.state = GameState()
        self.ai = GameAI(self.state)  

    # def render(self) -> None:
    #     """ Render all UI components """
    #     pass
        # for element in self.state.ui.elements:
        #     element.render()

    # def update(self) -> None:
    #     """
    #     Update the engine state
    #     """
    #     actions = self.ai.get_actions()
    #     for action in actions:
    #         action.perform()
