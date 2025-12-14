
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol


class BaseGameEvent(Protocol):
    message: str

