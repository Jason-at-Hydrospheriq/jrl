#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import itertools
from typing import List


# Helper functions to create GraphicManifestDict
def create_states(n: int) -> List[str]:
    """
    Generates a list of all possible binary strings for a given bit length n.

    Args:
        n: The desired number of bits (length of the binary strings).

    Returns:
        A list of strings, where each string is a unique n-bit binary representation.
    """
    if n < 0:
        raise ValueError("Bit length must be a non-negative integer.")
        
    # itertools.product('01', repeat=n) generates all combinations of '0' and '1' 
    # of length n as tuples, which are then joined into strings.
    return [''.join(i) for i in itertools.product('01', repeat=n)]

def graphics_state_assignment(manifest):
    statebits = manifest['state_definition']['bits']
    n = len(statebits)
    manifest['state_definition']['names'] = create_states(n)

    graphics = manifest['graphics']
    states = manifest['state_definition']['names']
    labels = manifest['state_definition']['dtype_labels']

    # Assign allowable states to graphics based on their fixed state bits
    for graphic in graphics.values():

        # Screen through each state and assign it to a graphic if it matches the fixed state bits
        for state in states:
            add_state = False

            for idx, bit in enumerate(state):
                fixed_bit = graphic['fixed_state_bits'][statebits[idx]]
                if fixed_bit is None:
                    pass

                elif fixed_bit == int(bit):
                    add_state = True

                else:
                    add_state = False
                    break

            if add_state:
                # Screen through each label and assign a color state label to the state
                for label_name, label_bits in labels.items():
                    use_label = False
                    for idx, bit in enumerate(state):
                        if label_bits[statebits[idx]] is None:
                            use_label = True
                        
                        elif label_bits[statebits[idx]] == int(bit):
                            use_label = True

                        else:
                             # Placeholder for actual color name
                             use_label = False
                             break
                        
                    if use_label:
                        graphic['state_labels'][state] = (label_name, "color name")

    return manifest


    