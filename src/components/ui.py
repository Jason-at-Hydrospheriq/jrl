from typing import Set, TYPE_CHECKING
from tcod.console import Console

if TYPE_CHECKING:
    from engine import Engine

from components.display.base import BaseUIComponent
from components.display.maps import MainMapDisplay
from copy import deepcopy

MAP = MainMapDisplay("main_map", 5, 5, 80, 45)

class UIDisplay:

    __slots__ = ("console", "elements")
    
    console: Console
    elements: Set[BaseUIComponent]

    """ The UI Manager handles the various UI components and their interactions. """
    
    def __init__(self, console: Console) -> None:
        self.console = console
        self.add_element(MAP)

    def add_element(self, element: BaseUIComponent, x: int = -1, y: int = -1) -> None:
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(element)
        if x == -1:
            x = element.upper_Left_x
        if y == -1:
            y = element.upper_Left_y
        clone.upper_Left_x = x
        clone.upper_Left_y = y
        clone.lower_Right_x = x + element.width
        clone.lower_Right_y = y + element.height
        self.elements.add(clone)
    
    def get_element_by_name(self, name: str) -> BaseUIComponent | None:
        """Retrieve a UI element by its name."""
        for element in self.elements:
            if element.name == name:
                return element
        return None
    
    def get_elements_by_type(self, element_type: type) -> Set[BaseUIComponent]:
        """Retrieve all UI elements of a specific type."""
        return {element for element in self.elements if isinstance(element, element_type)}
    
    def render(self, engine: Engine) -> None:
        """ Render all UI components """
        for element in self.elements:
            element.render(engine)