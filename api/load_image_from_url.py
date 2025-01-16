import torch
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import time

class LoadImageFromURL:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
                "fallback_image": ("IMAGE",),
                "timeout": ("FLOAT", {
                    "default": 10.0,
                    "min": 1.0,
                    "max": 60.0,
                    "step": 0.1
                }),
                "max_retries": ("INT", {
                    "default": 3,
                    "min": 0,
                    "max": 10,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING")
    RETURN_NAMES = ("output_image", "success", "message")
    FUNCTION = "load_image"
    CATEGORY = "✨✨✨design-ai/api"

    def load_image(self, url, fallback_image, timeout, max_retries):
        message = ""
        success = False
        output_image = fallback_image

        # 尝试从URL加载图片
        retry_count = 0
        while retry_count <= max_retries:
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    # 从响应内容加载图片
                    image = Image.open(BytesIO(response.content))
                    
                    # 转换为RGB模式（如果是RGBA，去掉alpha通道）
                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1])
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 转换为numpy数组并归一化
                    np_image = np.array(image).astype(np.float32) / 255.0
                    
                    # 确保图像是RGB格式，并添加batch维度
                    if len(np_image.shape) == 2:  # 如果是灰度图像
                        np_image = np.stack([np_image] * 3, axis=-1)
                    
                    # 添加batch维度 [height, width, channels] -> [1, height, width, channels]
                    np_image = np_image[None, ...]
                    
                    # 将numpy数组转换为PyTorch tensor，保持[B,H,W,C]格式
                    output_image = torch.from_numpy(np_image)
                    
                    success = True
                    message = "Image loaded successfully"
                    break
                else:
                    message = f"HTTP error {response.status_code}"
            except requests.Timeout:
                message = f"Request timed out (attempt {retry_count + 1}/{max_retries + 1})"
            except requests.RequestException as e:
                message = f"Request error: {str(e)}"
            except Exception as e:
                message = f"Unexpected error: {str(e)}"
            
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(1)  # 重试前等待1秒

        if not success:
            message = f"Failed to load image after {max_retries + 1} attempts. Using fallback image. Error: {message}"

        # 确保fallback_image也是正确的格式
        if not success and not isinstance(output_image, torch.Tensor):
            output_image = torch.from_numpy(output_image)
        if len(output_image.shape) == 3:  # 如果没有batch维度
            output_image = output_image.unsqueeze(0)

        return (output_image, success, message)