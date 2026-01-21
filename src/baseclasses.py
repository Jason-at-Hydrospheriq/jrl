#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from functools import wraps
from typing import TYPE_CHECKING, Dict, Set, Tuple
from transitions import Machine
import numpy as np
import tcod
from tcod.console import Console
from tcod.context import Context
from enum import Enum, auto

import colors
from manifests import DEFAULT_TILEMAP_MANIFEST
from game_types import StateHandler, StatefulObject, TileCoordinate, TileTuple, UIManifestDict

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


def is_locked(func):
    """A decorator to wrap each method with a condition check."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Access the condition from the instance (self)
        if self.action_locked:
            return None # Or raise an exception, or handle as needed
        return func(self, *args, **kwargs)
    return wrapper


def action_locked(cls):
    """A class decorator to apply the condition_checker to all methods."""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith('__'):
            # Wrap the method with the condition checker
            setattr(cls, attr_name, is_locked(attr_value))

        if isinstance(attr_value, property):
            if attr_value.fset:
                # Wrap the setter method of the property
                setter = attr_value.fset
                if setter and callable(setter):
                    wrapped_setter = is_locked(setter)
                else:
                    wrapped_setter = setter

                # Create a new property with the wrapped methods
                new_property = property(attr_value.fget, wrapped_setter)
                setattr(cls, attr_name, new_property)

    return cls


class EntityRenderOrder(Enum):
     CORPSE = auto()
     ITEM = auto()
     CHARACTER = auto()


class WidgetRenderOrder(Enum):
    BACKGROUND = auto()
    FOREGROUND = auto()


class BaseUIWidget:
    name: str
    upper_Left_x: int
    upper_Left_y: int
    lower_Right_x: int
    lower_Right_y: int
    width: int
    height: int
    render_order: WidgetRenderOrder

    def __init__(self, name: str, x: int, y: int, width: int, height: int, render_order: WidgetRenderOrder) -> None:
        self.name = name
        self.upper_Left_x = x
        self.upper_Left_y = y
        self.lower_Right_x = x + width
        self.lower_Right_y = y + height
        self.width = width
        self.height = height
        self.render_order = render_order

    def render(self, context: Context, console: Console, store: GameStore) -> None:
        """ Render the UI component """
        raise NotImplementedError()


class BaseUIWindow:
    name: str
    context: Context | None
    console: Console | None
    store: GameStore | None
    width: int
    height: int
    widgets: Set[BaseUIWidget]
    overlay_x: int
    overlay_y: int
    is_rendered: bool = False
    is_overlay: bool = False

    def __init__(self, name: str, store: GameStore | None = None, context: Context | None = None, width: int = 80, height: int = 50, 
                 overlay_x: int = 1, overlay_y: int = 1, widget_manifest: UIManifestDict | None = None, is_rendered: bool = False, 
                 is_overlay: bool = False) -> None:
        
        self.name = name
        
        if context is not None:
            self.context = context
        
        if store is not None:
            self.store = store

        self.console = None
        self.widgets = set()
        self.width = width
        self.height = height
        self.overlay_x = overlay_x
        self.overlay_y = overlay_y
        self.is_rendered = is_rendered
        self.is_overlay = is_overlay

        if widget_manifest is not None:

            for widget_name, widget_info in widget_manifest['widgets'].items():
                widget_cls = widget_info['cls']
                x = widget_info.get('x', 0)
                y = widget_info.get('y', 0)
                width = widget_info.get('width', 10)
                height = widget_info.get('height', 5)
                render_order = widget_info.get('render_order', WidgetRenderOrder.BACKGROUND)
                widget = widget_cls(widget_name, upper_Left_x=x, upper_Left_y=y, width=width, height=height, render_order=render_order)
                self.add_widget(widget=widget, x=x, y=y)

            self.widgets = set(sorted(self.widgets, key=lambda w: w.render_order.value))

    def add_widget(self, *, widget: BaseUIWidget, x: int = -1, y: int = -1) -> None:
        """Add a widget to the UI window at the given location."""
        widget.upper_Left_x = x
        widget.upper_Left_y = y
        widget.lower_Right_x = x + widget.width
        widget.lower_Right_y = y + widget.height
        self.widgets.add(widget)

    def drop_widget(self, *, name: str) -> None:
        """Remove a widget by its name."""
        widget_to_remove = None
        for widget in self.widgets:
            if widget.name == name:
                widget_to_remove = widget
                break
        if widget_to_remove:
            self.widgets.remove(widget_to_remove)

    def get_widget_by_name(self, name: str) -> BaseUIWidget | None:
        """Retrieve a widget by its name."""
        for widget in self.widgets:
            if widget.name == name:
                return widget
        return None

    def get_widgets_by_type(self, widget_type: type) -> Set[BaseUIWidget]:
        """Retrieve all widgets of a specific type."""
        return {widget for widget in self.widgets if isinstance(widget, widget_type)}

    def render(self) -> None:
        if self.is_rendered and self.context and self.store:
            if self.context.sdl_window is not None:
                self.console = self.context.new_console(self.width, self.height, order="F")
                sorted_widgets = sorted(self.widgets, key=lambda w: w.render_order.value)
                for widget in sorted_widgets:
                    widget.render(self.context, self.console, self.store)


class BaseUI:
    store: GameStore | None
    machine: Machine
    context: Context | None
    ai: SubLoopHandler | None
    windows: Set[BaseUIWindow]
    context_width: int
    context_height: int

    """ The UI Manager handles the various UI components and their interactions. """

    def __init__(self, context: Context | None = None, store: GameStore | None = None, ui_manifest: UIManifestDict | None = None, *, context_width: int = 80, context_height: int = 50) -> None:

        if context is not None:
            self.context = context

        if store is not None:
            self.store = store

        self.windows = set()
        self.context_width = context_width
        self.context_height = context_height

        states = ['idle',
                    {'name': 'started', 'on_enter': '_start'},
                    {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

    def _start(self) -> None:
        ...

    def _stop(self) -> None:
        ...

    def add_window(self, window: BaseUIWindow) -> None:
        """Spawn a copy of this entity at the given location."""
        self.windows.add(window)

    def remove_window(self, *, name: str) -> None:
        """Remove a UI element by its name."""
        window_to_remove = None
        for window in self.windows:
            if window.name == name:
                window_to_remove = window
                break   
        if window_to_remove:
            self.windows.remove(window_to_remove)

    def get_window_by_name(self, name: str) -> BaseUIWindow | None:
        """Retrieve a UI element by its name."""
        for window in self.windows:
            if window.name == name:
                return window
        return None

    def get_windows_by_type(self, window_type: type) -> Set[BaseUIWindow]:
        """Retrieve all UI elements of a specific type."""
        return {window for window in self.windows if isinstance(window, window_type)}

    def process_event(self, input_event: tcod.event.Event) -> None:
        raise NotImplementedError()
        
    def render(self) -> None:
        if self.context and self.store:
            main_window = self.get_window_by_name('main_window')
            if self.context.sdl_window and main_window and main_window.console:
                main_window.render()
                for window in self.windows:
                    if window != main_window and window.is_rendered and window.console:
                        window.render()
                        if window.is_overlay:
                            window.console.blit(main_window.console, window.overlay_x, window.overlay_y)
                self.context.present(main_window.console)
                # for window in self.windows:
                #     if window.console:
                #         window.console.clear()


class BaseSubState:
    machine: Machine
    name: str
    store: StatefulObject

    # Set defaults in subclasses
    _state_bits: Tuple[str, ...]
    _states: Tuple[Dict, ...]
    _transitions: Tuple[Dict, ...]
    _initial_state: str

    def __init__(self, name: str, store: StatefulObject):
        self.name = name
        self.store = store

        machine = Machine(model=self, states=self._states, transitions=self._transitions, initial=self._initial_state)
        self.machine = machine

    def set_bits(self) -> None:
        pass # Define in subclasses


class BaseParentState:
    machine: Machine
    substates: list[BaseSubState]
    state_vector: Dict[str, bool]
    state_vector_dtype: np.dtype
    # Define in subclasses
    _substates_manifest: Tuple[Tuple[str, type[BaseSubState]], ...]

    def __init__(self):
        self.substates = []
        self.state_vector = {}
        self.machine = Machine(model=self, states=[], transitions=[])

        for name, substate in self._substates_manifest:
            self._add_substate(substate(name=name, store=self))

    def update(self) -> None:
        for substate in self.substates:
            try:
                substate.set_bits()
                substate.update() # type: ignore

            except Exception as e:
                raise e

    def _add_substate(self, substate: BaseSubState) -> None:
        self.substates.append(substate)
        for bit in substate._state_bits:
            self.state_vector[bit] = False
        self.__setattr__(substate.name.lower(), substate) #type: ignore


class BaseGameSubState(BaseSubState):
    """
    A generic substate for game entity_components

    Duck Types: EntitySubState, BaseSubState
    """
    _state_bits = ('on_map',)
    _states = ({'name': 'in_play'},
               {'name': 'not_in_play'})
    _transitions = (
        {'trigger':'update', 'source':'not_in_play', 'dest':'in_play', 'conditions':['is_on_map']},
        {'trigger':'update', 'source':'in_play', 'dest':'not_in_play', 'conditions':['is_not_on_map']})
    _initial_state = 'not_in_play'

    def set_bits(self) -> None:
        self.store.state_vector['on_map'] = self.store.location is not None #type: ignore

    # All substates must have the primary state bit methods
    def is_on_map(self) -> bool:
        return self.store.state_vector['on_map'] # type: ignore

    def is_not_on_map(self) -> bool:
        return not self.store.state_vector['on_map'] # type: ignore


@action_locked
class BaseGameEntity(BaseParentState):
    """
    A generic object to represent players, enemies, items, etc.

    Duck Types: StatefulObject, StateStoreObject, GameEntity, BaseParentState
    """
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None
    is_invulnerable: bool | None
    action_locked: bool | None
    _hp: int | None
    _max_hp: int | None
    name: str
    symbol: str
    color: Tuple[int, int, int] # Do this like the maps. Numpy datatypes mapped to state.
    render_order: EntityRenderOrder

    # Substate definition
    _substates_manifest = (
        ("spawn", BaseGameSubState),
    )

    def __init__(self,
                 store: GameStore | None = None,
                 *,
                 location: TileCoordinate | None = None,
                 name: str="<Unnamed>",
                 symbol: str=' ',
                 color: Tuple[int, int, int]=(0,0,0), 
                 render_order: EntityRenderOrder=EntityRenderOrder.CORPSE) -> None:
        super().__init__()

        self.store = store
        parent_map_size = TileTuple(([100], [100]))

        if self.store:
            parent_map_size = self.store.atlas.active.grid.size  # type: ignore

        if not hasattr(self, 'location'):
            self.location = location

        if not hasattr(self, 'symbol'):
            self.symbol = symbol

        if not hasattr(self, 'color'):
            self.color = color

        if not hasattr(self, 'name'):
            self.name = name

        if not hasattr(self, 'render_order'):
            self.render_order = render_order

        self.blocks_movement = True
        self.is_invulnerable = False
        self._hp = 0
        self._max_hp = 1
        self.action_locked = False

        self.update()

    @property
    def hp(self) -> int | None:
        if not self.is_invulnerable:
            return self._hp
        return None

    @hp.setter
    def hp(self, value: int | None) -> None:
        if not self.is_invulnerable:
            self._hp = value
            self.update()

    @property
    def max_hp(self) -> int | None:
        if not self.is_invulnerable:
            return self._max_hp
        return None

    @max_hp.setter
    def max_hp(self, value: int | None) -> None:
        if not self.is_invulnerable:
            self._max_hp = value
            self.update()


class BaseGameEvent:
    store: StatefulObject | None
    handler: StateHandler | None

    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler

    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement the trigger method.")


class BaseEntityEvent(BaseGameEvent):
    entity: BaseGameEntity | None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity

    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement the trigger method.")


class BaseGameAction:
    store: StatefulObject | None
    handler: StateHandler | None

    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseActionOnEntity(BaseGameAction):
    entity: BaseGameEntity | None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseActionOnTarget(BaseGameAction):
    entity: BaseGameEntity | None = None
    target: BaseGameEntity | None = None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None,
                 target: BaseGameEntity | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity
        self.target = target

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseActionOnDestination(BaseGameAction):
    entity: BaseGameEntity | None = None
    destination: TileCoordinate | None = None

    def __init__(self, store: StatefulObject | None = None, handler:  StateHandler | None = None, entity: BaseGameEntity | None = None,
                 destination: TileCoordinate | None = None) -> None:
        super().__init__(store, handler)

        self.entity = entity
        self.destination = destination

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class Message:
    """ A single message for the message log. """
    def __init__(self, text: str, fg: Tuple[int, int, int] = colors.white) -> None:
        self.plain_text = text
        self.fg= fg
        self.count = 1

    @property
    def full_text(self) -> str:
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    cursor: int = 0
    
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


class BaseItem(BaseGameEntity):
    """An Item is any game object that can be picked up and used by a Character. 
    It has a 'spawn' substate that is an instance of BaseGameSubState that manages its 
    spawning states. An Item can be stored in an inventory or used directly."""
    owner: BaseGameEntity | None = None
    _substates_manifest = (
        ("spawn", BaseGameSubState)),

    def __init__(   self,
                    store: GameStore | None = None,
                    owner: BaseGameEntity | None = None,
                    location: TileCoordinate | None = None,
                    *,
                    name: str="<Unnamed>",
                    symbol: str=' ',
                    color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__(store=store, location=location, name=name, symbol=symbol, color=color)
        self.owner = owner


class BaseInventorySlot:
    name: str
    item: BaseItem | None
    quantity: int
    max_quantity: int = 1
    
    def __init__(self, name: str = '', item: BaseItem | None = None, quantity: int = 0, max_quantity: int = 99) -> None:
        self.name = name
        self.item = item
        self.quantity = quantity
        self.max_quantity = max_quantity


class BaseInventory:
    store: BaseGameEntity | None = None
    slot_template: BaseInventorySlot | None = None
    slots: dict[str, BaseInventorySlot]
    max_slots: int = 20

    def __init__(self, store: BaseGameEntity | None = None, slot_template: BaseInventorySlot | None = None, max_slots: int = 20) -> None:
        self.store = store
        self.slot_template = slot_template
        self.slots = {}
        self.max_slots = max_slots
    
    def get(self, item_name: str) -> BaseItem | None:
        if item_name in self.slots and self.slots[item_name].quantity > 0:
            item_slot = self.slots[item_name]
            item_slot.quantity -= 1
            return item_slot.item
        
        return None
    
    def add(self, item: BaseItem) -> None:
        if len(self.slots) >= self.max_slots and item.name not in self.slots:
            self.store.store.portfolio.log.add(f"{self.store.name}'s inventory is full and cannot pick up {item.name}.")  # type: ignore | Assume store is Character and store.store is GameStore
            return # This state check should move to Action/Behavior later

        item.owner = self.store  # type: ignore | Assume store is Character
        if item.name in self.slots:
            self.slots[item.name].quantity += 1
        else:
            if self.slot_template:
                new_inventory_slot = deepcopy(self.slot_template)
                new_inventory_slot.item = item
                new_inventory_slot.name = item.name
                new_inventory_slot.quantity = 1
                self.slots[item.name] = new_inventory_slot
 
        self.store.store.log.add(f"{self.store.name} picks up {item.name}.")  # type: ignore | Assume store is Character and store.store is GameStore
 
    def drop(self, item_name: str) -> bool:
        if item_name in self.slots:
            if self.slots[item_name].quantity > 1:
                self.slots[item_name].quantity -= 1
            else:
                del self.slots[item_name]
            return True
        return False