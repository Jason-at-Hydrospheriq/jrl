from queue import Queue
import threading
from typing import TYPE_CHECKING, List
import tcod

from core_components.dispatchers.base import BaseEventDispatcher
from core_components.events.library import BaseGameEvent, UIEvent, SystemEvent
from core_components.dispatchers.library import InputDispatcher, InterfaceDispatcher, SystemDispatcher
from core_components.actions.library import BaseGameAction, NoAction
from core_components.state import GameState


class GameAI:
    """ The Game AI is responsible for processing the game state and determining the actions of non-player characters (NPCs) in the game. In this implementation,
    it is an eventhandler that processes events and dispatches actions based on the game state. The game state is updated in the main loop by the game engine.
    The GameAI processes events from an event message queue to function specific dispatchers. The Dispatchers convert events to actions which the GameAI compiles into
    an action queue. On each pass, the GameEngine executes the actions in the action queue. Future implementations of the GameAI will include more sophisticated 
    algorithms for processing game states, events, and actions.
    """
    state: GameState
    
