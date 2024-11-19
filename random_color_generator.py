import random
import colorsys
import json

class RandomColorGenerator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "h_range": ("FLOAT", {"default": [0, 360], "min": 0, "max": 360}),
                "s_range": ("FLOAT", {"default": [0, 1], "min": 0, "max": 1}),
                "l_range": ("FLOAT", {"default": [0, 1], "min": 0, "max": 1}),
                "seed": ("INT", {"default": None}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("color1_hex", "color2_hex")
    FUNCTION = "generate_random_colors"
    CATEGORY = "✨✨✨design-ai"

    def generate_random_colors(self, h_range, s_range, l_range, seed=None):
        if seed is not None:
            random.seed(seed)

        # Generate first random color in HSL
        h = random.uniform(h_range[0], h_range[1])
        s = random.uniform(s_range[0], s_range[1])
        l = random.uniform(l_range[0], l_range[1])

        # Convert HSL to RGB
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        # Convert RGB to Hex
        color1_hex = f"#{r:02x}{g:02x}{b:02x}"

        # Create color description JSON
        color1_description = json.dumps({
            "rgb": (r, g, b),
            "hsl": (h, s, l),
            "hex": color1_hex
        })

        # Generate second color
        if random.random() < 0.5:
            color2_hex = color1_hex
        else:
            color2_hex = "#ffffff"  # Pure white

        return color1_hex, color2_hex, color1_description
