import torch
import numpy as np
from PIL import Image
import math

class LayerTransform: 
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "offset_x": ("INT", {"default": 0, "min": -4096, "max": 4096}),
                "offset_y": ("INT", {"default": 0, "min": -4096, "max": 4096}),
                "offset_x_percent": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0}),
                "offset_y_percent": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0}),
                "rotation_angle": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0}),
                "background_color": ("INT", {"default": 0, "min": 0, "max": 255}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "transform_layer"
    CATEGORY = "✨✨✨design-ai/layer"

    def transform_layer(self, image, mask, offset_x, offset_y, offset_x_percent, offset_y_percent, 
                       rotation_angle, background_color):
        # Convert torch tensors to PIL Images
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        # Invert mask values (255 - mask) so that white is empty and black is content
        mask_img = Image.fromarray(255 - (mask.cpu().numpy().squeeze() * 255).astype(np.uint8))
        
        # Get dimensions
        width, height = img.size
        
        # Calculate final offsets (percent takes precedence)
        final_offset_x = offset_x
        final_offset_y = offset_y
        
        if abs(offset_x_percent) > 0:
            final_offset_x = int(width * offset_x_percent / 100 + offset_x)
        if abs(offset_y_percent) > 0:
            final_offset_y = int(height * offset_y_percent / 100 +offset_y)
            
        # Create new images with background color
        new_img = Image.new('RGB', (width, height), (background_color, background_color, background_color))
        new_mask = Image.new('L', (width, height), 0)  # 0 means empty/background in mask
        
        # If there's rotation, handle it first
        if rotation_angle != 0:
            # Rotate images
            img = img.rotate(rotation_angle, Image.BICUBIC, expand=False)
            mask_img = mask_img.rotate(rotation_angle, Image.BICUBIC, expand=False)
        
        # Calculate paste coordinates
        paste_x = final_offset_x
        paste_y = final_offset_y
        
        # Handle negative offsets and offsets that would push the image out of bounds
        if paste_x < 0:
            img = img.crop((-paste_x, 0, width, height))
            mask_img = mask_img.crop((-paste_x, 0, width, height))
            paste_x = 0
        if paste_y < 0:
            img = img.crop((0, -paste_y, width, height))
            mask_img = mask_img.crop((0, -paste_y, width, height))
            paste_y = 0
        if paste_x + img.width > width:
            img = img.crop((0, 0, width - paste_x, img.height))
            mask_img = mask_img.crop((0, 0, width - paste_x, mask_img.height))
        if paste_y + img.height > height:
            img = img.crop((0, 0, img.width, height - paste_y))
            mask_img = mask_img.crop((0, 0, mask_img.width, height - paste_y))
        
        # Paste the transformed images
        new_img.paste(img, (paste_x, paste_y))
        new_mask.paste(mask_img, (paste_x, paste_y))
        
        # Convert back to torch tensors
        transformed_image = torch.from_numpy(np.array(new_img).astype(np.float32) / 255.0).unsqueeze(0)
        # Invert mask back before returning (255 - mask)
        transformed_mask = torch.from_numpy((255 - np.array(new_mask)).astype(np.float32) / 255.0)
        
        return (transformed_image, transformed_mask)