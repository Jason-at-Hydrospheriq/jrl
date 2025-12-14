#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from typing import Protocol, Set, Dict
from tcod.console import Console
import numpy as np


class BaseUI(Protocol):
    __slots__ = ("console", "widgets")
    
    console: Console
    widgets: Set[BaseUIWidget]
    states: Dict[str, np.ndarray]
    
    """ The UI Manager handles the various UI components and their interactions. """
    
    def __init__(self, console: Console | None = None) -> None:

        if console:
            self.console = console
        
        self.widgets = set()
        self.states = {}

    def add_element(self, element: BaseUIWidget, x: int = -1, y: int = -1) -> None:
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
        self.widgets.add(clone)
    
    def get_element_by_name(self, name: str) -> BaseUIWidget | None:
        """Retrieve a UI element by its name."""
        for element in self.widgets:
            if element.name == name:
                return element
        return None
    
    def get_elements_by_type(self, element_type: type) -> Set[BaseUIWidget]:
        """Retrieve all UI elements of a specific type."""
        return {element for element in self.widgets if isinstance(element, element_type)}

    def render(self) -> None:
        for widget in self.widgets:
            state_name = "state_" + widget.__class__.__name__.lower()
            state = self.states[state_name]
            widget.render(self.console, state)

        
class BaseUIWidget(Protocol):
    name: str
    upper_Left_x: int
    upper_Left_y: int
    lower_Right_x: int
    lower_Right_y: int
    width: int
    height: int

    def __init__(self, name: str, x: int, y: int, width: int, height: int, console: Console | None = None):
        self.name = name
        self.upper_Left_x = x
        self.upper_Left_y = y
        self.lower_Right_x = x + width
        self.lower_Right_y = y + height
        self.width = width
        self.height = height


    def render(self, console: Console, state: np.ndarray) -> None:
        """ Render the UI component """
        raise NotImplementedError()