import numpy as np

class TextPositionEstimator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "transformed_json": ("JSON",),
                "image_width": ("INT", {"default": 1000, "min": 1, "max": 10000, "step": 1}),
                "image_height": ("INT", {"default": 1000, "min": 1, "max": 10000, "step": 1}),
                "center_threshold": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("max_area_position", "centroid_position")

    FUNCTION = "estimate_text_position"

    CATEGORY = "✨✨✨design-ai"

    def estimate_text_position(self, transformed_json, image_width, image_height, center_threshold):
        if not isinstance(transformed_json, list):
            return ("failed", "failed")

        try:
            # Algorithm 1: Find the text with the largest area
            max_area = 0
            max_area_position = None
            for item in transformed_json:
                points = item['points']
                width = abs(points[1][0] - points[0][0])
                height = abs(points[1][1] - points[0][1])
                area = width * height
                if area > max_area:
                    max_area = area
                    max_area_position = points

            # Algorithm 2: Calculate the centroid of all text regions
            total_x = 0
            total_y = 0
            total_area = 0
            for item in transformed_json:
                points = item['points']
                width = abs(points[1][0] - points[0][0])
                height = abs(points[1][1] - points[0][1])
                area = width * height
                centroid_x = (points[0][0] + points[1][0]) / 2
                centroid_y = (points[0][1] + points[1][1]) / 2
                total_x += centroid_x * area
                total_y += centroid_y * area
                total_area += area

            centroid_position = [total_x / total_area, total_y / total_area]

            # Determine the position (left, right, center)
            def determine_position(x, width, threshold):
                if x < width * (1 - threshold) / 2:
                    return "left"
                elif x > width * (1 + threshold) / 2:
                    return "right"
                else:
                    return "center"

            max_area_x = (max_area_position[0][0] + max_area_position[1][0]) / 2
            centroid_x = centroid_position[0]

            max_area_result = determine_position(max_area_x, image_width, center_threshold)
            centroid_result = determine_position(centroid_x, image_width, center_threshold)

            return (max_area_result, centroid_result)
        except Exception as e:
            return ("failed", "failed")
