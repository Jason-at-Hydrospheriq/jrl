#!/usr/bin/env python3
# -*- coding: utf-8 -*-M

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Tuple
import numpy as np  # type: ignore
import tcod

from components.action_handlers.ai_events import AIEvent, AIEventPathToTarget, AIEventTargetInMeleeRange, AIEventNone

if TYPE_CHECKING:
    from entities import AICharactor, Charactor
    from engine import Engine
    from src.components.game_map import MapCoords


class BaseAI:
    entity: AICharactor

    def __init__(self, entity: AICharactor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine
    
    def event(self) -> AIEvent:
        raise NotImplementedError()
        
    def get_path_to(self, destination: MapCoords) -> List[MapCoords]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.physical_objects:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.location.x, entity.location.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.location.x, entity.location.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.location.x, self.entity.location.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((destination.x, destination.y))[1:].tolist()
        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [self.entity.game_map.get_map_coords(index[0], index[1]) for index in path]
    
    
class HostileAI(BaseAI):
    path: List[MapCoords] = []
    target: Optional[Charactor] = None
    
    def __init__(self, entity: AICharactor) -> None:
        super().__init__(entity)
        self.target = None
        self.path = []

    @property
    def distance_to_target(self) -> Optional[int]:
        if self.target:
            dx = self.target.location.x - self.entity.location.x
            dy = self.target.location.y - self.entity.location.y
            return max(abs(dx), abs(dy))
        return None

    def event(self) -> AIEvent:
        # Acquire target if none exists or if target is dead
        if self.entity.in_player_fov:
            if not self.target or not self.target.is_alive:
                self.target = self.engine.player

            # Recalculate path to target
            self.path = self.get_path_to(self.target.location) if self.target else []

        if self.target:
            if self.distance_to_target is not None:
                if self.distance_to_target <= 1:
                    return AIEventTargetInMeleeRange(self.entity, self.target)
                
                else:
                    if self.path:
                        return AIEventPathToTarget(self.entity, self.path[0])
            
        return AIEventNone(self.entity)
