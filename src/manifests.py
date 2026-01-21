from game_types import ascii_graphic
from game_types import GraphicsManifestDict, TileTuple


DEFAULT_TILEMAP_MANIFEST = GraphicsManifestDict({'dimensions': {'grid_size': TileTuple(([50], [50]))},
                                         'statespace': {    'bits': ('blocks_movement', 'blocks_vision', 'visible', 'seen'),
                                                            'vector_tuples': ( (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1),
                                                                        (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1),
                                                                        (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1),
                                                                        (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1) ),
                                                            'dtype_labels': {'names': ('shroud', 'visible', 'explored', 'first_look'),
                                                                            'fixed_bits': { 'shroud':       (None, None, 0, 0),
                                                                                            'visible':      (None, None, 1, 1),
                                                                                            'first_look':   (None, None, 1, 0),
                                                                                            'explored':     (None, None, 0, 1)
                                                                                            }
                                                                            },
                                                            'label_map': (),
                                                                },
                                         'colors': {"fill_bluebell": (ord(" "), (255, 255, 255), (50, 50, 150)),
                                                    "fill_light_yellow": (ord(" "), (255, 255, 255), (200, 180, 50)),
                                                    "fill_black": (ord(" "), (255, 255, 255), (0, 0, 0)),
                                                    "fill_dark_blue": (ord(" "), (255, 255, 255), (0, 0, 100)),
                                                    "fill_golden_yellow": (ord(" "), (255, 255, 255), (130, 110, 50)),
                                                    "fill_brown": (ord(" "), (255, 255, 255), (100, 50, 0)),
                                                    "fill_golden_brown": (ord(" "), (255, 255, 255), (180, 120, 20))
                                                        },
                                         'dtypes': {
                                                        "tile_state_vector": None,
                                                        "tile_color": ascii_graphic,
                                                        "tile_graphic": None,
                                                        "tile_grid": None
                                         },
                                         'graphics': {  "default": {   "fixed_state_bits": (1, 1, None, None),
                                                                        "state_definitions": {'shroud': 'fill_black'}},
                                                        "floor": {  "fixed_state_bits": (0, 0, None, None),
                                                                    "state_definitions": {'shroud': 'fill_black',
                                                                                    'explored': 'fill_bluebell',
                                                                                    'first_look': 'fill_light_yellow',
                                                                                    'visible': 'fill_light_yellow'}},
                                                        "wall": {   "fixed_state_bits": (1, 1, None, None),
                                                                    "state_definitions": {'shroud': 'fill_black',
                                                                                    'explored': 'fill_dark_blue',
                                                                                    'first_look': 'fill_golden_yellow',
                                                                                    'visible': 'fill_golden_yellow'}},
                                                        "solid_door": {   "fixed_state_bits": (1, 1, None, None),
                                                                            "state_definitions": {'shroud': 'fill_black',
                                                                                    'explored': 'fill_brown',
                                                                                    'first_look': 'fill_golden_brown',
                                                                                    'visible': 'fill_golden_brown'}},
                                                        }
                                         })