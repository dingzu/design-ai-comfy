import torch

class BlackBorderDetector:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01}),
                "expand": ("INT", {"default": 0, "min": -1000, "max": 1000, "step": 1}),
                "expand_after_crop": ("INT", {"default": 0, "min": -1000, "max": 1000, "step": 1}),
                "ignore_threshold": ("INT", {"default": -1, "min": -1, "max": 1000, "step": 1}),
                "remove_mode": (["black", "all_colors"],),
                "max_iterations": ("INT", {"default": 5, "min": 1, "max": 10, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "width", "height", "top_border", "bottom_border", "left_border", "right_border", "top_border_add", "bottom_border_add", "left_border_add", "right_border_add")

    FUNCTION = "detect_and_crop_border"

    CATEGORY = "✨✨✨design-ai"

    def detect_and_crop_border(self, image, threshold, expand, expand_after_crop, ignore_threshold, remove_mode, max_iterations):
        img = image[0]
        original_height, original_width, _ = img.shape
        
        top_border, bottom_border, left_border, right_border = 0, original_height, 0, original_width
        
        for _ in range(max_iterations):
            new_top, new_bottom, new_left, new_right = self._detect_borders(img, threshold, expand, ignore_threshold, remove_mode)
            
            if new_top == 0 and new_bottom == img.shape[0] and new_left == 0 and new_right == img.shape[1]:
                break  # No new borders detected
            
            top_border += new_top
            bottom_border -= (img.shape[0] - new_bottom)
            left_border += new_left
            right_border -= (img.shape[1] - new_right)
            
            img = img[new_top:new_bottom, new_left:new_right]
        
        final_img = image[0][top_border:bottom_border, left_border:right_border]
        final_img = final_img.unsqueeze(0)
        
        # Apply final expand_after_crop
        top_border, bottom_border, left_border, right_border, top_add, bottom_add, left_add, right_add = self._apply_expand_after_crop(
            top_border, bottom_border, left_border, right_border, original_height, original_width, expand_after_crop
        )
        
        new_height = bottom_border - top_border
        new_width = right_border - left_border
        
        return (final_img, new_width, new_height, top_border, original_height - bottom_border, left_border, original_width - right_border, top_add, bottom_add, left_add, right_add)

    def _detect_borders(self, img, threshold, expand, ignore_threshold, remove_mode):
        height, width, _ = img.shape
        gray = self._compute_gray_image(img, remove_mode)
        
        top_border, bottom_border = self._find_vertical_borders(gray, height, threshold)
        left_border, right_border = self._find_horizontal_borders(gray, width, threshold)
        
        top_border, bottom_border, left_border, right_border = self._apply_ignore_threshold(
            top_border, bottom_border, left_border, right_border, height, width, ignore_threshold
        )
        
        top_border, bottom_border, left_border, right_border = self._apply_expand(
            top_border, bottom_border, left_border, right_border, height, width, expand
        )
        
        return top_border, bottom_border, left_border, right_border

    def _compute_gray_image(self, img, remove_mode):
        if remove_mode == "black":
            return torch.mean(img, dim=2)
        else:
            return torch.sum(torch.abs(img - img[0, 0, :]), dim=2)

    def _find_vertical_borders(self, gray, height, threshold):
        top_border = 0
        bottom_border = height

        for i in range(height):
            if torch.mean(gray[i]) > threshold:
                top_border = i
                break

        for i in range(height - 1, -1, -1):
            if torch.mean(gray[i]) > threshold:
                bottom_border = i + 1
                break

        return top_border, bottom_border

    def _find_horizontal_borders(self, gray, width, threshold):
        left_border = 0
        right_border = width

        for i in range(width):
            if torch.mean(gray[:, i]) > threshold:
                left_border = i
                break

        for i in range(width - 1, -1, -1):
            if torch.mean(gray[:, i]) > threshold:
                right_border = i + 1
                break

        return left_border, right_border

    def _apply_ignore_threshold(self, top_border, bottom_border, left_border, right_border, height, width, ignore_threshold):
        if ignore_threshold > 0:
            if top_border <= ignore_threshold:
                top_border = 0
            if height - bottom_border <= ignore_threshold:
                bottom_border = height
            if left_border <= ignore_threshold:
                left_border = 0
            if width - right_border <= ignore_threshold:
                right_border = width
        return top_border, bottom_border, left_border, right_border

    def _apply_expand(self, top_border, bottom_border, left_border, right_border, height, width, expand):
        if top_border != 0:
            top_border = max(0, top_border + expand)
        if bottom_border != height:
            bottom_border = min(height, bottom_border - expand)
        if left_border != 0:
            left_border = max(0, left_border + expand)
        if right_border != width:
            right_border = min(width, right_border - expand)

        if top_border >= bottom_border:
            top_border = 0
            bottom_border = height
        if left_border >= right_border:
            left_border = 0
            right_border = width

        return top_border, bottom_border, left_border, right_border

    def _apply_expand_after_crop(self, top_border, bottom_border, left_border, right_border, height, width, expand_after_crop):
        top_add = bottom_add = left_add = right_add = 0

        if top_border != 0:
            top_border = max(0, top_border + expand_after_crop)
            top_add = expand_after_crop
        if bottom_border != height:
            bottom_border = min(height, bottom_border - expand_after_crop)
            bottom_add = expand_after_crop
        if left_border != 0:
            left_border = max(0, left_border + expand_after_crop)
            left_add = expand_after_crop
        if right_border != width:
            right_border = min(width, right_border - expand_after_crop)
            right_add = expand_after_crop

        return top_border, bottom_border, left_border, right_border, top_add, bottom_add, left_add, right_add