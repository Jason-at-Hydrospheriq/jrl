import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np


from core_components.entities.attributes import *
from core_components.entities.factory import *
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

# def test_spawn_entity():
#     location = MapCoords(10, 15)
#     spawned_orc = spawn(ORC, location)
    
#     try:
#         assert spawned_orc is not ORC  # Ensure it's a different instance
#         assert spawned_orc.name == ORC.name
#         assert spawned_orc.char == ORC.char
#         assert spawned_orc.color == ORC.color
#         assert spawned_orc.physical.max_hp == ORC.physical.max_hp
#         assert spawned_orc.location == location

#     except AssertionError:
#         pytest.fail("Entity spawning did not function as expected")