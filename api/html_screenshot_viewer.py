import torch
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import json

class ApiResponseViewerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "response_data": ("STRING", {
                    "forceInput": True,
                    "tooltip": "来自API响应节点的数据（HTML截图或JS编辑器）"
                }),
                "timeout": ("FLOAT", {
                    "default": 30.0,
                    "min": 5.0,
                    "max": 120.0,
                    "step": 1.0,
                    "tooltip": "图片下载超时时间(秒)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "IMAGE", "IMAGE", "IMAGE", "BOOLEAN", "BOOLEAN", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("formatted_json", "task_id", "image_url_big", "image_url_medium", "image_url_small", "downloaded_image_big", "downloaded_image_medium", "downloaded_image_small", "download_success_big", "download_success_medium", "download_success_small", "download_message", "extracted_json")
    FUNCTION = "view_response"
    CATEGORY = "✨✨✨design-ai/api"

    def view_response(self, response_data, timeout):
        try:
            if not response_data or response_data.strip() == "":
                return self._return_empty_result("响应数据为空")

            # 解析JSON响应
            try:
                response_json = json.loads(response_data)
            except json.JSONDecodeError as e:
                return self._return_empty_result(f"JSON解析错误: {str(e)}")

            # 格式化JSON显示
            formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)

            # 提取关键信息
            task_id = ""
            image_url_big = ""
            image_url_medium = ""
            image_url_small = ""
            extracted_json = ""

            if response_json.get("code") == 1:
                data = response_json.get("data", {})
                task_id = data.get("taskId", "")
                
                resource = data.get("resource", {})
                design_ai_resource_items = resource.get("design_ai_resource_items", [])
                design_ai_text_resource_items = resource.get("design_ai_text_resource_items", [])
                
                # 提取图片URL
                if design_ai_resource_items and len(design_ai_resource_items) > 0:
                    item = design_ai_resource_items[0]
                    image_url_big = item.get("image_url_big", "")
                    image_url_medium = item.get("image_url_medium", "")
                    image_url_small = item.get("image_url_small", "")

                # 提取JSON数据（适用于HTML截图的screenshotWithJson或JS编辑器的结果）
                if design_ai_text_resource_items and len(design_ai_text_resource_items) > 0:
                    for text_item in design_ai_text_resource_items:
                        text_content = text_item.get("text", "")
                        if text_content:
                            extracted_json = text_content
                            break  # 取第一个有内容的text

            # 下载三个尺寸的图片
            downloaded_image_big = None
            downloaded_image_medium = None
            downloaded_image_small = None
            download_success_big = False
            download_success_medium = False
            download_success_small = False
            download_messages = []

            if image_url_big:
                downloaded_image_big, download_success_big, msg_big = self._download_image(image_url_big, timeout)
                download_messages.append(f"Big: {msg_big}")
            else:
                download_messages.append("Big: 没有URL")

            if image_url_medium:
                downloaded_image_medium, download_success_medium, msg_medium = self._download_image(image_url_medium, timeout)
                download_messages.append(f"Medium: {msg_medium}")
            else:
                download_messages.append("Medium: 没有URL")

            if image_url_small:
                downloaded_image_small, download_success_small, msg_small = self._download_image(image_url_small, timeout)
                download_messages.append(f"Small: {msg_small}")
            else:
                download_messages.append("Small: 没有URL")

            # 如果下载失败，使用空白图片
            if not download_success_big:
                downloaded_image_big = self._create_blank_image()
            if not download_success_medium:
                downloaded_image_medium = self._create_blank_image()
            if not download_success_small:
                downloaded_image_small = self._create_blank_image()

            # 添加JSON提取状态到消息中
            if extracted_json:
                download_messages.append("JSON: 提取成功")
            else:
                download_messages.append("JSON: 无数据")

            download_message = " | ".join(download_messages)

            return (
                formatted_json,
                task_id,
                image_url_big,
                image_url_medium,
                image_url_small,
                downloaded_image_big,
                downloaded_image_medium,
                downloaded_image_small,
                download_success_big,
                download_success_medium,
                download_success_small,
                download_message,
                extracted_json
            )

        except Exception as e:
            return self._return_empty_result(f"处理过程中出现错误: {str(e)}")

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
                
                return (image_tensor, True, f"图片下载成功，尺寸: {image.size}")
            else:
                return (None, False, f"HTTP错误 {response.status_code}")
        except Exception as e:
            return (None, False, f"下载错误: {str(e)}")

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        # 创建白色背景图片
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def _return_empty_result(self, error_message):
        """返回空结果"""
        blank_image = self._create_blank_image()
        return (
            f'{{"error": "{error_message}"}}',  # formatted_json
            "",  # task_id
            "",  # image_url_big
            "",  # image_url_medium
            "",  # image_url_small
            blank_image,  # downloaded_image_big
            blank_image,  # downloaded_image_medium
            blank_image,  # downloaded_image_small
            False,  # download_success_big
            False,  # download_success_medium
            False,  # download_success_small
            error_message,  # download_message
            ""  # extracted_json
        ) 