# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from engine import GameEngine
from loop_behaviors import InputEvent
import time

GLOBAL_COOLDOWN_TIME = 10  # in milliseconds

def main() -> None:

    game = GameEngine()    
    game.start() # type: ignore | State machine attribute created dynamically

    while True:
        
        # Update Display
        if game.display:
            game.display.render()

        # Update Inputs
        for event in tcod.event.wait():
            #time.sleep(GLOBAL_COOLDOWN_TIME / 1000)  # Small delay to prevent high CPU usage
            if event.type in ( "QUIT", "KEYDOWN" ):
                match event.type:
                    case "QUIT":
                        game.stop()  # type: ignore
                
                    case "KEYDOWN":
                        key_sim = event.sym
                        if game.ai and game.ai.player_loop_handler:
                            match key_sim:
                                case tcod.event.KeySym.ESCAPE:
                                    game.reset()  # type: ignore

                                case tcod.event.KeySym.P:
                                    msg = "Game is now "

                                    if game.state == 'playing':  # type: ignore
                                        game.pause()  # type: ignore
                                        msg = msg + f"{game.state}."  # type: ignore | State machine attribute created dynamically
                                    elif game.state == 'paused':  # type: ignore
                                        game.play()  # type: ignore
                                        msg = msg + f"{game.state}."  # type: ignore | State machine attribute created dynamically
                                    elif game.state == 'idle':  # type: ignore
                                        game.play()  # type: ignore
                                        msg = msg + f"{game.state}."  # type: ignore | State machine attribute created dynamically
                                    
                                    if game.store and msg != "Game is now ":
                                        game.store.log.add(msg)
                                        print(msg)
                                case _:
                                    if game.state not in ('idle', 'paused', 'shutdown'):  # type: ignore
                                        if game.ai.player_loop_handler.events.qsize() < 10 and game.ai.player_loop_handler.actions.qsize() < 10:
                                            game_event = InputEvent(store=game.store, handler=game.ai.player_loop_handler, input_event=event)
                                            game.ai.player_loop_handler.handle(game_event)
                                        else:
                                            game.store.log.add(f"Events={game.ai.player_loop_handler.events.qsize()}, Actions={game.ai.player_loop_handler.actions.qsize()}")  # type: ignore
                
                if game.ai:
                    time.sleep(GLOBAL_COOLDOWN_TIME / 1000)  # Small delay to prevent high CPU usage
                    game.ai.update()

        if game.state == 'shutdown':  # type: ignore | State machine attribute created dynamically
            break

if __name__ == "__main__":
    main()