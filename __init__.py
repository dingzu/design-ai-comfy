from .blackborderdetector import BlackBorderDetector
from .cropborder import Cropborder
from .resize_and_center import ResizeAndCenter

NODE_CLASS_MAPPINGS = {
    "BlackBorderDetector": BlackBorderDetector,
    "Cropborder": Cropborder,
    "ResizeAndCenter": ResizeAndCenter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlackBorderDetector": "img_black_border_detector",
    "Cropborder": "img_crop_border",
    "ResizeAndCenter": "resize_and_center"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']