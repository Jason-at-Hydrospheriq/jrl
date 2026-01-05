import pytest
from sys import path

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.maps.atlas import Atlas
from core_components.maps.generators.library import DungeonGenerator
from core_components.entities.portfolio import Portfolio
from core_components.store import GameStore

def test_component_portfolio_initialization():
    # Arrange
    store = GameStore()
    portfolio = Portfolio(store=store)

    # Act
    entities = portfolio.entities
    player = portfolio.player
    all_actors = portfolio.all_actors
    entity_locations = portfolio.entity_locations

    # Assert
    assert isinstance(portfolio, Portfolio)
    assert isinstance(entities, set)
    assert player is None
    assert isinstance(all_actors, list)
    assert isinstance(entity_locations, list)

def test_component_portfolio_entity_blocked_locations():
    # Arrange
    store = GameStore()
    store.atlas = Atlas(store=store)
    store.atlas.create_map()

    portfolio = Portfolio(store=store)
    portfolio.spawn_player(store.atlas.active)
    player_location = None
    if portfolio.player is not None:
        player_location = portfolio.player.location

    # Act
    blocked_locations = portfolio.entity_blocked_locations

    # Assert
    assert isinstance(blocked_locations, list)
    assert len(blocked_locations) == 1

    if portfolio.player is not None:
        assert player_location in blocked_locations

def test_component_portfolio_spawn_player():
    # Arrange
    store = GameStore()
    store.atlas = Atlas(store=store)
    store.atlas.create_map()

    portfolio = Portfolio(store=store)

    # Act
    portfolio.spawn_player(store.atlas.active)
    player = portfolio.player

    # Assert
    assert player is not None
    assert player in portfolio.entities
    assert player in portfolio.all_actors
    assert player in portfolio.live_actors
    assert player not in portfolio.live_ai_actors