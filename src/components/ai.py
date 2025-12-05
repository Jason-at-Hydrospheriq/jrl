from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    
class AIManager:
    """ The AI Manager is responsible for processing the game state and determining the actions of non-player characters (NPCs) in the game. """
    
    def decide_actions(self, engine: Engine) -> list:
        """
        Decide actions for all NPCs based on the current game state provided by the Engine.
        """
        actions = []
        # AI logic to determine actions goes here
        return actions