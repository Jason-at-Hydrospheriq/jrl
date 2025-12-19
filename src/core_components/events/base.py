
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class BaseGameEvent(Protocol):
    message: str
    
