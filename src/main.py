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
            if event.type in ( "QUIT", "KEYDOWN" ):
                match event.type:
                    case "QUIT":
                        game.stop()  # type: ignore
                
                    case "KEYDOWN":
                        key_sim = event.sym
                        match key_sim:
                            case tcod.event.K_ESCAPE:
                                game.reset()  # type: ignore

                            case tcod.event.K_p:
                                if game.state == 'playing':  # type: ignore
                                    game.pause()  # type: ignore
                                elif game.state == 'paused':  # type: ignore
                                    game.play()  # type: ignore
                                elif game.state == 'idle':  # type: ignore
                                    game.play()  # type: ignore

                        if game.loop and game.loop.handler:
                            game.loop.handler.handle(event)

        if game.state == 'shutdown':  # type: ignore
            break

if __name__ == "__main__":
    main()