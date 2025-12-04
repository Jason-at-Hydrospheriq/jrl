#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
import numpy as np

if TYPE_CHECKING:
   from engine import Engine
   from entities import PhysicalObject, Charactor, AICharactor
   from game_map import MapCoords


class Action(Protocol):
    
    def perform(self) -> None:
        ...


class BaseAction:

    def __init__(self, entity: PhysicalObject | Charactor | AICharactor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        ...  # To be implemented by subclasses.


class ActionOnTarget(BaseAction):
    def __init__(self, entity: PhysicalObject | Charactor | AICharactor, target: PhysicalObject | Charactor | AICharactor) -> None:
        super().__init__(entity)
        
        if "Charactor" in str(target.__class__) or "AICharactor" in str(target.__class__):
            if target.is_alive and target.targetable: #type: ignore
                self.entity.target = target
        elif target.physical:
            if not target.physical.is_destroyed and target.targetable:
                self.entity.target = target


class ActionOnDestination(BaseAction):

    def __init__(self, entity: PhysicalObject | Charactor | AICharactor, destination: MapCoords) -> None:
        super().__init__(entity)

        self.entity.destination = destination

class NoAction(BaseAction):
    def perform(self) -> None:
        pass


class EscapeAction(BaseAction):
    def perform(self) -> None:
        raise SystemExit()


class SystemExitAction(BaseAction):
    def perform(self) -> None:
        raise SystemExit()
    

class MoveAction(ActionOnDestination):
    def perform(self) -> None:

        if self.entity.collision: # Destination is blocked by an entity, wall, or map boundary.
            # If obstacle is an ai_actor, perform a melee attack instead.
            obstacle = self.entity.game_map.get_entity_at_location(self.entity.destination)
            if obstacle and obstacle in self.entity.game_map.live_ai_actors:
                if hasattr(self.entity, 'ai'):
                    return # Do nothing if obstacle is an AICharactor.
                else:
                    return MeleeAction(self.entity, obstacle).perform() # Player attacks AICharactor.
            if obstacle and obstacle is self.entity.game_map.player:
                if hasattr(self.entity, 'ai'):
                    return MeleeAction(self.entity, obstacle).perform() # AICharactor attacks Player.
            return  # Destination is blocked by an entity, wall, or map boundary.
        
        self.entity.move() # type: ignore


class MeleeAction(ActionOnTarget):
    def perform(self) -> None:
        damage = 0
        attack_desc = ""
        attacker_class = str(self.entity.__class__)

        if not self.entity.target:
            return  # No entity to attack.

        if not "Charactor" in attacker_class and not "AICharactor" in attacker_class:
            return  # Cannot perform melee attack if entity is not a Charactor or AICharactor.
        
        if self.entity.combat and self.entity.target.combat:
            damage = self.entity.attack() # type: ignore
            attack_desc = f"{self.entity.name} attacks {self.entity.target.name}"
        
        if damage > 0:
            print(f"{attack_desc} for {damage} hit points.")

            if self.entity.target.physical:
                self.entity.target.physical.hp -= damage
        else:
            print(f"{attack_desc} but does no damage.")
