import torch
import numpy as np
import requests
import time
import json
import base64
import io
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple
import folder_paths

class QwenImageEditNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["prod", "staging", "idc", "overseas", "domestic"], {
                    "default": "prod",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "image": ("IMAGE", {
                    "tooltip": "要编辑的输入图像"
                }),
                "prompt": ("STRING", {
                    "default": "修改这张图片",
                    "multiline": True,
                    "tooltip": "图像编辑指令"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词（描述不希望出现的内容）"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "timeout": ("FLOAT", {
                    "default": 60.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 15.0,
                    "tooltip": "请求超时时间（秒）"
                }),
                "use_proxy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否使用代理服务器"
                }),
                "custom_base_url": ("STRING", {
                    "default": "",
                    "tooltip": "自定义API基础URL（优先级高于环境选择）"
                }),
                "custom_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/qwen-image/multimodal-generation/generation",
                    "tooltip": "自定义API端点路径"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "edit_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal",
            "overseas": "http://llm-gateway-sgp.internal",
            "domestic": "http://llm-gateway.internal"
        }

    def edit_image(self, environment, api_key, image, prompt, negative_prompt, 
                   watermark, timeout, use_proxy, custom_base_url="", custom_endpoint="/ai-serve/v1/qwen-image/multimodal-generation/generation"):
        """
        Qwen-Image 图像编辑（异步API）
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("编辑指令不能为空")
            
            if image is None:
                raise ValueError("输入图像不能为空")

            # 转换图像为base64
            image_base64 = self._image_to_base64(image)

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
            else:
                base_url = self.environments[environment]
            
            # 使用自定义端点路径
            endpoint = custom_endpoint.strip() if custom_endpoint.strip() else "/ai-serve/v1/qwen-image/multimodal-generation/generation"
            endpoint = endpoint.lstrip('/')  # 移除开头的斜杠
            api_url = f"{base_url}/{endpoint}"
            
            # 构建请求体 - 新的消息格式
            payload = {
                "model": "qwen-image-edit",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": f"data:image/png;base64,{image_base64}"
                                },
                                {
                                    "text": prompt.strip()
                                }
                            ]
                        }
                    ]
                },
                "parameters": {
                    "negative_prompt": negative_prompt.strip() if negative_prompt else "",
                    "watermark": watermark
                }
            }
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-QwenImage-Edit/1.0"
            }
            
            print(f"[Qwen-Image Edit] 发送请求到: {api_url}")
            print(f"[Qwen-Image Edit] 编辑指令: {prompt}")
            print(f"[Qwen-Image Edit] 负面提示词: {negative_prompt if negative_prompt else '无'}")
            print(f"[Qwen-Image Edit] 是否添加水印: {'是' if watermark else '否'}")
            
            # 配置代理
            request_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": timeout
            }
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            # 发送同步请求
            response = requests.post(api_url, **request_kwargs)
            
            print(f"[Qwen-Image Edit] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                raise ValueError(f"无效的JSON响应: {response.text}")
            
            # 检查响应状态
            if not response.ok:
                error_msg = result.get('error', {}).get('message', response.text)
                raise ValueError(f"请求失败 [{response.status_code}]: {error_msg}")
            
            # 处理结果
            return self._process_result(result, use_proxy)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒）。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像编辑失败: {str(e)}")

    def _image_to_base64(self, image_tensor):
        """将图像tensor转换为base64"""
        try:
            # 获取第一张图像（如果是批量）
            if len(image_tensor.shape) == 4:
                image = image_tensor[0]
            else:
                image = image_tensor
            
            # 转换为numpy并转换到0-255范围
            image_np = (image.cpu().numpy() * 255).astype(np.uint8)
            
            # 创建PIL图像
            pil_image = Image.fromarray(image_np)
            
            # 转换为base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            print(f"[Qwen-Image Edit] 图像转换完成: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
            
        except Exception as e:
            raise ValueError(f"图像转换失败: {str(e)}")

    def _process_result(self, result, use_proxy):
        """处理编辑结果"""
        try:
            # 提取结果数据 - 新的choices格式
            choices = result.get("output", {}).get("choices", [])
            if not choices:
                raise ValueError("响应中没有choices数据")
            
            images_tensor = []
            image_urls = []
            
            print(f"[Qwen-Image Edit] 处理 {len(choices)} 个结果")
            
            for idx, choice in enumerate(choices):
                message = choice.get("message", {})
                content = message.get("content", [])
                
                for content_item in content:
                    if "image" in content_item:
                        image_url = content_item["image"]
                        if not image_url:
                            print(f"[Qwen-Image Edit] 结果 {idx + 1} 没有图像URL")
                            continue
                        
                        image_urls.append(image_url)
                        
                        # 下载图像
                        try:
                            print(f"[Qwen-Image Edit] 下载图像 {idx + 1}: {image_url[:100]}...")
                            # 配置代理
                            download_kwargs = {"timeout": 60}
                            if use_proxy:
                                download_kwargs["proxies"] = {"http": None, "https": None}
                            
                            img_response = requests.get(image_url, **download_kwargs)
                            if img_response.status_code == 200:
                                image = Image.open(io.BytesIO(img_response.content))
                                
                                # 转换为RGB（如果不是的话）
                                if image.mode != 'RGB':
                                    image = image.convert('RGB')
                                
                                # 转换为tensor
                                image_np = np.array(image).astype(np.float32) / 255.0
                                image_tensor = torch.from_numpy(image_np)[None,]
                                images_tensor.append(image_tensor)
                                
                                print(f"[Qwen-Image Edit] 图像 {idx + 1}: {image.size}, 模式: {image.mode}")
                            else:
                                print(f"[Qwen-Image Edit] 图像下载失败 {img_response.status_code}")
                                
                        except Exception as e:
                            print(f"[Qwen-Image Edit] 下载图像 {idx + 1} 异常: {str(e)}")
            
            if not images_tensor:
                raise ValueError("没有成功下载的图像")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage = result.get('usage', {})
            usage_info = f"使用统计:\n"
            usage_info += f"- 宽度: {usage.get('width', 'N/A')}\n"
            usage_info += f"- 高度: {usage.get('height', 'N/A')}\n"
            usage_info += f"- 图像数量: {usage.get('image_count', len(images_tensor))}\n"
            usage_info += f"- 成功下载: {len(images_tensor)}\n"
            usage_info += f"- 请求ID: {result.get('request_id', 'N/A')}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            print(f"[Qwen-Image Edit] 图像编辑完成")
            print(f"[Qwen-Image Edit] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except Exception as e:
            raise ValueError(f"结果处理失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenImageEdit": QwenImageEditNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEdit": "Qwen-Image 图像编辑"
}
