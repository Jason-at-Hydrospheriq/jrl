#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from baseclasses import BaseGameSubState, BaseInventorySlot, BaseInventory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.actors import Character


class CollisionSubState(BaseGameSubState):
    """The CollisionSubState is a class that defines and runs the 'collision' state machine for a Game Entity.
    This state machine tracks whether an Entity is colliding with another object or not. It manages the 
    'entity_collision', 'terrain_collision', 'boundary_collision' state bits in the state_vector."""

    _state_bits = ('in_entity_collision', 'in_terrain_collision', 'in_boundary_collision')
    _states = ( {'name':'colliding_with_entity', 'on_enter': ['update']},
                {'name':'colliding_with_terrain', 'on_enter': ['update']},
                {'name':'colliding_with_boundary', 'on_enter': ['update']},
                {'name':'not_colliding', 'on_enter': ['update']},
                {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'colliding_with_entity', 'conditions':['is_on_map', 'is_colliding_with_entity']},
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_entity'], 'dest':'colliding_with_terrain', 'conditions':['is_on_map', 'is_colliding_with_terrain']},
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_entity'], 'dest':'colliding_with_boundary', 'conditions':['is_on_map', 'is_colliding_with_boundary']},
            {'trigger':'update', 'source':['unknown', 'colliding_with_entity', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'not_colliding', 'conditions':['is_on_map', 'is_not_colliding']},
            {'trigger':'update', 'source':['not_colliding', 'colliding_with_entity', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'unknown', 'conditions':['is_not_on_map']})
    _initial_state = 'not_colliding'

    def set_bits(self) -> None:
        self.store.state_vector['in_entity_collision'] = self.store.destination_is_blocking_entity  # type: ignore
        self.store.state_vector['in_terrain_collision'] = self.store.destination_is_blocking_terrain  # type: ignore
        self.store.state_vector['in_boundary_collision'] = self.store.destination_is_map_boundary  # type: ignore

    def is_colliding_with_entity(self) -> bool:
        return self.store.state_vector['in_entity_collision']  # type: ignore

    def is_colliding_with_terrain(self) -> bool:
        return self.store.state_vector['in_terrain_collision']  # type: ignore

    def is_colliding_with_boundary(self) -> bool:
        return self.store.state_vector['in_boundary_collision']  # type: ignore

    def is_not_colliding(self) -> bool:
        return not (self.store.state_vector['in_entity_collision'] or  # type: ignore
                    self.store.state_vector['in_terrain_collision'] or  # type: ignore
                    self.store.state_vector['in_boundary_collision'])  # type: ignore

    def is_colliding(self) -> bool:
        return not self.is_not_colliding()


class TargetedSubState(BaseGameSubState):
    """The TargetedSubState is a class that defines and runs the 'perception' state machine for a Game Entity.
    This state machine tracks whether an Entity is targeted by another entity. It manages the 'is_target' state
    bit in the state_vector."""

    _state_bits = ('is_target',)
    _states = ({'name':'targeted', 'on_enter': ['update']},
                 {'name':'not_targeted', 'on_enter': ['update']},
                 {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['not_targeted', 'unknown'], 'dest':'targeted', 'conditions':['is_on_map', 'is_target']},
            {'trigger':'update', 'source':['targeted', 'unknown'], 'dest':'not_targeted', 'conditions':['is_on_map', 'is_not_target']},
            {'trigger':'update', 'source':['targeted', 'not_targeted'], 'dest':'unknown', 'conditions':['is_not_on_map']},
        )
    _initial_state = 'not_targeted'

    def set_bits(self) -> None:
        self.store.state_vector['is_target'] = self.store.targeter is not None  # type: ignore

    def is_target(self) -> bool:
        return self.store.state_vector['is_target']  # type: ignore

    def is_not_target(self) -> bool:
        return not self.store.state_vector['is_target']  # type: ignore


class TargetingSubState(BaseGameSubState):
    """The TargetingSubState is a class that defines and runs the 'focus' state machine for a Game Entity.
    This state machine tracks whether an Entity has a target and the status of that target. It manages the 
    'target_in_fov', 'target_is_hostile', and 'has_target' state bits in the state_vector."""

    threat_level_threshold: int = 60

    state_changed: bool = False
    _state_bits = ('target_in_fov', 'target_is_hostile', 'has_target')
    _states = ({'name':'stopped', 'on_enter':['update']},
                {'name':'idle', 'on_enter':['update']},
                {'name':'searching', 'on_enter':['update']},
                {'name':'tracking', 'on_enter':['state_transition']},
                {'name':'targeting', 'on_enter':['update']},
                {'name':'unknown', 'on_enter':['update']},)
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'searching', 'tracking', 'targeting'], 'dest':'idle', 'conditions':['is_on_map', 'has_no_target']},
            {'trigger':'update', 'source':['unknown', 'idle', 'tracking', 'targeting'], 'dest':'searching', 'conditions':['is_on_map', 'has_target', 'has_no_visible_target', 'has_no_hostile_target']},
            {'trigger':'update', 'source':['unknown', 'idle', 'searching', 'targeting'], 'dest':'tracking', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_no_hostile_target',]},
            {'trigger':'update', 'source':['unknown', 'idle', 'searching', 'tracking'], 'dest':'targeting', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_hostile_target']},
            {'trigger':'update', 'source':['idle', 'searching', 'tracking', 'targeting'], 'dest':'unknown', 'conditions':['is_not_on_map']},
            )
    _initial_state = 'idle'

    def state_transition(self) -> None:
        self.state_changed = True
        self.set_bits()

    def set_bits(self) -> None: # Interprets store data to set state bits
        self.store.state_vector['target_in_fov'] = self.store.target_in_fov  # type: ignore
        self.store.state_vector['target_is_hostile'] = self.store.threat_level > self.threat_level_threshold # type: ignore
        self.store.state_vector['has_target'] = self.store.target is not None  # type: ignore

    # All substates must have the primary state bit methods
    def has_target(self) -> bool:
        return self.store.state_vector['has_target']  # type: ignore

    def has_no_target(self) -> bool:
        return not self.store.state_vector['has_target']  # type: ignore

    def has_visible_target(self) -> bool:
        return self.store.state_vector['target_in_fov']  # type: ignore

    def has_no_visible_target(self) -> bool:
        return not self.store.state_vector['target_in_fov']  # type: ignore

    def has_hostile_target(self) -> bool:
        return self.store.state_vector['target_is_hostile']  # type: ignore

    def has_no_hostile_target(self) -> bool:
        return not self.store.state_vector['target_is_hostile']  # type: ignore


class CombatSubState(BaseGameSubState):
    """The CombatSubState is a class that defines and runs the 'combat' state machine for a Game Entity.
    This state machine tracks whether an Entity is engaged in combat, attacking, disengaged, or peaceful.
    It manages the 'in_melee_range' state bit in the state_vector. An entity can have more than one CombatSubState
    to represent different combat types (melee, missile, spell)."""

    range_threshold: int = 1  # Distance threshold for combat range
    combat_type: str = "melee"  # Type of combat: 'melee', 'missile', 'spell'

    _state_bits = (f'in_{combat_type}_range',)
    _states = ( {'name': 'engaged', 'on_enter':['update']},
                {'name': 'fighting', 'on_enter':['update']},
                {'name': 'disengaged', 'on_enter':['update']},
                {'name': 'peaceful', 'on_enter':['update']},
                {'name': 'unknown', 'on_enter':['update']})
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'peaceful', 'disengaged', 'fighting'], 'dest':'engaged', 'conditions':['is_on_map', 'is_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'peaceful', 'engaged', 'disengaged'], 'dest':'fighting', 'conditions':['is_on_map', 'is_targeting', 'is_in_range']},
            {'trigger':'update', 'source':['unknown', 'disengaged', 'engaged', 'fighting'], 'dest':'peaceful', 'conditions':['is_on_map', 'is_not_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'peaceful', 'engaged', 'fighting'], 'dest':'disengaged', 'conditions':['is_on_map', 'is_not_targeting', 'is_in_range']},
            {'trigger':'update', 'source':['peaceful', 'engaged', 'disengaged', 'fighting'], 'dest':'unknown', 'conditions':['is_not_on_map']},)
    _initial_state = 'disengaged'

    def set_bits(self) -> None: # Interprets distance to target and targeting status into state bits
        if self.store.distance_to_target is not None:  # type: ignore
            self.store.state_vector[f'in_{self.combat_type}_range'] = self.store.distance_to_target <= self.range_threshold  # type: ignore

    def is_in_range(self) -> bool:
        return self.store.state_vector[f'in_{self.combat_type}_range']  # type: ignore

    def is_out_of_range(self) -> bool:
        return not (self.is_in_range()) # or self.is_in_missile_range() or self.is_in_spell_range())

    def is_targeting(self) -> bool:
        return self.store.focus.is_targeting()  # type: ignore 

    def is_not_targeting(self) -> bool:
        return not self.store.focus.is_targeting()  # type: ignore


class CharacterHealthSubState(BaseGameSubState):
    """The CharacterHealthSubState is a class that defines and runs the 'health' state machine for a Game Entity.
    This state machine tracks whether a Character is healthy, injured, critical, or dead. It manages the 
    'is_healthy', 'is_injured', 'is_critical', and 'is_dead' state bits in the state_vector."""

    _state_bits = ('is_healthy', 'is_injured', 'is_critical', 'is_dead')
    _states = ( {'name':'healthy', 'on_enter': ['update']},
                {'name':'injured', 'on_enter': ['update']},
                {'name':'critical', 'on_enter': ['update']},
                {'name':'unconscious', 'on_enter': ['update']},
                {'name':'dead', 'on_enter': ['update']},
                {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'injured', 'critical', 'unconscious'], 'dest':'healthy', 'conditions':['is_on_map', 'is_healthy']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'critical', 'unconscious'], 'dest':'injured', 'conditions':['is_on_map', 'is_injured']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'unconscious'], 'dest':'critical', 'conditions':['is_on_map', 'is_critical']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'critical'], 'dest':'unconscious', 'conditions':['is_on_map', 'is_unconscious']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'critical', 'unconscious'], 'dest':'dead', 'conditions':['is_on_map', 'is_dead']},
            {'trigger':'update', 'source':['healthy', 'injured', 'critical', 'unconscious', 'dead'], 'dest':'unknown', 'conditions':['is_not_on_map']},)
    _initial_state = 'healthy'

    def set_bits(self) -> None:
        if self.store.hp is not None and self.store.max_hp is not None:  # type: ignore | Character can take damage when alive.
            self.store.state_vector['is_healthy'] = self.store.hp > (0.7 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_injured'] = (0.3 * self.store.max_hp) < self.store.hp <= (0.7 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_critical'] = 0 < self.store.hp <= (0.3 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_unconscious'] = self.store.hp == 0 and self.store.is_alive  # type: ignore

        elif self.store.hp is None:  # type: ignore | Character cannot take damage when dead.
            self.store.state_vector['is_dead'] = not self.store.is_alive  # type: ignore

    def is_healthy(self) -> bool:
        return self.store.state_vector['is_healthy']  # type: ignore

    def is_injured(self) -> bool:
        return self.store.state_vector['is_injured']  # type: ignore

    def is_critical(self) -> bool:
        return self.store.state_vector['is_critical']  # type: ignore

    def is_unconscious(self) -> bool:
        return self.store.state_vector['is_unconscious']  # type: ignore

    def is_dead(self) -> bool:
        return self.store.state_vector['is_dead']  # type: ignore
    

class PlayerInventory(BaseInventory):
    """An Inventory Slot for the Player Character's inventory. Can hold multiple items of the same type."""
    
    def __init__(self, store: Character | None = None, max_quantity: int = 5, max_slots: int = 20) -> None:
        super().__init__(store=store, slot_template=BaseInventorySlot(max_quantity=max_quantity), 
                         max_slots=max_slots)


