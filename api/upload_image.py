import torch
import numpy as np
import requests
from PIL import Image
import io
import json

class UploadImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "upload_type": (["内部cdn(默认)", "blobstore", "外部海外cdn", "aws", "外部国内cdn"], {
                    "default": "内部cdn(默认)",
                    "tooltip": "选择上传类型：内部cdn(默认)=2, blobstore=1, 外部海外cdn=3, aws=4, 外部国内cdn=8"
                }),
                "image_format": (["JPEG", "PNG", "WebP"], {
                    "default": "JPEG",
                    "tooltip": "输出图片格式"
                }),
                "quality": ("INT", {
                    "default": 80,
                    "min": 10,
                    "max": 100,
                    "step": 5,
                    "tooltip": "JPEG质量 (仅对JPEG格式有效)"
                }),
                "resize_enabled": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用尺寸调整"
                }),
                "resize_type": (["width", "height"], {
                    "default": "width",
                    "tooltip": "调整类型"
                }),
                "resize_value": ("INT", {
                    "default": 800,
                    "min": 100,
                    "max": 4000,
                    "step": 50,
                    "tooltip": "调整尺寸值"
                }),
                "timeout": ("FLOAT", {
                    "default": 30.0,
                    "min": 5.0,
                    "max": 120.0,
                    "step": 1.0,
                    "tooltip": "请求超时时间(秒)"
                }),
                "api_url": ("STRING", {
                    "default": "http://poify.internal/api-token/common/upload-file",
                    "tooltip": "上传API的URL地址"
                }),
                "poify_token": ("STRING", {
                    "default": "zorD9Tk4YPATC7U3RgXtAsemT5p6a28W",
                    "tooltip": "用于认证的Poify Token (poify-token header)"
                }),
                "use_proxy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否使用代理服务器"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("url", "success", "message", "response_data")
    FUNCTION = "upload_image"
    CATEGORY = "✨✨✨design-ai/api"

    def upload_image(self, image, upload_type, image_format, quality, 
                    resize_enabled, resize_type, resize_value, timeout, api_url, poify_token, use_proxy):
        try:
            # 映射upload_type描述到数字值
            upload_type_map = {
                "blobstore": "1",
                "内部cdn(默认)": "2", 
                "外部海外cdn": "3",
                "aws": "4",
                "外部国内cdn": "8"
            }
            upload_type_value = upload_type_map.get(upload_type, "2")  # 默认使用内部cdn
            
            # 将ComfyUI的image tensor转换为PIL图像
            # ComfyUI的图像格式是 [batch, height, width, channels]，值在0-1之间
            if isinstance(image, torch.Tensor):
                # 取第一张图片（如果是batch）
                img_array = image[0].cpu().numpy()
                # 转换为0-255范围
                img_array = (img_array * 255).astype(np.uint8)
                pil_image = Image.fromarray(img_array)
            else:
                return ("", False, "Invalid image format", "")

            # 图像处理
            processed_image = self._process_image(
                pil_image, image_format, quality, 
                resize_enabled, resize_type, resize_value
            )

            # 准备上传
            return self._upload_to_api(processed_image, upload_type_value, timeout, api_url, poify_token, use_proxy)

        except Exception as e:
            error_msg = f"图片上传失败: {str(e)}"
            return ("", False, error_msg, "")

    def _process_image(self, image, format_type, quality, resize_enabled, resize_type, resize_value):
        """处理图片：格式转换和尺寸调整"""
        processed_image = image.copy()
        
        # 尺寸调整
        if resize_enabled:
            width, height = processed_image.size
            
            if resize_type == "width":
                if width != resize_value:
                    ratio = resize_value / width
                    new_width = resize_value
                    new_height = int(height * ratio)
                    processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:  # height
                if height != resize_value:
                    ratio = resize_value / height
                    new_height = resize_value
                    new_width = int(width * ratio)
                    processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 格式转换
        output_buffer = io.BytesIO()
        
        if format_type == "JPEG":
            # 确保是RGB模式
            if processed_image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', processed_image.size, (255, 255, 255))
                background.paste(processed_image, mask=processed_image.split()[-1])
                processed_image = background
            elif processed_image.mode != 'RGB':
                processed_image = processed_image.convert('RGB')
            
            processed_image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            filename = "image.jpg"
            content_type = "image/jpeg"
            
        elif format_type == "PNG":
            processed_image.save(output_buffer, format='PNG', optimize=True)
            filename = "image.png"
            content_type = "image/png"
            
        elif format_type == "WebP":
            processed_image.save(output_buffer, format='WebP', quality=quality)
            filename = "image.webp"
            content_type = "image/webp"

        output_buffer.seek(0)
        return output_buffer, filename, content_type

    def _upload_to_api(self, image_data, upload_type, timeout, api_url, poify_token, use_proxy):
        """上传图片到API"""
        buffer, filename, content_type = image_data
        
        # 准备multipart/form-data
        files = {
            'file': (filename, buffer, content_type)
        }
        
        data = {
            'uploadType': upload_type
        }
        
        # 构建请求头
        headers = {}
        if poify_token and poify_token.strip():
            headers['poify-token'] = poify_token
        
        # 配置代理
        request_kwargs = {
            "files": files,
            "data": data,
            "timeout": timeout
        }
        
        # 只有在有自定义headers时才添加
        if headers:
            request_kwargs["headers"] = headers
            
        if use_proxy:
            request_kwargs["proxies"] = {"http": None, "https": None}
        
        try:
            response = requests.post(api_url, **request_kwargs)
            
            # 解析响应
            response_text = response.text
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    
                    if response_json.get("code") == 1:
                        url = response_json.get("data", "")
                        message = "图片上传成功"
                        success = True
                    else:
                        url = ""
                        message = f"API返回错误: {response_json.get('errorMsg', '未知错误')}"
                        success = False
                        
                    return (url, success, message, response_text)
                    
                except json.JSONDecodeError:
                    return ("", False, f"API响应格式错误: {response_text}", response_text)
            else:
                return ("", False, f"HTTP错误 {response.status_code}: {response_text}", response_text)
                
        except requests.Timeout:
            return ("", False, f"请求超时({timeout}秒)", "")
        except requests.RequestException as e:
            return ("", False, f"网络请求错误: {str(e)}", "")
        except Exception as e:
            return ("", False, f"上传过程中出现错误: {str(e)}", "") 