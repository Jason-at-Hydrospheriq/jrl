# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from engine import GameEngine
from core_components.loops.library import InputEvent
import time

def main() -> None:

    game = GameEngine()    
    game.start() # type: ignore | State machine attribute created dynamically

    while True:
        
        # Update Display
        if game.display:
            game.display.render()

        # Update State Inputs
        for event in tcod.event.wait():
            time.sleep(0.01)  # Small delay to prevent high CPU usage
            if event.type in ( "QUIT", "KEYDOWN" ):
                match event.type:
                    case "QUIT":
                        game.stop()  # type: ignore
                
                    case "KEYDOWN":
                        key_sim = event.sym
                        if game.loop and game.loop.handler:
                            if game.loop.handler.events.qsize() < 10 and game.loop.handler.actions.qsize() < 10:
                                match key_sim:
                                    case tcod.event.KeySym.ESCAPE:
                                        game.reset()  # type: ignore

                                    case tcod.event.KeySym.P:
                                        if game.state == 'playing':  # type: ignore
                                            game.pause()  # type: ignore
                                        elif game.state == 'paused':  # type: ignore
                                            game.play()  # type: ignore
                                        elif game.state == 'idle':  # type: ignore
                                            game.play()  # type: ignore
                                    case _:
                                            game_event = InputEvent(store=game.store, handler=game.loop.handler, input_event=event)
                                            game.loop.handler.handle(game_event)

        if game.state == 'shutdown':  # type: ignore
            break

if __name__ == "__main__":
    main()