import torch
import numpy as np
from PIL import Image

class ResizeBySidePro:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512, "min": 64, "max": 6048}),
                "apply_to": (["width", "height", "long_edge", "short_edge"],),
                "max_long_edge": ("INT", {"default": 1024, "min": 64, "max": 6048}),
                "multiple_of": ("INT", {"default": 8, "min": 1, "max": 128}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "resize_with_config"
    CATEGORY = "✨✨✨design-ai"

    def resize_with_config(self, image, size, apply_to, max_long_edge, multiple_of):
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Get original dimensions
        orig_width, orig_height = img.size

        # Determine new dimensions based on apply_to
        if apply_to == "width":
            new_width = size
            new_height = int(orig_height * (size / orig_width))
        elif apply_to == "height":
            new_height = size
            new_width = int(orig_width * (size / orig_height))
        elif apply_to == "long_edge":
            if orig_width > orig_height:
                new_width = size
                new_height = int(orig_height * (size / orig_width))
            else:
                new_height = size
                new_width = int(orig_width * (size / orig_height))
        else:  # short_edge
            if orig_width < orig_height:
                new_width = size
                new_height = int(orig_height * (size / orig_width))
            else:
                new_height = size
                new_width = int(orig_width * (size / orig_height))

        # Apply max_long_edge constraint
        if max(new_width, new_height) > max_long_edge:
            scale = max_long_edge / max(new_width, new_height)
            new_width = int(new_width * scale)
            new_height = int(new_height * scale)

        # Adjust dimensions to be multiples of multiple_of
        new_width = (new_width // multiple_of) * multiple_of
        new_height = (new_height // multiple_of) * multiple_of

        # Resize image
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Convert back to torch tensor
        resized_image = torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

        return (resized_image, new_width, new_height)