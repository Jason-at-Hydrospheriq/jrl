# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from engine import GameEngine

def main() -> None:

    game = GameEngine()    
    game.start() # type: ignore

    while True:
        
        # Update Display
        if game.display:
            game.display.render()

        # Update State Inputs
        for event in tcod.event.wait():
            if event.type == "QUIT":
                game.stop()  # type: ignore
            
            if event.type == "KEYDOWN":
                if event.sym == tcod.event.K_ESCAPE:
                    game.reset()  # type: ignore
            
            if event.type == "KEYDOWN":
                if event.sym == tcod.event.K_p:
                    if game.state == 'playing':  # type: ignore
                        game.pause()  # type: ignore
                    elif game.state == 'paused':  # type: ignore
                        game.resume()  # type: ignore
                    elif game.state == 'idle':  # type: ignore
                        game.play()  # type: ignore

            if game.loop and game.loop.handler:
                game.loop.handler.handle(event)

        if game.state == 'shutdown':  # type: ignore
            break

if __name__ == "__main__":
    main()