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
                "use_proxy": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否使用代理服务器"
                }),
            },
            "optional": {
                "token": ("STRING", {
                    "default": "",
                    "tooltip": "用于认证的Bearer Token（如果需要）"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING")
    RETURN_NAMES = ("output_image", "success", "message")
    FUNCTION = "load_image"
    CATEGORY = "✨✨✨design-ai/api"

    def build_headers(self, token: str = "") -> dict:
        """构建请求头"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 如果提供了token，添加Authorization头
        if token and token.strip():
            headers['Authorization'] = f'Bearer {token}'
            
        return headers

    def load_image(self, url, fallback_image, timeout, max_retries, use_proxy, token=""):
        message = ""
        success = False
        output_image = fallback_image

        # 构建请求头
        headers = self.build_headers(token)
        
        # 配置请求参数
        request_kwargs = {
            "headers": headers,
            "timeout": timeout
        }
        
        # 配置代理
        if use_proxy:
            request_kwargs["proxies"] = {"http": None, "https": None}

        # 尝试从URL加载图片
        retry_count = 0
        while retry_count <= max_retries:
            try:
                print(f"尝试加载图片 (第 {retry_count + 1} 次): {url}")
                
                response = requests.get(url, **request_kwargs)
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
                    message = f"图片加载成功! 尺寸: {image.size}"
                    print(message)
                    break
                else:
                    message = f"HTTP错误 {response.status_code}: {response.reason}"
                    print(message)
            except requests.Timeout:
                message = f"请求超时 (第 {retry_count + 1}/{max_retries + 1} 次尝试)"
                print(message)
            except requests.RequestException as e:
                message = f"请求错误: {str(e)}"
                print(message)
            except Exception as e:
                message = f"意外错误: {str(e)}"
                print(message)
            
            retry_count += 1
            if retry_count <= max_retries:
                print(f"等待1秒后重试...")
                time.sleep(1)  # 重试前等待1秒

        if not success:
            final_message = f"加载图片失败，共尝试 {max_retries + 1} 次。使用备用图片。最后错误: {message}"
            print(final_message)
            message = final_message

        # 确保fallback_image也是正确的格式
        if not success and not isinstance(output_image, torch.Tensor):
            output_image = torch.from_numpy(output_image)
        if len(output_image.shape) == 3:  # 如果没有batch维度
            output_image = output_image.unsqueeze(0)

        return (output_image, success, message)