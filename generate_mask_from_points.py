import torch
import numpy as np
import cv2

class GenerateMaskFromPoints:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "points": ("STRING",),  # 输入的点坐标字符串
                "width": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "height": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "blur_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),  # 模糊百分比
            },
        }

    RETURN_TYPES = ("MASK",)
    FUNCTION = "generate_mask_from_points"
    CATEGORY = "✨✨✨design-ai/mask"

    def generate_mask_from_points(self, points, width, height, blur_percent):
        # 解析点坐标字符串为列表
        points = eval(points)

        # 过滤掉非数字内容的点
        valid_points = []
        for point in points:
            if isinstance(point, (list, tuple)) and len(point) == 2:
                x, y = point
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    valid_points.append((int(x), int(y)))

        # 如果有效点的数量小于等于 2，生成纯色的 mask
        if len(valid_points) <= 2:
            mask = torch.zeros((height, width), dtype=torch.float32)
            return (mask.unsqueeze(0),)

        # 创建一个空白的 mask
        mask = torch.zeros((height, width), dtype=torch.float32)

        # 将有效点坐标转换为 numpy 数组
        valid_points = np.array(valid_points, dtype=np.int32)

        # 绘制多边形
        cv2.fillPoly(mask.numpy(), [valid_points], 1.0)

        # 应用模糊
        if blur_percent > 0:
            blur_radius = int(min(width, height) * blur_percent)
            mask = self.apply_blur(mask, blur_radius)

        return (mask.unsqueeze(0),)

    def apply_blur(self, mask, radius):
        mask_np = mask.numpy()
        mask_np = cv2.GaussianBlur(mask_np, (radius * 2 + 1, radius * 2 + 1), 0)
        return torch.from_numpy(mask_np)