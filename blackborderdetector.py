import torch

class BlackBorderDetector:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
                "expand": ("INT", {"default": 0, "min": -1000, "max": 1000, "step": 1}),
                "expand_after_crop": ("INT", {"default": 0, "min": -1000, "max": 1000, "step": 1}),
                "ignore_threshold": ("INT", {"default": -1, "min": -1, "max": 1000, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "width", "height", "top_border", "bottom_border", "left_border", "right_border", "top_border_add", "bottom_border_add", "left_border_add", "right_border_add")

    FUNCTION = "detect_and_crop_black_border"

    CATEGORY = "✨✨✨design-ai"

    def detect_and_crop_black_border(self, image, threshold, expand, expand_after_crop, ignore_threshold):
        img = image[0]
        height, width, channels = img.shape
        gray = torch.mean(img, dim=2)

        # 检测边框
        top_border = 0
        bottom_border = height
        left_border = 0
        right_border = width

        # 记录额外拓展值
        top_border_expand_after_crop = 0
        bottom_border_expand_after_crop = 0
        left_border_expand_after_crop = 0
        right_border_expand_after_crop = 0

        for i in range(height):
            if torch.mean(gray[i]) > threshold:
                top_border = i
                break

        for i in range(height - 1, -1, -1):
            if torch.mean(gray[i]) > threshold:
                bottom_border = i + 1
                break

        for i in range(width):
            if torch.mean(gray[:, i]) > threshold:
                left_border = i
                break

        for i in range(width - 1, -1, -1):
            if torch.mean(gray[:, i]) > threshold:
                right_border = i + 1
                break

        # 应用忽略阈值
        if ignore_threshold > 0:
            if top_border <= ignore_threshold:
                top_border = 0
            if height - bottom_border <= ignore_threshold:
                bottom_border = height
            if left_border <= ignore_threshold:
                left_border = 0
            if width - right_border <= ignore_threshold:
                right_border = width

        # 应用扩展值
        if top_border != 0:
            top_border = max(0, top_border + expand)
        if bottom_border != height:
            bottom_border = min(height, bottom_border - expand)
        if left_border != 0:
            left_border = max(0, left_border + expand)
        if right_border != width:
            right_border = min(width, right_border - expand)

        # 确保裁剪区域有效
        if top_border >= bottom_border:
            top_border = 0
            bottom_border = height
        if left_border >= right_border:
            left_border = 0
            right_border = width

        # 裁剪图像
        cropped_img = img[top_border:bottom_border, left_border:right_border, :]
        cropped_img = cropped_img.unsqueeze(0)

        # 裁剪图片后再次拓展
        if top_border != 0:
            top_border = max(0, top_border + expand_after_crop)
            top_border_expand_after_crop = expand_after_crop
        if bottom_border != height:
            bottom_border = min(height, bottom_border - expand_after_crop)
            bottom_border_expand_after_crop = expand_after_crop
        if left_border != 0:
            left_border = max(0, left_border + expand_after_crop)
            left_border_expand_after_crop = expand_after_crop
        if right_border != width:
            right_border = min(width, right_border - expand_after_crop)
            right_border_expand_after_crop = expand_after_crop

        # 计算输出参数
        new_height = bottom_border - top_border
        new_width = right_border - left_border

        return (cropped_img, new_width, new_height, top_border, height - bottom_border, left_border, width - right_border, top_border_expand_after_crop, bottom_border_expand_after_crop, left_border_expand_after_crop, right_border_expand_after_crop)
