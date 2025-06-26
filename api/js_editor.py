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
                    "default": "https://design-out.staging.kuaishou.com/www/server",
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
                    "default": "https://design-out.staging.kuaishou.com/api-token/fission-template/create-common-render-task",
                    "tooltip": "API地址"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "BOOLEAN", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image_big", "image_medium", "image_small", "success", "message", "task_id", "image_url_big", "image_url_medium", "image_url_small", "extracted_json", "response_data")
    FUNCTION = "run_js_editor"
    CATEGORY = "✨✨✨design-ai/api"

    def run_js_editor(self, js_code, api_token, creator, go_to_url, sync, timeout, api_url):
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
            
            # 发送请求
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
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
                            image_url_medium = item.get("image_url_medium", "")
                            image_url_small = item.get("image_url_small", "")
                            
                            # 下载三个尺寸的图片
                            image_big, success_big, msg_big = self._download_image(image_url_big, timeout) if image_url_big else (None, False, "没有big尺寸URL")
                            image_medium, success_medium, msg_medium = self._download_image(image_url_medium, timeout) if image_url_medium else (None, False, "没有medium尺寸URL")
                            image_small, success_small, msg_small = self._download_image(image_url_small, timeout) if image_url_small else (None, False, "没有small尺寸URL")
                            
                            # 如果下载失败，使用空白图片
                            if not success_big:
                                image_big = self._create_blank_image()
                            if not success_medium:
                                image_medium = self._create_blank_image()
                            if not success_small:
                                image_small = self._create_blank_image()
                            
                            # 判断整体成功状态
                            overall_success = success_big or success_medium or success_small
                            
                            if overall_success:
                                message_parts = [f"JS编辑器运行成功 - Big: {'✓' if success_big else '✗'}, Medium: {'✓' if success_medium else '✗'}, Small: {'✓' if success_small else '✗'}"]
                                if extracted_json:
                                    message_parts.append("JSON数据提取成功")
                                else:
                                    message_parts.append("JSON数据提取失败")
                                message = " | ".join(message_parts)
                            else:
                                message = f"所有图片下载失败 - Big: {msg_big}, Medium: {msg_medium}, Small: {msg_small}"
                            
                            return (image_big, image_medium, image_small, overall_success, message, task_id, 
                                   image_url_big, image_url_medium, image_url_small, extracted_json, response_text)
                        else:
                            blank_image = self._create_blank_image()
                            return (blank_image, blank_image, blank_image, False, "API返回数据中没有图片资源", task_id, "", "", "", extracted_json, response_text)
                    else:
                        error_msg = response_json.get("errorMsg", "未知错误")
                        blank_image = self._create_blank_image()
                        return (blank_image, blank_image, blank_image, False, f"API返回错误: {error_msg}", "", "", "", "", "", response_text)
                        
                except json.JSONDecodeError:
                    blank_image = self._create_blank_image()
                    return (blank_image, blank_image, blank_image, False, f"API响应格式错误: {response_text}", "", "", "", "", "", response_text)
            else:
                blank_image = self._create_blank_image()
                return (blank_image, blank_image, blank_image, False, f"HTTP错误 {response.status_code}: {response_text}", "", "", "", "", "", response_text)
                
        except requests.Timeout:
            blank_image = self._create_blank_image()
            return (blank_image, blank_image, blank_image, False, f"请求超时({timeout}秒)", "", "", "", "", "", "")
        except requests.RequestException as e:
            blank_image = self._create_blank_image()
            return (blank_image, blank_image, blank_image, False, f"网络请求错误: {str(e)}", "", "", "", "", "", "")
        except Exception as e:
            blank_image = self._create_blank_image()
            return (blank_image, blank_image, blank_image, False, f"处理过程中出现错误: {str(e)}", "", "", "", "", "", "")

    def _download_image(self, image_url, timeout):
        """下载图片并转换为tensor"""
        try:
            response = requests.get(image_url, timeout=timeout)
            if response.status_code == 200:
                # 从响应内容加载图片
                image = Image.open(BytesIO(response.content))
                
                # 转换为RGB模式
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
                image_tensor = torch.from_numpy(np_image)
                
                return (image_tensor, True, "图片下载成功")
            else:
                return (None, False, f"HTTP错误 {response.status_code}")
        except Exception as e:
            return (None, False, f"下载错误: {str(e)}")

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        # 创建白色背景图片
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array) 