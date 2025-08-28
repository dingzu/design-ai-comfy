import torch
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import json
import time

class JsEditorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "js_code": ("STRING", {
                    "multiline": True,
                    "default": "globalEditor.changeSize(1080, 1920); // 设置画布大小\nconst image = await editor.createLayer('image', {\n    fills: [{\n         url: 'https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/2e098d8604c1822136f5dfc0b.png'\n    }]\n}); // 添加图片图层\nconst text = await editor.createLayer('text', {\n    text: 'Hello World!',\n    fontSize: 80,\n    strokes:[{fill:'red', strokeWidth: 2, stroke: 'blue'}]\n});// 添加文字图层",
                    "tooltip": "要在编辑器中运行的JavaScript代码"
                }),
                "api_token": ("STRING", {
                    "default": "random-code",
                    "tooltip": "API访问令牌"
                }),
                "creator": ("STRING", {
                    "default": "1",
                    "tooltip": "创建者ID"
                }),
                "go_to_url": ("STRING", {
                    "default": "http://poify.internal/www/server",
                    "tooltip": "编辑器页面URL"
                }),
                "sync": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否同步等待结果"
                }),
                "timeout": ("FLOAT", {
                    "default": 30.0,
                    "min": 5.0,
                    "max": 120.0,
                    "step": 1.0,
                    "tooltip": "请求超时时间(秒)"
                }),
                "api_url": ("STRING", {
                    "default": "http://poify.internal/api-token/fission-template/create-common-render-task",
                    "tooltip": "API地址"
                }),
                "use_proxy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否使用代理服务器"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image_big", "mask_big", "success", "message", "task_id", "image_url_big", "extracted_json", "response_data")
    FUNCTION = "run_js_editor"
    CATEGORY = "✨✨✨design-ai/api"

    def run_js_editor(self, js_code, api_token, creator, go_to_url, sync, timeout, api_url, use_proxy):
        try:
            # 构建请求数据
            payload = {
                "apiToken": api_token,
                "creator": creator,
                "type": "editorRun",  # 使用editorRun类型
                "goToUrl": go_to_url,
                "params": js_code,  # 直接传入JS代码作为params
                "sync": sync
            }
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "poify-token": api_token
            }
            
            # 配置代理
            request_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": timeout
            }
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            # 发送请求
            response = requests.post(api_url, **request_kwargs)
            
            response_text = response.text
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    
                    if response_json.get("code") == 1:
                        data = response_json.get("data", {})
                        task_id = data.get("taskId", "")
                        
                        resource = data.get("resource", {})
                        design_ai_resource_items = resource.get("design_ai_resource_items", [])
                        design_ai_text_resource_items = resource.get("design_ai_text_resource_items", [])
                        
                        # 提取JSON数据（编辑器结果）
                        extracted_json = ""
                        if design_ai_text_resource_items:
                            for text_item in design_ai_text_resource_items:
                                text_content = text_item.get("text", "")
                                if text_content:
                                    extracted_json = text_content
                                    break  # 取第一个有内容的text
                        
                        if design_ai_resource_items and len(design_ai_resource_items) > 0:
                            item = design_ai_resource_items[0]
                            image_url_big = item.get("image_url_big", "")
                            
                            # 只下载大尺寸图片
                            if image_url_big:
                                image_big, mask_big, success_big, msg_big = self._download_image(image_url_big, timeout, use_proxy)
                            else:
                                image_big, mask_big, success_big, msg_big = (None, None, False, "没有big尺寸URL")
                            
                            # 如果下载失败，使用空白图片和mask
                            if not success_big:
                                image_big = self._create_blank_image()
                                mask_big = self._create_blank_mask()
                            
                            if success_big:
                                message_parts = [f"JS编辑器运行成功 - Big: ✓"]
                                if extracted_json:
                                    message_parts.append("JSON数据提取成功")
                                else:
                                    message_parts.append("JSON数据提取失败")
                                message = " | ".join(message_parts)
                            else:
                                message = f"图片下载失败 - Big: {msg_big}"
                            
                            return (image_big, mask_big, success_big, message, task_id, image_url_big, extracted_json, response_text)
                        else:
                            blank_image = self._create_blank_image()
                            blank_mask = self._create_blank_mask()
                            return (blank_image, blank_mask, False, "API返回数据中没有图片资源", task_id, "", extracted_json, response_text)
                    else:
                        error_msg = response_json.get("errorMsg", "未知错误")
                        blank_image = self._create_blank_image()
                        blank_mask = self._create_blank_mask()
                        return (blank_image, blank_mask, False, f"API返回错误: {error_msg}", "", "", "", response_text)
                        
                except json.JSONDecodeError:
                    blank_image = self._create_blank_image()
                    blank_mask = self._create_blank_mask()
                    return (blank_image, blank_mask, False, f"API响应格式错误: {response_text}", "", "", "", response_text)
            else:
                blank_image = self._create_blank_image()
                blank_mask = self._create_blank_mask()
                return (blank_image, blank_mask, False, f"HTTP错误 {response.status_code}: {response_text}", "", "", "", response_text)
                
        except requests.Timeout:
            blank_image = self._create_blank_image()
            blank_mask = self._create_blank_mask()
            return (blank_image, blank_mask, False, f"请求超时({timeout}秒)", "", "", "", "")
        except requests.RequestException as e:
            blank_image = self._create_blank_image()
            blank_mask = self._create_blank_mask()
            return (blank_image, blank_mask, False, f"网络请求错误: {str(e)}", "", "", "", "")
        except Exception as e:
            blank_image = self._create_blank_image()
            blank_mask = self._create_blank_mask()
            return (blank_image, blank_mask, False, f"处理过程中出现错误: {str(e)}", "", "", "", "")

    def _download_image(self, image_url, timeout, use_proxy=False):
        """下载图片并转换为tensor，分别返回RGB和Mask"""
        try:
            # 配置代理
            request_kwargs = {"timeout": timeout}
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            response = requests.get(image_url, **request_kwargs)
            if response.status_code == 200:
                # 从响应内容加载图片
                image = Image.open(BytesIO(response.content))
                
                # 处理alpha通道和RGB通道
                has_alpha = image.mode in ('RGBA', 'LA') or 'transparency' in image.info
                
                # 提取alpha通道作为mask
                mask_tensor = None
                if has_alpha:
                    if image.mode == 'RGBA':
                        alpha_channel = image.split()[-1]  # 获取alpha通道
                    elif image.mode == 'LA':
                        alpha_channel = image.split()[-1]  # 获取alpha通道
                    else:
                        # 处理有transparency信息但不是RGBA/LA模式的图片
                        image = image.convert('RGBA')
                        alpha_channel = image.split()[-1]
                    
                    # 将alpha通道转换为mask tensor
                    mask_array = np.array(alpha_channel).astype(np.float32) / 255.0
                    # ComfyUI中mask语义相反：透明区域(alpha=0)应该是白色(mask=1)，不透明区域(alpha=1)应该是黑色(mask=0)
                    mask_array = 1.0 - mask_array
                    # 添加batch维度 [height, width] -> [1, height, width]
                    mask_array = mask_array[None, ...]
                    mask_tensor = torch.from_numpy(mask_array)
                
                # 处理RGB通道
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景并合成
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if has_alpha:
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image)
                    rgb_image = background
                elif image.mode != 'RGB':
                    rgb_image = image.convert('RGB')
                else:
                    rgb_image = image
                
                # 转换RGB为numpy数组并归一化
                np_image = np.array(rgb_image).astype(np.float32) / 255.0
                
                # 确保图像是RGB格式，并添加batch维度
                if len(np_image.shape) == 2:  # 如果是灰度图像
                    np_image = np.stack([np_image] * 3, axis=-1)
                
                # 添加batch维度 [height, width, channels] -> [1, height, width, channels]
                np_image = np_image[None, ...]
                
                # 将numpy数组转换为PyTorch tensor，保持[B,H,W,C]格式
                image_tensor = torch.from_numpy(np_image)
                
                # 如果没有alpha通道，创建全黑的mask（ComfyUI语义：黑色=不处理，白色=处理）
                # 对于没有透明度的图片，默认认为是完全不透明，所以mask为黑色（不处理背景）
                if mask_tensor is None:
                    mask_array = np.zeros((1, image_tensor.shape[1], image_tensor.shape[2]), dtype=np.float32)
                    mask_tensor = torch.from_numpy(mask_array)
                
                return (image_tensor, mask_tensor, True, "图片下载成功")
            else:
                return (None, None, False, f"HTTP错误 {response.status_code}")
        except Exception as e:
            return (None, None, False, f"下载错误: {str(e)}")

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        # 创建白色背景图片
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)
    
    def _create_blank_mask(self, width=512, height=512):
        """创建空白mask tensor"""
        # 创建全黑的mask（ComfyUI语义：黑色=不处理，对应完全不透明的图片）
        blank_mask_array = np.zeros((1, height, width), dtype=np.float32)
        return torch.from_numpy(blank_mask_array)