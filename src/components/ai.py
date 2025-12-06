from typing import TYPE_CHECKING

import tcod
from components.dispatch.input import InputDispatcher
from components.dispatch.interface import InterfaceDispatcher
from components.dispatch.gameover import GameOverDispatcher
from resources.events import UIEvent, GameOver

if TYPE_CHECKING:
    from engine import Engine
    
class GameAI:
    input_dispatcher: InputDispatcher
    interface_dispatcher: InterfaceDispatcher
    gameover_dispatcher: GameOverDispatcher

    def __init__(self) -> None:
        self.input_dispatcher = InputDispatcher()
        self.interface_dispatcher = InterfaceDispatcher()
        self.gameover_dispatcher = GameOverDispatcher()


    """ The Game AI is responsible for processing the game state and determining the actions of non-player characters (NPCs) in the game. """
    
    def get_actions(self, engine: Engine) -> list:
        action_sequence = []
        
        for event in tcod.event.wait():
            if engine.game_over:
                action_sequence = [self.gameover_dispatcher.dispatch(event)]
            else:
                action_sequence += [self.input_dispatcher.dispatch(event)]
        
        for event in engine.game_events:
            if isinstance(event, UIEvent):
                action_sequence += [self.interface_dispatcher.dispatch(event)]

            elif isinstance(event, GameOver):
                action_sequence = [self.gameover_dispatcher.dispatch(event)]

        return action_sequence