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
                "remove_mode": (["black", "all_colors"],),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "width", "height", "top_border", "bottom_border", "left_border", "right_border", "top_border_add", "bottom_border_add", "left_border_add", "right_border_add")

    FUNCTION = "detect_and_crop_border"

    CATEGORY = "✨✨✨design-ai"

    def detect_and_crop_border(self, image, threshold, expand, expand_after_crop, ignore_threshold, remove_mode):
        def crop_once(img, mode):
            gray = torch.mean(img, dim=2) if mode == "black" else torch.sum(torch.abs(img - img[0, 0, :]), dim=2)
            # 假设初始化边框与颜色无关
            top_border, bottom_border = 0, img.shape[0]
            left_border, right_border = 0, img.shape[1]

            while True:
                new_top_border, new_bottom_border = top_border, bottom_border
                new_left_border, new_right_border = left_border, right_border

                for i in range(top_border, bottom_border):
                    if torch.mean(gray[i, left_border:right_border]) > threshold:
                        new_top_border = i
                        break

                for i in range(bottom_border - 1, top_border - 1, -1):
                    if torch.mean(gray[i, left_border:right_border]) > threshold:
                        new_bottom_border = i + 1
                        break

                for i in range(left_border, right_border):
                    if torch.mean(gray[top_border:bottom_border, i]) > threshold:
                        new_left_border = i
                        break

                for i in range(right_border - 1, left_border - 1, -1):
                    if torch.mean(gray[top_border:bottom_border, i]) > threshold:
                        new_right_border = i + 1
                        break

                if (new_top_border == top_border and new_bottom_border == bottom_border and
                    new_left_border == left_border and new_right_border == right_border):
                    break

                top_border, bottom_border = new_top_border, new_bottom_border
                left_border, right_border = new_left_border, new_right_border

            return (top_border, bottom_border, left_border, right_border)

        img = image[0]
        height, width, channels = img.shape

        modes = ["black", "all_colors"]
        borders = [None, None, None, None]
        for mode in modes:
            top, bottom, left, right = crop_once(img, mode)
            borders[0] = max(borders[0] or top, top)
            borders[1] = min(borders[1] or bottom, bottom)
            borders[2] = max(borders[2] or left, left)
            borders[3] = min(borders[3] or right, right)

        cropped_img = img[borders[0]:borders[1], borders[2]:borders[3], :]
        cropped_img = cropped_img.unsqueeze(0)

        new_height = borders[1] - borders[0]
        new_width = borders[3] - borders[2]
        
        return (cropped_img, new_width, new_height, borders[0], height - borders[1], borders[2], width - borders[3], 0, 0, 0, 0)