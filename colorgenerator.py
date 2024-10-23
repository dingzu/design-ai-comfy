import numpy as np
from PIL import Image
from collections import Counter
from .utils import color_utils  # 引入你提供的 color_utils.py

class GetPrimaryColor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("INT", {"default": 30, "min": 0, "max": 255}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("main_color",)
    FUNCTION = "analyze_and_extract_main_color"
    CATEGORY = "✨✨✨design-ai"

    def analyze_and_extract_main_color(self, image, threshold):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Get image pixels and count occurrences
        pixels = list(img.getdata())
        pixel_count = Counter(pixels)
        palette = [{'color': color, 'count': count} for color, count in pixel_count.items()]

        # Merge similar colors
        merged_palette = color_utils.merge_similar_colors([p['color'] for p in palette], threshold)

        # Sort colors by count in descending order
        sorted_palette = sorted(merged_palette, key=lambda x: x['count'], reverse=True)

        # Select top 3 colors (or fewer if less than 3)
        top_colors = sorted_palette[:3]

        # Calculate the average color of the top colors
        if top_colors:
            total_count = sum(c['count'] for c in top_colors)
            avg_color = [
                sum(c['color'][i] * c['count'] for c in top_colors) / total_count
                for i in range(3)
            ]
            main_color_hex = color_utils.rgb_to_hex(avg_color)
        else:
            main_color_hex = "#000000"  # Default to black if no colors are found

        return (main_color_hex,)
