import torch
import numpy as np
import cv2

class TransformBbox:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bboxes": ("STRING",),  # 输入的边界框字符串
                "scale_x": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0}),  # X轴缩放比例
                "scale_y": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0}),  # Y轴缩放比例
                "shift_x_percent": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),  # X轴位移百分比
                "shift_y_percent": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),  # Y轴位移百分比
                "rotation_angle": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 0.1}),  # 旋转角度
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "transform_bbox"
    CATEGORY = "✨✨✨design-ai/mask"

    def transform_bbox(self, bboxes, scale_x, scale_y, shift_x_percent, shift_y_percent, rotation_angle):
        # 解析边界框字符串为列表
        bboxes = eval(bboxes)

        # 如果没有任何 bbox 数据，返回空字符串
        if not bboxes:
            return ("[]",)

        # Initialize an empty list to store transformed bbox vertices
        transformed_bboxes = []

        # Iterate over each bbox list and transform each
        for bbox_list in bboxes:
            for bbox in bbox_list:
                # Extract bbox coordinates
                x1, y1, x2, y2 = bbox

                # Calculate the width and height of the bbox
                bbox_width = x2 - x1
                bbox_height = y2 - y1

                # Calculate the center of the bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                # Define the four vertices of the rectangle
                vertices = np.array([
                    [x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x1, y2]
                ], dtype=np.float32)  # 将数据类型显式转换为float32

                # Apply scaling
                vertices[:, 0] = center_x + (vertices[:, 0] - center_x) * scale_x
                vertices[:, 1] = center_y + (vertices[:, 1] - center_y) * scale_y

                # Apply shifting
                shift_x = bbox_width * shift_x_percent
                shift_y = bbox_height * shift_y_percent
                vertices[:, 0] += shift_x
                vertices[:, 1] += shift_y

                # Apply rotation
                if rotation_angle != 0.0:
                    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), rotation_angle, 1.0)
                    vertices = cv2.transform(np.array([vertices]), rotation_matrix)[0]

                # Append the transformed vertices to the list
                transformed_bboxes.append(vertices.tolist())

        # Convert the list to a string
        transformed_bboxes_str = str(transformed_bboxes)

        return (transformed_bboxes_str,)