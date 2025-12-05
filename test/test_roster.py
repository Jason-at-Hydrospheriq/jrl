import pytest
import numpy as np
import sys

# Ensure the src directory is on sys.path so dataset can be imported
SRC_DIR = r'C:\Users\jason\workspaces\repos\jrl' or ".."

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.components.roster import Roster, ORC, TROLL
from src.components.game_map import MapCoords

def test_roster_spawn():
    roster = Roster()
    spawn_location = MapCoords(5, 5)
    
    roster.spawn(ORC, spawn_location)
    
    try:
        assert len(roster.entities) == 1
        spawned_orc = next(iter(roster.entities))
        assert spawned_orc.name == "Orc"
        assert spawned_orc.location == spawn_location

    except AssertionError:
        pytest.fail("Roster spawn did not function as expected")

def test_roster_entity_blocked_locations():
    roster = Roster()
    roster.spawn(ORC, MapCoords(1, 1))
    roster.spawn(TROLL, MapCoords(2, 2))
    
    try:
        blocked_locations = roster.entity_blocked_locations
        assert len(blocked_locations) == 2
        assert MapCoords(1, 1) in blocked_locations
        assert MapCoords(2, 2) in blocked_locations

    except AssertionError:
        pytest.fail("Entity blocked locations did not function as expected")

def test_roster_entity_collision():
    roster = Roster()
    orc_location = MapCoords(3, 3)
    troll_location = MapCoords(4, 4)
    
    roster.spawn(ORC, orc_location)
    roster.spawn(TROLL, troll_location)
    
    moving_entity = ORC
    moving_entity.destination = MapCoords(3, 3)  # Collides with spawned ORC
    
    try:
        assert roster.entity_collision(moving_entity) == True
        
        moving_entity.destination = MapCoords(2, 2)  # No collision
        assert roster.entity_collision(moving_entity) == False

    except AssertionError:
        pytest.fail("Entity collision detection did not function as expected")

def test_roster_live_actors():
    roster = Roster()
    roster.spawn(ORC, MapCoords(1, 1))
    roster.spawn(TROLL, MapCoords(2, 2))
    
    try:
        live_actors = roster.live_actors
        assert len(live_actors) == 2
        
        # Simulate one actor dying
        for actor in live_actors:
            if actor.name == "Orc":
                actor.physical.hp = 0  # Orc is dead
        
        live_actors_after_death = roster.live_actors
        assert len(live_actors_after_death) == 1
        assert live_actors_after_death[0].name == "Troll"

    except AssertionError:
        pytest.fail("Live actors filtering did not function as expected")

def test_roster_live_ai_actors():
    roster = Roster()
    roster.spawn(ORC, MapCoords(1, 1))
    roster.spawn(TROLL, MapCoords(2, 2))
    
    try:
        live_ai_actors = roster.live_ai_actors
        assert len(live_ai_actors) == 2
        
        # Simulate one AI actor dying
        for actor in live_ai_actors:
            if actor.name == "Troll":
                actor.physical.hp = 0  # Troll is dead
        
        live_ai_actors_after_death = roster.live_ai_actors
        assert len(live_ai_actors_after_death) == 1
        assert live_ai_actors_after_death[0].name == "Orc"

    except AssertionError:
        pytest.fail("Live AI actors filtering did not function as expected")

def test_roster_get_entity_at_location():
    roster = Roster()
    location = MapCoords(7, 7)
    roster.spawn(ORC, location)
    
    try:
        entities_at_location = roster.get_entity_at_location(location)
        assert entities_at_location
        assert len(entities_at_location) == 1
        assert next(iter(entities_at_location)).name == "Orc"
        
        empty_location = MapCoords(0, 0)
        entities_at_empty_location = roster.get_entity_at_location(empty_location)
        assert not entities_at_empty_location

    except AssertionError:
        pytest.fail("Get entity at location did not function as expected")

