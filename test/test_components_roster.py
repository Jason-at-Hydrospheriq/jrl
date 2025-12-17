import pytest
from sys import path

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.generators.library import DungeonGenerator
from core_components.dispatchers.library import SystemDispatcher
from core_components.roster import Roster

def test_component_roster_initialization():
    # Arrange
    roster = Roster()

    # Act
    entities = roster.entities
    player = roster.player
    all_actors = roster.all_actors
    entity_locations = roster.entity_locations

    # Assert
    assert isinstance(roster, Roster)
    assert isinstance(entities, set)
    assert player is None
    assert isinstance(all_actors, list)
    assert isinstance(entity_locations, list)

def test_component_roster_entity_blocked_locations():
    # Arrange
    roster = Roster()
    game_map = DungeonGenerator().generate()
    roster.spawn_player(game_map)
    player_location = None
    if roster.player is not None:
        player_location = roster.player.location

    # Act
    blocked_locations = roster.entity_blocked_locations

    # Assert
    assert isinstance(blocked_locations, list)
    assert len(blocked_locations) == 1

    if roster.player is not None:
        assert player_location in blocked_locations