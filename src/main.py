# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import time
import tcod
from delays import GLOBAL_COOLDOWN_TIME
from engine import GameEngine
from entities.behaviors import InputEvent
import gc
import traceback

LAST_UPDATE_TIME = 0.0
LAST_EVENT = {}

def throttle() -> bool:
    global LAST_UPDATE_TIME
    """A simple AI throttle to limit how often the AI can process events/actions."""
    
    if (time.time() - LAST_UPDATE_TIME) < GLOBAL_COOLDOWN_TIME / 1000:
        return False
    # print(f"Throttled Main Loop to {1 / (time.time() - LAST_UPDATE_TIME):.2f} FPS")
    
    LAST_UPDATE_TIME = time.time()
    # print(LAST_UPDATE_TIME)

    return True

def is_spam(event_key: str) -> bool:
    global LAST_EVENT
    current_time = time.time()
    
    # Check if this event type is on cooldown
    if event_key in LAST_EVENT:
        time_diff = current_time - LAST_EVENT[event_key]

        if time_diff < GLOBAL_COOLDOWN_TIME / 1000:
            print(f"Ignoring spam event: {event_key}, dt: {(time_diff*1000):.2f}ms")
            return True # Ignore the event (spam)

    # Process the event and update the last event time
    LAST_EVENT[event_key] = current_time
    print(f"Processing event: {event_key}")
    return False


def main() -> None:
    try:
        game = GameEngine()    
        game.start() # type: ignore | State machine attribute created dynamically
        ctr = 0

        while True:
            global LAST_UPDATE_TIME

            ctr += 1

            if ctr % 50 == 0:
                if ctr % 100 == 0:
                    print(f"Main Loop 8>: {(time.time() - LAST_UPDATE_TIME)*1000:.2f}ms")
                    ctr = 0
                else:
                    print(f"Main Loop <8: {(time.time() - LAST_UPDATE_TIME)*1000:.2f}ms")
                LAST_UPDATE_TIME = time.time()
                

            # # Update Inputs
            #print("Entering tcod event loop")
            for event in tcod.event.wait(timeout=GLOBAL_COOLDOWN_TIME / 1000):

                if not is_spam(str(event.type)):
                    if event.type in ( "QUIT", "KEYDOWN" ):
                        match event.type:
                            case "QUIT":
                                game.stop()  # type: ignore
                        
                            case "KEYDOWN":
                                key_sim = event.sym
                                if game.loop and game.loop.player_loop_handler:
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
                                                # if game.ai.player_loop_handler.events.not_full and game.ai.player_loop_handler.actions.not_full:
                                                game_event = InputEvent(store=game.store, handler=game.loop.player_loop_handler, input_event=event)
                                                game.loop.player_loop_handler.handle(game_event)
                                            else:
                                                game.store.log.add(f"Events={game.loop.player_loop_handler.events.qsize()}, Actions={game.loop.player_loop_handler.actions.qsize()}")  # type: ignore
                
                # print("Leaing tcod event loop")
                if game.loop:
                    game.loop.update()

            if game.state == 'shutdown':  # type: ignore | State machine attribute created dynamically
                break

    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()

    finally:
        print("Shutting down game...")
        if game.state != 'shutdown':  # type: ignore | State machine attribute created dynamically
            game.stop()  # type: ignore
        gc.collect()
        print("Game has been shut down.")

if __name__ == "__main__":
    main()