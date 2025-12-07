from typing import List, Set
import tcod

from components.queues.event_lib import BaseGameEvent, UIEvent, SystemEvent
from components.dispatchers.event_to_action import InputDispatcher, InterfaceDispatcher, SystemDispatcher
from components.state import GameState
    
def is_subclass(instance, cls: type) -> bool:
    instance_mro = set([x.__name__ for x in instance.__class__.mro()])
    cls_mro = set([x.__name__ for x in cls.mro()])
    return instance_mro.issuperset(cls_mro)

class GameAI:
    """ The Game AI is responsible for processing the game state and determining the actions of non-player characters (NPCs) in the game. """
    state: GameState
    input_dispatcher: InputDispatcher
    interface_dispatcher: InterfaceDispatcher
    system_dispatcher: SystemDispatcher
    
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.input_dispatcher = InputDispatcher(state)
        self.interface_dispatcher = InterfaceDispatcher(state)
        self.system_dispatcher = SystemDispatcher(state)

    def get_actions(self) -> List:
        action_sequence = []
        
        for event in tcod.event.wait():
            if self.state.game_over:
                action_sequence = [self.system_dispatcher.dispatch(event)]
            else:
                action_sequence += [self.input_dispatcher.dispatch(event)]
        
        while not self.state.game_events.is_empty():
            event = self.state.game_events.get()

            if self.state.game_over:
                action_sequence = self.system_dispatcher.dispatch(event)

            else:
                if is_subclass(event, UIEvent):
                    action_sequence += self.interface_dispatcher.dispatch(event)

                if is_subclass(event, SystemEvent):
                    action_sequence += self.system_dispatcher.dispatch(event)

        return action_sequence