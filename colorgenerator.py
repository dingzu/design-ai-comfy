import numpy as np
from PIL import Image
from collections import Counter
from sklearn.cluster import KMeans
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
    CATEGORY = "✨✨✨design-ai/color"

    def analyze_and_extract_main_color(self, image, threshold):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Get image pixels
        pixels = np.array(img.getdata())

        # Count occurrences of each color
        pixel_count = Counter(map(tuple, pixels))
        unique_colors = list(pixel_count.keys())

        if len(unique_colors) > 10:
            # Use KMeans to cluster the colors into 10 representative colors
            kmeans = KMeans(n_clusters=10)
            kmeans.fit(pixels)
            cluster_centers = kmeans.cluster_centers_
            labels = kmeans.labels_

            # Count occurrences of each cluster
            label_counts = Counter(labels)
            total_count = sum(label_counts.values())

            # Create a palette with the representative colors and their counts
            palette = [{'color': cluster_centers[i], 'count': label_counts[i]} for i in range(10)]
        else:
            # If there are fewer than 10 unique colors, use them directly
            palette = [{'color': np.array(color), 'count': count} for color, count in pixel_count.items()]

        # Merge similar colors
        merged_palette = color_utils.merge_similar_colors([p['color'] for p in palette], threshold)

        # Sort colors by count in descending order
        sorted_palette = sorted(merged_palette, key=lambda x: x['count'], reverse=True)

        # Select top 3 colors (or fewer if less than 3)
        top_colors = sorted_palette[:3]

        # Calculate the weighted average color of the top colors
        if top_colors:
            total_count = sum(c['count'] for c in top_colors)
            weighted_avg_color = [
                sum(c['color'][i] * c['count'] for c in top_colors) / total_count
                for i in range(3)
            ]
            main_color_hex = color_utils.rgb_to_hex(weighted_avg_color)
        else:
            main_color_hex = "#000000"  # Default to black if no colors are found

        return (main_color_hex,)