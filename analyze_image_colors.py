import numpy as np
from PIL import Image
from collections import Counter
from sklearn.cluster import KMeans
import torch

class AnalyzeImageColors:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),  # 新增的 MASK 输入
                "threshold": ("INT", {"default": 30, "min": 0, "max": 255}),
                "ignore_neutral_colors": ("FLOAT", {"default": 0, "min": 0, "max": 1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("color_analysis_with_neutral", "color_analysis_without_neutral")
    FUNCTION = "analyze_image_colors"
    CATEGORY = "✨✨✨design-ai/color"

    def analyze_image_colors(self, image, mask, threshold, ignore_neutral_colors):
        # Move image and mask to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        image = image.to(device)
        mask = mask.to(device)

        # Convert torch tensor to numpy array
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Resize image and mask to reduce processing time
        img = img.resize((100, 100))
        mask = torch.nn.functional.interpolate(mask.unsqueeze(0), size=(100, 100), mode='nearest').squeeze(0)

        # Get image pixels and apply mask
        pixels = np.array(img.getdata())
        mask_np = mask.cpu().numpy().flatten()
        masked_pixels = pixels[mask_np <= 0.5]  # Only consider pixels where mask is active

        # Use KMeans to cluster the colors
        if len(masked_pixels) == 0:
            return ("No valid pixels to analyze", "No valid pixels to analyze")

        kmeans = KMeans(n_clusters=10, random_state=0)
        kmeans.fit(masked_pixels)
        cluster_centers = kmeans.cluster_centers_
        labels = kmeans.labels_

        # Count occurrences of each cluster
        label_counts = Counter(labels)
        total_pixels = sum(label_counts.values())

        # Create a palette with the representative colors and their percentages
        palette = [{'color': cluster_centers[i], 'percentage': label_counts[i] / total_pixels} for i in range(10)]

        # Merge similar colors
        merged_palette = self.merge_similar_colors(palette, threshold)

        # Generate both outputs
        color_analysis_with_neutral = self.generate_color_analysis(merged_palette, ignore_neutral_colors, False)
        color_analysis_without_neutral = self.generate_color_analysis(merged_palette, ignore_neutral_colors, True)

        return (str(color_analysis_with_neutral), str(color_analysis_without_neutral))

    def generate_color_analysis(self, palette, ignore_neutral_colors, filter_neutral):
        if filter_neutral:
            filtered_palette = self.filter_neutral_colors(palette, ignore_neutral_colors)
            if not filtered_palette:
                filtered_palette = self.filter_neutral_colors(palette, 1 - ignore_neutral_colors)
        else:
            filtered_palette = palette

        # Recalculate percentages
        total_percentage = sum(color['percentage'] for color in filtered_palette)
        for color in filtered_palette:
            color['percentage'] /= total_percentage

        # Sort colors by percentage in descending order
        sorted_palette = sorted(filtered_palette, key=lambda x: x['percentage'], reverse=True)

        # Select top 5 colors (or fewer if less than 5)
        top_colors = sorted_palette[:5]

        # Create simplified output
        return [
            [self.rgb_to_hex(color['color']), f"{color['percentage']*100:.1f}%"]
            for color in top_colors
        ]

    def merge_similar_colors(self, palette, threshold):
        merged = []
        for color in palette:
            for merged_color in merged:
                if self.color_distance(color['color'], merged_color['color']) < threshold:
                    merged_color['percentage'] += color['percentage']
                    merged_color['color'] = (merged_color['color'] + color['color']) / 2
                    break
            else:
                merged.append(color)
        return merged

    def filter_neutral_colors(self, palette, threshold):
        return [color for color in palette if not self.is_neutral_color(color['color'], threshold)]

    def is_neutral_color(self, color, threshold):
        r, g, b = color
        # Check if the color is close to gray (all channels similar)
        max_diff = max(abs(r - g), abs(r - b), abs(g - b))
        return max_diff < (255 * threshold)

    def color_distance(self, color1, color2):
        return np.sqrt(np.sum((color1 - color2) ** 2))

    def rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))