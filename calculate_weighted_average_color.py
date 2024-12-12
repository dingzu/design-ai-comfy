import ast
import numpy as np

class CalculateWeightedAverageColor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "color_list": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("average_color",)
    FUNCTION = "calculate_average_color"
    CATEGORY = "✨✨✨design-ai/color"

    def calculate_average_color(self, color_list):
        try:
            # Convert the input string to a Python list
            color_data = ast.literal_eval(color_list)
            
            # Convert hex colors to RGB and percentages to floats
            colors_and_weights = [
                (self.hex_to_rgb(color), float(percentage.strip('%')) / 100)
                for color, percentage in color_data
            ]
            
            # Calculate weighted average
            total_weight = sum(weight for _, weight in colors_and_weights)
            weighted_sum = np.sum([
                np.array(color) * weight for color, weight in colors_and_weights
            ], axis=0)
            
            average_color = weighted_sum / total_weight
            
            # Convert back to hex
            return (self.rgb_to_hex(average_color),)
        
        except Exception as e:
            print(f"Error calculating average color: {e}")
            return ("#FFFFFF",)  # Return black in case of error

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))