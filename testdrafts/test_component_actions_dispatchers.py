import pytest
from core_components.dispatchers.library import *

def test_dispatcher_initialization():
    # Arrange & Act
    dispatchers = [AIDispatcher(), InputDispatcher(), InterfaceDispatcher(),SystemDispatcher()]
    
    # Assert
    try:
        for dispatcher in dispatchers:
             assert dispatcher is not None, f"{dispatcher.__class__.__name__} failed to initialize."
        
        for dispatcher in dispatchers:
            # '_ev_quit' exists in BaseEventDispatcher, so checking for at least one method starting with '_ev_' 
            methods = dir(dispatcher)
            assert '_ev_quit' in methods, "'_ev_quit' not found."
        
            for method in methods:
            # Check if method names starting with '_ev_' are callable
                if method.startswith("_ev_"):
                    assert callable(getattr(dispatcher, method)), f"{method} should be callable."
            
    except Exception as e:
        pytest.fail(str(e))

def test_dispatcher_ev_quit():
    # Arrange
    dispatchers = [AIDispatcher(), InputDispatcher(), InterfaceDispatcher(),SystemDispatcher()]
    dummy_state = GameState()  # Assuming GameState can be instantiated without parameters

    # Act & Assert
    try:
        quit_event = tcod.event.Quit()
        for dispatcher in dispatchers:
            actions = dispatcher._ev_quit(quit_event, dummy_state)
            assert isinstance(actions, list), f"{dispatcher.__class__.__name__}._ev_quit should return a list of actions."
            assert all(hasattr(action, 'state') for action in actions), f"All actions returned by {dispatcher.__class__.__name__}._ev_quit should have a 'state' attribute."
    
    except Exception as e:
        pytest.fail(str(e))