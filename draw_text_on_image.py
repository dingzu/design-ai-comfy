import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .utils import color_utils

class DrawTextOnImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING",),
                "color_hex": ("STRING",),
                "font_size": ("INT", {"default": 40, "min": 10, "max": 200}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_with_text",)
    FUNCTION = "draw_text_on_image"
    CATEGORY = "✨✨✨design-ai/test"

    def draw_text_on_image(self, image, text, color_hex, font_size):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Create a drawing context
        draw = ImageDraw.Draw(img)
        color = color_utils.hex_to_rgb(color_hex)

        # Load a font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (img.width - text_width) // 2
        text_y = (img.height - text_height) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, fill=color, font=font)

        # Convert back to torch tensor
        tensor_img = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

        return (tensor_img,)
