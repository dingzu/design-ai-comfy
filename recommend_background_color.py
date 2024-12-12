import ast
import colorsys

class RecommendBackgroundColor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "color_list": ("STRING", {"multiline": True}),
                "dominant_threshold": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.01}),
                "default_background": ("STRING", {"default": "#F5F5F5"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("recommended_background",)
    FUNCTION = "recommend_background"
    CATEGORY = "✨✨✨design-ai/color"

    def recommend_background(self, color_list, dominant_threshold, default_background):
        try:
            # Convert the input string to a Python list
            color_data = ast.literal_eval(color_list)
            
            # Sort colors by percentage in descending order
            sorted_colors = sorted(color_data, key=lambda x: float(x[1].strip('%')), reverse=True)
            
            if not sorted_colors:
                return (default_background,)
            
            dominant_color = sorted_colors[0]
            dominant_percentage = float(dominant_color[1].strip('%')) / 100
            
            if dominant_percentage > dominant_threshold:
                # Generate a light version of the dominant color
                rgb = self.hex_to_rgb(dominant_color[0])
                h, s, v = colorsys.rgb_to_hsv(*rgb)
                light_color = colorsys.hsv_to_rgb(h, s * 0.3, min(1, v * 1.5))
                return (self.rgb_to_hex(light_color),)
            else:
                # Use the default background color
                return (default_background,)
        
        except Exception as e:
            print(f"Error recommending background color: {e}")
            return (default_background,)  # Return default background in case of error

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))