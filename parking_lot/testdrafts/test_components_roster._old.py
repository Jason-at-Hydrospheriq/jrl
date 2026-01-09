import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from game_components.portfolio import Portfolio, ORC, TROLL, PLAYER
from core_components.tiles.base import TileCoordinate, TileTuple

# def test_roster_spawn():
#     roster = Roster()
#     location_ = TileTuple(([5], [5]))
#     spawn_location = TileCoordinate(location_)
    
#     portfolio.spawn(ORC, spawn_location)
    
#     try:
#         assert len(portfolio.entities) == 1
#         spawned_orc = next(iter(portfolio.entities))
#         assert spawned_orc.name == "Orc"
#         assert spawned_orc.location == spawn_location

#     except AssertionError:
#         pytest.fail("Roster spawn did not function as expected")

# def test_roster_entity_blocked_locations():
#     roster = Roster()
#     portfolio.spawn(ORC, TileCoordinate(1, 1))
#     portfolio.spawn(TROLL, TileCoordinate(2, 2))
    
#     try:
#         blocked_locations = portfolio.entity_blocked_locations
#         assert len(blocked_locations) == 2
#         assert TileCoordinate(1, 1) in blocked_locations
#         assert TileCoordinate(2, 2) in blocked_locations

#     except AssertionError:
#         pytest.fail("Entity blocked locations did not function as expected")

# def test_roster_entity_collision():
#     roster = Roster()
#     orc_location = TileCoordinate(3, 3)
#     troll_location = TileCoordinate(4, 4)
    
#     portfolio.spawn(ORC, orc_location)
#     portfolio.spawn(TROLL, troll_location)
    
#     moving_entity = ORC
#     moving_entity.destination = TileCoordinate(3, 3)  # Collides with spawned ORC
    
#     try:
#         assert portfolio.entity_collision(moving_entity) == True
        
#         moving_entity.destination = TileCoordinate(2, 2)  # No collision
#         assert portfolio.entity_collision(moving_entity) == False

#     except AssertionError:
#         pytest.fail("Entity collision detection did not function as expected")

# def test_roster_live_actors():
#     roster = Roster()
#     portfolio.spawn(ORC, TileCoordinate(1, 1))
#     portfolio.spawn(PLAYER, TileCoordinate(2, 2))
#     portfolio.spawn(TROLL, TileCoordinate(3, 3))
    
#     try:
#         live_actors = portfolio.live_actors
#         assert len(live_actors) == 3
        
#         # Simulate one actor dying
#         for actor in live_actors:
#             if actor.name == "Orc":
#                 actor.physical.hp = 0  # Orc is dead
        
#         live_actors_after_death = portfolio.live_actors
#         assert len(live_actors_after_death) == 2
#         assert live_actors_after_death[0].name == "Player"
#         assert live_actors_after_death[1].name == "Troll"

#     except AssertionError:
#         pytest.fail("Live actors filtering did not function as expected")

# def test_roster_live_ai_actors():
#     roster = Roster()
#     portfolio.spawn(ORC, TileCoordinate(1, 1))
#     portfolio.spawn(PLAYER, TileCoordinate(2, 2))
#     portfolio.spawn(TROLL, TileCoordinate(3, 3))
    
#     try:
#         live_ai_actors = portfolio.live_ai_actors
#         assert len(live_ai_actors) == 2
        
#         # Simulate one AI actor dying
#         for actor in live_ai_actors:
#             if actor.name == "Troll":
#                 actor.physical.hp = 0  #type: ignore  # Troll is dead
        
#         live_ai_actors_after_death = portfolio.live_ai_actors
#         assert len(live_ai_actors_after_death) == 1
#         assert live_ai_actors_after_death[0].name == "Orc"

#     except AssertionError:
#         pytest.fail("Live AI actors filtering did not function as expected")

# def test_roster_get_entity_at_location():
#     roster = Roster()
#     location = TileCoordinate(7, 7)
#     portfolio.spawn(ORC, location)
    
#     try:
#         entities_at_location = portfolio.get_entity_at_location(location)
#         assert entities_at_location
#         assert len(entities_at_location) == 1
#         assert next(iter(entities_at_location)).name == "Orc"
        
#         empty_location = TileCoordinate(0, 0)
#         entities_at_empty_location = portfolio.get_entity_at_location(empty_location)
#         assert not entities_at_empty_location

#     except AssertionError:
#         pytest.fail("Get entity at location did not function as expected")

