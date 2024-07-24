from .blackborderdetector import BlackBorderDetector
from .cropborder import Cropborder

NODE_CLASS_MAPPINGS = { "BlackBorderDetector": BlackBorderDetector,
                       "Cropborder": Cropborder }

NODE_DISPLAY_NAME_MAPPINGS = { "BlackBorderDetector": "img_black_border_detector",
                              "Cropborder": "img_crop_border" }

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']