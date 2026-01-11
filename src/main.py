# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from engine import GameEngine

def main() -> None:
        
        game = GameEngine()    
        game.start() # type: ignore | State machine attribute created dynamically
        game.main_loop()
        
if __name__ == "__main__":
    main()