from typing import Dict, Set, TYPE_CHECKING
from tcod.context import Context
import numpy as np

from core_components.interfaces.base import BaseUI, BaseUIWidget, UIManifestDict
from core_components.interfaces.library import HealthBarWidget, MainMapDisplay
from copy import deepcopy
from core_components.tiles.base import TileTuple
from core_components.maps.library import DEFAULT_MANIFEST

if TYPE_CHECKING:
    from state import GameState

DEFAULT_UI_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'main_map': {
                            'cls': MainMapDisplay,
                            'x': 1,
                            'y': 1,
                            'width': DEFAULT_MANIFEST['dimensions']['grid_size'][0][0],
                            'height': DEFAULT_MANIFEST['dimensions']['grid_size'][1][0]},
                        'player_health_bar': {
                            'cls': HealthBarWidget,
                            'x': 5,
                            'y': DEFAULT_MANIFEST['dimensions']['grid_size'][1][0] + 2,
                            'width': 20,
                            'height': 1
                        },

    }}


class UIDisplay(BaseUI):
    
    """ The UI Manager handles the various UI components and their interactions. """

    def __init__(self, context: Context | None = None, ui_manifest: UIManifestDict | None = DEFAULT_UI_MANIFEST) -> None:
        super().__init__(context=context, ui_manifest=ui_manifest)  
