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
                "border_color": (["black", "auto"],),  # 新增选项
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("image", "top_border", "bottom_border", "left_border", "right_border")
    FUNCTION = "resize_and_center"
    CATEGORY = "✨✨✨design-ai"

    def resize_and_center(self, image, width, height, border_color):
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

        # Determine border color
        if border_color == "auto":
            # Convert image to numpy array
            img_np = np.array(img)
            img_tensor = torch.from_numpy(img_np.astype(np.float32) / 255.0)

            # Calculate color differences
            left_diff = torch.sum(torch.abs(img_tensor[:, 0, :] - img_tensor[0, 0, :]), dim=1)
            right_diff = torch.sum(torch.abs(img_tensor[:, -1, :] - img_tensor[0, 0, :]), dim=1)
            top_diff = torch.sum(torch.abs(img_tensor[0, :, :] - img_tensor[0, 0, :]), dim=1)
            bottom_diff = torch.sum(torch.abs(img_tensor[-1, :, :] - img_tensor[0, 0, :]), dim=1)

            # Calculate mean color differences
            left_color_diff = torch.mean(left_diff).item()
            right_color_diff = torch.mean(right_diff).item()
            top_color_diff = torch.mean(top_diff).item()
            bottom_color_diff = torch.mean(bottom_diff).item()

            # Choose the edge with the smallest color difference
            min_diff = min(left_color_diff, right_color_diff, top_color_diff, bottom_color_diff)
            if min_diff == left_color_diff:
                border_color = tuple(np.mean(img_np[:, 0, :], axis=0).astype(int))
            elif min_diff == right_color_diff:
                border_color = tuple(np.mean(img_np[:, -1, :], axis=0).astype(int))
            elif min_diff == top_color_diff:
                border_color = tuple(np.mean(img_np[0, :, :], axis=0).astype(int))
            else:
                border_color = tuple(np.mean(img_np[-1, :, :], axis=0).astype(int))
        else:
            border_color = 'black'

        # Create new image with target size and specified background color
        new_img = Image.new('RGB', (width, height), color=border_color)

        # Paste resized image onto new image (centered)
        paste_x = left_border
        paste_y = top_border
        new_img.paste(img, (paste_x, paste_y))

        # Convert back to torch tensor
        tensor_img = torch.from_numpy(np.array(new_img).astype(np.float32) / 255.0).unsqueeze(0)

        return (tensor_img, top_border, bottom_border, left_border, right_border)