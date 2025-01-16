import torch
import base64
from PIL import Image
import io
import numpy as np

class ImageBase64Node:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_string",)
    FUNCTION = "convert_to_base64"
    CATEGORY = "✨✨✨design-ai/img"

    @torch.no_grad()
    def convert_to_base64(self, image: torch.Tensor, quality: int) -> tuple:
        try:
            # 如果tensor在GPU上，保持在GPU上进行处理
            if image.ndim == 4:
                image = image[0]
            
            # 在GPU上进行值范围裁剪和缩放
            if image.device.type == 'cuda':
                image = (image * 255).clamp(0, 255)
                image_np = image.cpu().numpy().astype(np.uint8)
            else:
                image = (image * 255).clamp(0, 255)
                image_np = image.numpy().astype(np.uint8)

            # 使用buffer直接在内存中处理图像
            buffer = io.BytesIO()
            Image.fromarray(image_np).save(buffer, format="JPEG", quality=quality, optimize=True)
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            
            return (base64_string,)

        except Exception as e:
            print(f"Error in convert_to_base64: {e}")
            return ("",)