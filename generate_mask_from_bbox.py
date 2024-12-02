import torch
import numpy as np
import cv2

class GenerateMaskFromBbox:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bboxes": ("STRING",),  # 输入的边界框字符串
                "width": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "height": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "trapezoid_ratio": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0}),  # 新增的梯形长短边比例
                "scale_x": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0}),  # X轴缩放比例
                "scale_y": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0}),  # Y轴缩放比例
                "shift_x_percent": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),  # X轴位移百分比
                "shift_y_percent": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.01}),  # Y轴位移百分比
                "blur_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0}),  # 模糊百分比
                "rotation_angle": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 0.1}),  # 旋转角度
            },
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "generate_mask_from_bbox"
    CATEGORY = "✨✨✨design-ai/mask"

    def generate_mask_from_bbox(self, bboxes, width, height, trapezoid_ratio, scale_x, scale_y, shift_x_percent, shift_y_percent, blur_percent, rotation_angle):
        # 解析边界框字符串为列表
        bboxes = eval(bboxes)

        # 如果没有任何 bbox 数据，生成一个全黑 mask
        if not bboxes:
            return (torch.zeros((1, height, width), dtype=torch.float32),)

        # Initialize an empty list to store masks
        masks = []

        # Iterate over each bbox list and create a mask for each
        for bbox_list in bboxes:
            for bbox in bbox_list:
                mask = torch.zeros((height, width), dtype=torch.float32)

                # Extract bbox coordinates
                x1, y1, x2, y2 = bbox

                # Ensure bbox coordinates are within the image dimensions
                x1 = max(0, min(x1, width - 1))
                y1 = max(0, min(y1, height - 1))
                x2 = max(0, min(x2, width - 1))
                y2 = max(0, min(y2, height - 1))

                # Calculate the width and height of the bbox
                bbox_width = x2 - x1
                bbox_height = y2 - y1

                # Calculate the width of the top and bottom edges of the trapezoid
                top_width = bbox_width * trapezoid_ratio
                bottom_width = bbox_width

                # Calculate the x-coordinates of the top edge
                top_x1 = x1 + (bottom_width - top_width) / 2
                top_x2 = top_x1 + top_width

                # Ensure the top edge coordinates are within the image dimensions
                top_x1 = max(0, min(top_x1, width - 1))
                top_x2 = max(0, min(top_x2, width - 1))

                # Apply scaling
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                x1 = center_x + (x1 - center_x) * scale_x
                x2 = center_x + (x2 - center_x) * scale_x
                y1 = center_y + (y1 - center_y) * scale_y
                y2 = center_y + (y2 - center_y) * scale_y
                top_x1 = center_x + (top_x1 - center_x) * scale_x
                top_x2 = center_x + (top_x2 - center_x) * scale_x

                # Apply shifting
                shift_x = bbox_width * shift_x_percent
                shift_y = bbox_height * shift_y_percent
                x1 += shift_x
                x2 += shift_x
                y1 += shift_y
                y2 += shift_y
                top_x1 += shift_x
                top_x2 += shift_x

                # Apply rotation
                if rotation_angle != 0.0:
                    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), rotation_angle, 1.0)
                    points = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2], [top_x1, y1], [top_x2, y1]])
                    rotated_points = cv2.transform(np.array([points]), rotation_matrix)[0]
                    x1, y1 = rotated_points[0]
                    x2, y1 = rotated_points[1]
                    x2, y2 = rotated_points[2]
                    x1, y2 = rotated_points[3]
                    top_x1, y1 = rotated_points[4]
                    top_x2, y1 = rotated_points[5]

                # Draw the trapezoid on the mask
                for y in range(int(y1), int(y2)):
                    if y < 0 or y >= height:
                        continue  # Skip rows that are out of bounds

                    # Calculate the x-coordinates of the current row
                    current_x1 = int(top_x1 + (x1 - top_x1) * (y - y1) / (y2 - y1))
                    current_x2 = int(top_x2 + (x2 - top_x2) * (y - y1) / (y2 - y1))

                    # Ensure the current row coordinates are within the image dimensions
                    current_x1 = max(0, min(current_x1, width - 1))
                    current_x2 = max(0, min(current_x2, width - 1))

                    # Set the mask values to 1 within the current row
                    mask[y, current_x1:current_x2] = 1.0

                # Apply blur
                if blur_percent > 0:
                    blur_radius = int(bbox_width * blur_percent)
                    mask = self.apply_blur(mask, blur_radius)

                # Append the mask to the list
                masks.append(mask)

        # Stack all masks to create a batch
        masks_batch = torch.stack(masks, dim=0)

        return (masks_batch,)

    def apply_blur(self, mask, radius):
        mask_np = mask.numpy()
        mask_np = cv2.GaussianBlur(mask_np, (radius * 2 + 1, radius * 2 + 1), 0)
        return torch.from_numpy(mask_np)