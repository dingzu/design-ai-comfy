import torch
import numpy as np
from PIL import Image

class ResizeImgAndMaskPro:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "width": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "height": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "resize_mode": ([
                    "scale_by_width",           # 根据宽度和原比例自动缩放
                    "scale_by_height",          # 根据高度和原比例自动缩放
                    "scale_by_long_edge",       # 根据长边和比例自动缩放
                    "scale_by_short_edge",      # 根据短边和比例自动缩放
                    "stretch",                  # 拉伸到指定尺寸
                    "fit_with_padding",         # 保持比例填充
                    "fill_and_crop"             # 保持比例裁剪
                ],),
                "multiple_of": ("INT", {"default": 8, "min": 1, "max": 128}),
                "pad_color": ("INT", {"default": 0, "min": 0, "max": 255}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "resize_with_mask"
    CATEGORY = "✨✨✨design-ai/img"

    def resize_with_mask(self, image, mask, width, height, resize_mode, multiple_of, pad_color=0):
        # Convert torch tensors to PIL Images
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        mask_img = Image.fromarray((mask.cpu().numpy().squeeze() * 255).astype(np.uint8))
        
        # Ensure mask size matches image size
        if mask_img.size != img.size:
            mask_img = mask_img.resize(img.size, Image.LANCZOS)

        # Get original dimensions
        orig_width, orig_height = img.size
        new_width, new_height = width, height

        # Calculate dimensions based on resize mode
        if resize_mode in ["scale_by_width", "scale_by_height", "scale_by_long_edge", "scale_by_short_edge"]:
            if resize_mode == "scale_by_width":
                scale = width / orig_width
                new_height = int(orig_height * scale)
            elif resize_mode == "scale_by_height":
                scale = height / orig_height
                new_width = int(orig_width * scale)
            elif resize_mode == "scale_by_long_edge":
                target = width if orig_width > orig_height else height
                scale = target / max(orig_width, orig_height)
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
            else:  # scale_by_short_edge
                target = width if orig_width < orig_height else height
                scale = target / min(orig_width, orig_height)
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)

        # Adjust dimensions to be multiples of multiple_of
        new_width = (new_width // multiple_of) * multiple_of
        new_height = (new_height // multiple_of) * multiple_of

        if resize_mode == "stretch":
            # Simply resize to target dimensions
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_mask = mask_img.resize((new_width, new_height), Image.LANCZOS)

        elif resize_mode == "fit_with_padding":
            # Calculate scaling factor to fit within target size
            scale = min(width / orig_width, height / orig_height)
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)
            
            # Adjust to multiple_of
            scaled_width = (scaled_width // multiple_of) * multiple_of
            scaled_height = (scaled_height // multiple_of) * multiple_of

            # Create new images with padding
            resized_img = Image.new('RGB', (new_width, new_height), (pad_color, pad_color, pad_color))
            resized_mask = Image.new('L', (new_width, new_height), 255)

            # Resize original images
            temp_img = img.resize((scaled_width, scaled_height), Image.LANCZOS)
            temp_mask = mask_img.resize((scaled_width, scaled_height), Image.LANCZOS)

            # Calculate padding
            x_offset = (new_width - scaled_width) // 2
            y_offset = (new_height - scaled_height) // 2

            # Paste resized images onto padded canvas
            resized_img.paste(temp_img, (x_offset, y_offset))
            resized_mask.paste(temp_mask, (x_offset, y_offset))

        else:  # fill_and_crop
            # Calculate scaling factor to fill target size
            scale = max(width / orig_width, height / orig_height)
            scaled_width = int(orig_width * scale)
            scaled_height = int(orig_height * scale)

            # Resize images
            temp_img = img.resize((scaled_width, scaled_height), Image.LANCZOS)
            temp_mask = mask_img.resize((scaled_width, scaled_height), Image.LANCZOS)

            # Calculate crop coordinates
            x_offset = (scaled_width - new_width) // 2
            y_offset = (scaled_height - new_height) // 2

            # Crop to target size
            resized_img = temp_img.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))
            resized_mask = temp_mask.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))

        # Convert back to torch tensors
        resized_image = torch.from_numpy(np.array(resized_img).astype(np.float32) / 255.0).unsqueeze(0)
        resized_mask = torch.from_numpy(np.array(resized_mask).astype(np.float32) / 255.0)

        return (resized_image, resized_mask, new_width, new_height) 