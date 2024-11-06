import torch
import numpy as np
import random
from PIL import Image
from .utils import color_utils

class TextColorOnBg:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "color_hex": ("STRING",),
                "color_hex_combination": ("STRING",),
                "min_contrast_ratio": ("FLOAT", {"default": 4.5, "min": 1.0, "max": 21.0}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST", "STRING", "LIST")
    RETURN_NAMES = ("random_color", "valid_colors", "max_contrast_color", "high_contrast_colors")
    FUNCTION = "select_high_contrast_color"
    CATEGORY = "✨✨✨design-ai/color"

    def select_high_contrast_color(self, color_hex, color_hex_combination, min_contrast_ratio):
        base_color = color_utils.hex_to_rgb(color_hex)
        color_list = color_hex_combination.split(';')
        valid_colors = []
        max_contrast = 0
        max_contrast_color = "#000000"

        for color_hex in color_list:
            color = color_utils.hex_to_rgb(color_hex)
            contrast = color_utils.contrast_ratio(base_color, color)
            if contrast >= min_contrast_ratio:
                valid_colors.append(color_hex)
                if contrast > max_contrast:
                    max_contrast = contrast
                    max_contrast_color = color_hex

        if valid_colors:
            random_color = random.choice(valid_colors)
        else:
            # 优化兜底逻辑
            black_contrast = color_utils.contrast_ratio(base_color, (0, 0, 0))
            white_contrast = color_utils.contrast_ratio(base_color, (255, 255, 255))
            random_color = "#000000" if black_contrast > white_contrast else "#FFFFFF"

        return (random_color, valid_colors, max_contrast_color)