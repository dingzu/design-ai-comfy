import torch
import numpy as np
from PIL import Image

class ResizeAndCenter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "height": ("INT", {"default": 512, "min": 64, "max": 6048}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("image", "top_border", "bottom_border", "left_border", "right_border")
    FUNCTION = "resize_and_center"
    CATEGORY = "✨✨✨design-ai"

    def resize_and_center(self, image, width, height):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Calculate aspect ratios
        target_aspect = width / height
        img_aspect = img.width / img.height

        # Resize image
        if img_aspect > target_aspect:
            # Fit to width
            new_width = width
            new_height = int(width / img_aspect)
        else:
            # Fit to height
            new_height = height
            new_width = int(height * img_aspect)
        
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Calculate border sizes
        left_border = (width - new_width) // 2
        right_border = width - new_width - left_border
        top_border = (height - new_height) // 2
        bottom_border = height - new_height - top_border

        # Create new image with target size and black background
        new_img = Image.new('RGB', (width, height), color='black')

        # Paste resized image onto new image (centered)
        paste_x = left_border
        paste_y = top_border
        new_img.paste(img, (paste_x, paste_y))

        # Convert back to torch tensor
        tensor_img = torch.from_numpy(np.array(new_img).astype(np.float32) / 255.0).unsqueeze(0)

        return (tensor_img, top_border, bottom_border, left_border, right_border)