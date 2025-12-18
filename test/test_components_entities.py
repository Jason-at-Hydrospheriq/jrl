from copy import deepcopy
import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np


from core_components.entities.attributes import *
from core_components.entities.library import *


def test_physical_attributes():
    physical = PhysicalStats(max_hp=20, constitution=15)
    
    try:
        assert physical.max_hp == 20
        assert physical.constitution == 15
        assert physical.hp == 20  # current_hp should initialize to max_hp

    except AssertionError:
        pytest.fail("PhysicalStats attributes did not initialize correctly")

def test_mental_attributes():
    mental = MentalStats(max_mp=10, intelligence=12)
    
    try:
        assert mental.max_mp == 10
        assert mental.intelligence == 12
        assert mental.mp == 10  # current_mp should initialize to max_mp

    except AssertionError:
        pytest.fail("MentalStats attributes did not initialize correctly")

def test_combat_attributes():
    combat = CombatStats(defense=5, attack_power=8)
    
    try:
        assert combat.defense == 5
        assert combat.attack_power == 8

    except AssertionError:
        pytest.fail("CombatStats attributes did not initialize correctly")

def test_entity_class_inheritance():
    player = PlayerCharactor(
        name="Hero",
        symbol='@',
        color=(255, 255, 255),
        physical=PhysicalStats(max_hp=30, constitution=14),
        combat=CombatStats(defense=3, attack_power=7)
    )
    
    player2 = deepcopy(player)

    try:
        for cls in [BaseEntity, BlockingEntity, MortalEntity, TargetableEntity, TargetingEntity, CombatEntity, Charactor, PlayerCharactor]:
            assert isinstance(player, cls), f"PlayerCharactor should inherit from {cls.__name__}"
            assert isinstance(player2, cls), f"Deepcopied PlayerCharactor should inherit from {cls.__name__}"
            
    except AssertionError:
        pytest.fail("PlayerCharactor does not inherit correctly from BaseEntity and Charactor")