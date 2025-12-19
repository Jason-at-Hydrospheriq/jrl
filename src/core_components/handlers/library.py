#!/usr/bin/env python3
# -*- coding: utf-8 -*-M

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core_components.entities.library import MobCharactor

from core_components.events.library import MeleeAttackEvent, TargetAvailableAIEvent, OnTargetAIEvent
from core_components.handlers.base import BaseHandler, EntityStateTableDict


MOB_STATES = EntityStateTableDict({   'bits': ('is_alive', 'is_spotted', 'is_spotting', 'is_targeting', 'is_target_in_melee_range'),
                                        'vector_tuples': 
((0, 0, 0, 0, 0),
 (0, 0, 0, 0, 1),
 (0, 0, 0, 1, 0),
 (0, 0, 0, 1, 1),
 (0, 0, 1, 0, 0),
 (0, 0, 1, 0, 1),
 (0, 0, 1, 1, 0),
 (0, 0, 1, 1, 1),
 (0, 1, 0, 0, 0),
 (0, 1, 0, 0, 1),
 (0, 1, 0, 1, 0),
 (0, 1, 0, 1, 1),
 (0, 1, 1, 0, 0),
 (0, 1, 1, 0, 1),
 (0, 1, 1, 1, 0),
 (0, 1, 1, 1, 1),
 (1, 0, 0, 0, 0),
 (1, 0, 0, 0, 1),
 (1, 0, 0, 1, 0),
 (1, 0, 0, 1, 1),
 (1, 0, 1, 0, 0),
 (1, 0, 1, 0, 1),
 (1, 0, 1, 1, 0),
 (1, 0, 1, 1, 1),
 (1, 1, 0, 0, 0),
 (1, 1, 0, 0, 1),
 (1, 1, 0, 1, 0),
 (1, 1, 0, 1, 1),
 (1, 1, 1, 0, 0),
 (1, 1, 1, 0, 1),
 (1, 1, 1, 1, 0),
 (1, 1, 1, 1, 1)),
                                        'mapping': tuple([0]*20 + [TargetAvailableAIEvent] + [0] * 2 + [MeleeAttackEvent] + [0]*4 + [TargetAvailableAIEvent] + [0]*2 + [MeleeAttackEvent]),
                    })


class MobHandler(BaseHandler):
    def __init__(self, entity: MobCharactor | None) -> None:
        super().__init__(entity)
        self.state_table = MOB_STATES
        self._set_state_matrix()
        self._set_state_mapping()











        # # Acquire target if none exists or if target is dead
        # if self.entity.in_player_fov:
        #     if not self.target or not self.target.is_alive:
        #         self.target = self.engine.player

        #     # Recalculate path to target
        #     self.path = self.get_path_to(self.target.location) if self.target else []

        # if self.target:
        #     if self.distance_to_target is not None:
        #         if self.distance_to_target <= 1:
        #             return AIEventTargetInMeleeRange(self.entity, self.target)
                
        #         else:
        #             if self.path:
        #                 return AIEventPathToTarget(self.entity, self.path[0])
            
        # return AIEventNone(self.entity)
