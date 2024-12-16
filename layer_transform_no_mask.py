import torch
import numpy as np
from PIL import Image

class LayerTransformNoMask:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
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

    def transform_layer(self, image, offset_x, offset_y, offset_x_percent, offset_y_percent, 
                       rotation_angle, background_color):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        # Get dimensions
        width, height = img.size
        
        # Calculate final offsets (percent takes precedence)
        final_offset_x = offset_x
        final_offset_y = offset_y
        
        if abs(offset_x_percent) > 0:
            final_offset_x = int(width * offset_x_percent / 100)
        if abs(offset_y_percent) > 0:
            final_offset_y = int(height * offset_y_percent / 100)
            
        # Create new image with background color
        new_img = Image.new('RGB', (width, height), (background_color, background_color, background_color))
        # Create new mask (255 for new areas)
        new_mask = Image.new('L', (width, height), 255)
        
        # If there's rotation, handle it first
        if rotation_angle != 0:
            # Rotate image
            img = img.rotate(rotation_angle, Image.BICUBIC, expand=False)
        
        # Calculate paste coordinates
        paste_x = final_offset_x
        paste_y = final_offset_y
        
        # Handle negative offsets
        if paste_x < 0:
            img = img.crop((-paste_x, 0, width, height))
            paste_x = 0
        if paste_y < 0:
            img = img.crop((0, -paste_y, width, height))
            paste_y = 0
            
        # Handle offsets that would push the image out of bounds
        if paste_x + img.width > width:
            img = img.crop((0, 0, width - paste_x, height))
        if paste_y + img.height > height:
            img = img.crop((0, 0, width, height - paste_y))
        
        # Create a mask for the pasted area (0 for content area)
        content_mask = Image.new('L', img.size, 0)
        
        # Paste the transformed image and update mask
        new_img.paste(img, (paste_x, paste_y))
        new_mask.paste(content_mask, (paste_x, paste_y))
        
        # Convert back to torch tensors
        transformed_image = torch.from_numpy(np.array(new_img).astype(np.float32) / 255.0).unsqueeze(0)
        transformed_mask = torch.from_numpy(np.array(new_mask).astype(np.float32) / 255.0).unsqueeze(0)
        
        return (transformed_image, transformed_mask)