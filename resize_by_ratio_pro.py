import torch
import numpy as np
from PIL import Image

class ResizeByRatioPro:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "ratio_width": ("INT", {"default": 16, "min": 1, "max": 100}),
                "ratio_height": ("INT", {"default": 9, "min": 1, "max": 100}),
                "keep_dimension": ([
                    "auto",       # 自动选择变化最小的维度
                    "width",      # 保持宽度不变，调整高度
                    "height"      # 保持高度不变，调整宽度
                ],),
                "multiple_of": ("INT", {"default": 8, "min": 1, "max": 128}),
                "pad_color": ("INT", {"default": 0, "min": 0, "max": 255}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height", "expand_top", "expand_bottom", "expand_left", "expand_right")
    FUNCTION = "resize_by_ratio"
    CATEGORY = "✨✨✨design-ai/img"

    def resize_by_ratio(self, image, mask, ratio_width, ratio_height, keep_dimension, multiple_of, pad_color=0):
        # Convert torch tensors to PIL Images
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        mask_img = Image.fromarray((mask.cpu().numpy().squeeze() * 255).astype(np.uint8))

        # Get original dimensions
        orig_width, orig_height = img.size
        target_ratio = ratio_width / ratio_height
        current_ratio = orig_width / orig_height
        
        # Initialize expansion values
        expand_top = expand_bottom = expand_left = expand_right = 0
        
        # Calculate new dimensions based on keep_dimension setting
        if keep_dimension == "width":
            # Keep width, adjust height
            new_width = orig_width
            new_height = int(orig_width / target_ratio)
        elif keep_dimension == "height":
            # Keep height, adjust width  
            new_height = orig_height
            new_width = int(orig_height * target_ratio)
        else:  # auto
            # Choose the dimension that requires less change
            if current_ratio > target_ratio:
                # Current image is wider, keep width and increase height
                new_width = orig_width
                new_height = int(orig_width / target_ratio)
            else:
                # Current image is taller, keep height and increase width
                new_height = orig_height
                new_width = int(orig_height * target_ratio)
        
        # Adjust dimensions to be multiples of multiple_of
        new_width = ((new_width + multiple_of - 1) // multiple_of) * multiple_of
        new_height = ((new_height + multiple_of - 1) // multiple_of) * multiple_of
        
        # Create new images with expanded canvas
        resized_img = Image.new('RGB', (new_width, new_height), (pad_color, pad_color, pad_color))
        resized_mask = Image.new('L', (new_width, new_height), 255)  # 默认蒙版为白色，与原节点保持一致
        
        # Calculate positioning for centering the original image
        x_offset = (new_width - orig_width) // 2
        y_offset = (new_height - orig_height) // 2
        
        # Calculate expansion values
        expand_left = x_offset
        expand_right = new_width - orig_width - x_offset
        expand_top = y_offset  
        expand_bottom = new_height - orig_height - y_offset
        
        # Paste original images onto the new canvas
        resized_img.paste(img, (x_offset, y_offset))
        resized_mask.paste(mask_img, (x_offset, y_offset))

        # Convert back to torch tensors
        resized_image = torch.from_numpy(np.array(resized_img).astype(np.float32) / 255.0).unsqueeze(0)
        resized_mask_tensor = torch.from_numpy(np.array(resized_mask).astype(np.float32) / 255.0)

        return (
            resized_image, 
            resized_mask_tensor, 
            new_width, 
            new_height, 
            expand_top, 
            expand_bottom, 
            expand_left, 
            expand_right
        )

# 注册节点
NODE_CLASS_MAPPINGS = {
    "ResizeByRatioPro": ResizeByRatioPro
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResizeByRatioPro": "Resize By Ratio Pro"
}
