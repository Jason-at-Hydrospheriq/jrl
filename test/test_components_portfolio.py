import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from atlas import Atlas
from store.components import Portfolio
from store import GameStore
from game_types import TileCoordinate

def test_component_portfolio_initialization():
    try:
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
    
    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_portfolio_entity_blocked_locations():
    try:
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
            
    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_portfolio_spawn_player():
    try:
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

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_component_portfolio_get_entity_at_location():
    try:
        # Arrange
        store = GameStore()
        store.atlas = Atlas(store=store)
        store.atlas.create_map()
        portfolio = Portfolio(store=store)
        
        location = TileCoordinate.from_tuple((7, 7), parent_map_size=store.atlas.active.grid.size)
        portfolio.spawn_at_location(entity=portfolio.ORC, location=location)
        empty_location = TileCoordinate.from_tuple((0, 0), parent_map_size=store.atlas.active.grid.size)
        
        # Act
        entities_at_location = portfolio.get_entity_at_location(location)
        entities_at_empty_location = portfolio.get_entity_at_location(empty_location)
    
        # Assert
        assert entities_at_location
        assert len(entities_at_location) == 1
        assert next(iter(entities_at_location)).name == "Orc"
        assert not entities_at_empty_location

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass