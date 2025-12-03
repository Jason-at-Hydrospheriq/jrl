#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Tuple
import numpy as np  # type: ignore
import tcod

from components.ai_events import AIEvent, AIEventMove, AIEventMeleeAttack, AIEventNone

if TYPE_CHECKING:
    from entities import AICharactor, Charactor
    from engine import Engine

class BaseAI:
    entity: AICharactor

    def __init__(self, entity: AICharactor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine
    
    def generate_event(self) -> AIEvent:
        raise NotImplementedError()
        
    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.physical_objects:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]
    
    
class HostileAI(BaseAI):
    path: List[Tuple[int, int]] = []
    target: Optional[Charactor] = None
    
    def __init__(self, entity: AICharactor, target: Optional[Charactor] = None) -> None:
        super().__init__(entity)
        self.target = target
        self.path = self.get_path_to(target.x, target.y) if target else []

    @property
    def dx(self) -> Optional[int]:
        if self.target:
            return self.target.x - self.entity.x
        return None
    
    @property
    def dy(self) -> Optional[int]:
        if self.target:
            return self.target.y - self.entity.y
        return None
    
    @property
    def distance_to_target(self) -> Optional[int]:
        if self.dx and self.dy:
            return max(abs(self.dx), abs(self.dy))
        return None

    def _dispatch_events(self) -> AIEvent:
        if self.target:
            if self.entity.in_player_fov and self.distance_to_target is not None:
                if self.distance_to_target <= 1:
                    if self.dx and self.dy:
                        self.entity.target_dx = self.dx
                        self.entity.target_dy = self.dy

                    # Attack the player
                    return AIEventMeleeAttack(self.entity, self.target)
                
                else:
                    # Move towards the player
                    if self.path:
                        dest_x, dest_y = self.path[0]
                        return AIEventMove(self.entity, self.entity.destination)
                
        return AIEventNone(self.entity)