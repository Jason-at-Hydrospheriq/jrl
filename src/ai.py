from queue import Queue
import threading
from typing import TYPE_CHECKING, List
import tcod

from core_components.dispatchers.base import BaseEventDispatcher
from core_components.events.library import BaseGameEvent, UIEvent, SystemEvent
from core_components.dispatchers.library import InputDispatcher, InterfaceDispatcher, SystemDispatcher
from core_components.actions.library import BaseGameAction, NoAction
from core_components.state import GameState
    
def is_subclass(instance, cls: type) -> bool:
    instance_mro = set([x.__name__ for x in instance.__class__.mro()])
    cls_mro = set([x.__name__ for x in cls.mro()])
    return instance_mro.issuperset(cls_mro)

class GameAI:
    """ The Game AI is responsible for processing the game state and determining the actions of non-player characters (NPCs) in the game. In this implementation,
    it is an eventhandler that processes events and dispatches actions based on the game state. The game state is updated in the main loop by the game engine.
    The GameAI processes events from an event message queue to function specific dispatchers. The Dispatchers convert events to actions which the GameAI compiles into
    an action queue. On each pass, the GameEngine executes the actions in the action queue. Future implementations of the GameAI will include more sophisticated 
    algorithms for processing game states, events, and actions.
    """
    state: GameState
    dispatchers: List[BaseEventDispatcher]
    actions: Queue[BaseGameAction]
    
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.dispatchers = [SystemDispatcher()]
        self.actions = Queue()    

    def update_actions(self) -> None:
        for dispatcher in self.dispatchers:
            threading.Thread(target=dispatcher.dispatch, args=(self.state.events, self.actions, self.state), daemon=True).start()
        
        threading.Thread(target=self.state.update_state, args=(self.actions,), daemon=True).start()

        self.state.events.join()
        self.actions.join()
