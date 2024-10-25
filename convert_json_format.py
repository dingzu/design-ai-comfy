import math
import numpy as np

class ConvertJsonFormat:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_data": ("JSON",),
                "canvas_width": ("INT", {"default": 1000, "min": 1, "max": 10000, "step": 1}),
                "canvas_height": ("INT", {"default": 1000, "min": 1, "max": 10000, "step": 1}),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("transformed_json",)

    FUNCTION = "transform_json"

    CATEGORY = "✨✨✨design-ai"

    def transform_json(self, json_data, canvas_width, canvas_height):
        def rotate_and_restore_points(current_box, angle):
            radians = (-angle * math.pi) / 180
            centerX = current_box[0]
            centerY = current_box[1]
            rotation_matrix = np.array([
                [math.cos(radians), -math.sin(radians)],
                [math.sin(radians), math.cos(radians)],
            ])
            rotated_box = []
            for i in range(0, len(current_box), 2):
                point = np.array([
                    [current_box[i] - centerX],
                    [current_box[i + 1] - centerY],
                ])
                rotated_point = np.dot(rotation_matrix, point)
                rotated_box.append(rotated_point[0, 0] + centerX)
                rotated_box.append(rotated_point[1, 0] + centerY)
            return rotated_box

        transformed_data = []
        for item in json_data:
            x1, y1, x2, y2, x3, y3, x4, y4 = item['box']
            angle = math.atan2(y2 - y1, x2 - x1) * (180 / math.pi)
            origin_box = rotate_and_restore_points(
                [value * (canvas_width if index % 2 == 0 else canvas_height) for index, value in enumerate(item['box'])],
                angle,
            )
            points = [
                [origin_box[0], origin_box[1]],
                [origin_box[4], origin_box[5]],
            ]
            transformed_item = {
                "label": item['label'].replace('</s>', ''),
                "threshold": 0.1,
                "points": points,
                "rotation": angle,
            }
            transformed_data.append(transformed_item)

        return (transformed_data,)