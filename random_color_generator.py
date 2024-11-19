import random
import colorsys

class RandomColorGenerator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1, "step": 1}),
                "hue_min": ("INT", {"default": 0, "min": 0, "max": 360, "step": 1}),
                "hue_max": ("INT", {"default": 360, "min": 0, "max": 360, "step": 1}),
                "saturation_min": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "saturation_max": ("INT", {"default": 100, "min": 0, "max": 100, "step": 1}),
                "lightness_min": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "lightness_max": ("INT", {"default": 100, "min": 0, "max": 100, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "TUPLE")
    RETURN_NAMES = ("hex_color", "hsl_color")

    FUNCTION = "generate_random_color"

    CATEGORY = "✨✨✨design-ai/color"

    def generate_random_color(self, seed, hue_min, hue_max, saturation_min, saturation_max, lightness_min, lightness_max):
        # Set the seed for the random number generator
        random.seed(seed)

        # Generate a random HSL color within the specified ranges
        h = random.uniform(hue_min, hue_max) / 360.0
        s = random.uniform(saturation_min, saturation_max) / 100.0
        l = random.uniform(lightness_min, lightness_max) / 100.0

        # Convert HSL to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert RGB to 0-255 range
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

        # Convert the color to a hex string
        hex_color = f'#{r:02x}{g:02x}{b:02x}'

        # Return both hex color and HSL values
        hsl_color = (h * 360, s * 100, l * 100)
        return (hex_color, hsl_color)
