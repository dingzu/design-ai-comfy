from .blackborderdetector import BlackBorderDetector
from .cropborder import Cropborder
from .resize_and_center import ResizeAndCenter
from .switch_case_more import SwitchCaseMore
from .resize_by_side_pro import ResizeBySidePro
from .colorgenerator import GetPrimaryColor
from .text_color_on_bg import TextColorOnBg
from .draw_text_on_image import DrawTextOnImage
from .determine_text_position import DetermineTextPosition
from .crop_image_by_percentage import CropImageByPercentage

NODE_CLASS_MAPPINGS = {
    "BlackBorderDetector": BlackBorderDetector,
    "Cropborder": Cropborder,
    "ResizeAndCenter": ResizeAndCenter,
    "SwitchCaseMore": SwitchCaseMore,
    "ResizeBySidePro": ResizeBySidePro,
    "GetPrimaryColor": GetPrimaryColor,
    "TextColorOnBg": TextColorOnBg,
    "DrawTextOnImage": DrawTextOnImage,
    "DetermineTextPosition": DetermineTextPosition,
    "CropImageByPercentage": CropImageByPercentage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlackBorderDetector": "img_black_border_detector",
    "Cropborder": "img_crop_border",
    "ResizeAndCenter": "resize_and_center",
    "SwitchCaseMore": "Switch_case_more",
    "ResizeBySidePro": "Resize_by_side_pro",
    "GetPrimaryColor": "GetPrimaryColor",
    "TextColorOnBg": "TextColorOnBg",
    "DrawTextOnImage": "DrawTextOnImage",
    "DetermineTextPosition": "DetermineTextPosition",
    "CropImageByPercentage": "CropImageByPercentage"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

