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

class WanQingGPTImageGenerationNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["staging", "prod", "idc"], {
                    "default": "prod",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "生成一个带蝴蝶结的鲸鱼",
                    "multiline": True,
                    "tooltip": "图像描述提示词"
                }),
                "image_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量"
                }),
                "image_size": (["1024x1024", "1792x1024", "1024x1792", "auto"], {
                    "default": "1024x1024",
                    "tooltip": "图像尺寸"
                }),
                "quality": (["medium", "high", "low", "auto"], {
                    "default": "medium",
                    "tooltip": "图像质量"
                }),
                "output_format": (["png", "jpeg"], {
                    "default": "png",
                    "tooltip": "输出格式"
                }),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "请求超时时间（秒）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod-sgp.corp.kuaishou.com", 
            "prod-old": "https://llm-gateway-prod.corp.kuaishou.com",
            "idc": "http://llm-gateway.internal"
        }

    def generate_image(self, environment, api_key, prompt, image_count, 
                      image_size, quality, output_format, timeout):
        """
        万擎 GPT 图像生成
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("图像描述不能为空")

            # 构建URL
            base_url = self.environments[environment]
            url = f"{base_url}/llm-serve/v1/images/generations"
            
            # 构建请求体
            payload = {
                "prompt": prompt.strip(),
                "model": "gpt-image-1",
                "n": image_count,
                "size": image_size,
                "quality": quality,
                "output_format": output_format
            }
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-WanQing-GPT/1.0"
            }
            
            print(f"[万擎 GPT] 发送请求到: {url}")
            print(f"[万擎 GPT] 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            print(f"[万擎 GPT] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                raise ValueError(f"无效的JSON响应: {response.text}")
            
            # 检查响应状态
            if not response.ok:
                error_msg = response_data.get('error', {}).get('message', '未知错误')
                error_type = response_data.get('error', {}).get('type', 'unknown_error')
                error_code = response_data.get('error', {}).get('code', 'unknown')
                
                # 提供详细的错误信息和解决建议
                if 'unknown_parameter' in error_type.lower():
                    error_msg += "\n\n💡 建议: 检查API参数是否正确，某些参数可能不被当前版本支持"
                elif 'invalid_value' in error_type.lower():
                    error_msg += "\n\n💡 建议: 检查参数值是否在允许范围内"
                elif 'invalid_request_error' in error_type.lower():
                    error_msg += "\n\n💡 建议: 检查请求格式和必需参数"
                elif response.status_code == 401:
                    error_msg += "\n\n💡 建议: 检查API Key是否有效，联系 @于淼 获取正确的万擎网关key"
                elif response.status_code == 429:
                    error_msg += "\n\n💡 建议: 请求频率过高，请稍后重试"
                
                raise ValueError(f"API错误 [{error_code}]: {error_msg}")
            
            # 处理生成的图像
            images_tensor = []
            image_data = response_data.get('data', [])
            
            if not image_data:
                raise ValueError("响应中没有图像数据")
            
            print(f"[万擎 GPT] 成功生成 {len(image_data)} 张图像")
            
            for idx, item in enumerate(image_data):
                if 'b64_json' in item:
                    # 处理 base64 编码的图像
                    b64_data = item['b64_json']
                    image_bytes = base64.b64decode(b64_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB（如果不是的话）
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    print(f"[万擎 GPT] 图像 {idx + 1}: {image.size}, 模式: {image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    print(f"[万擎 GPT] 收到图像URL: {item['url']}")
                    # 这里可以选择下载URL图像，或者只是记录URL
                    # 为了简化，我们暂时跳过URL形式的图像
                    print(f"[万擎 GPT] 警告: 跳过URL形式的图像，当前版本仅支持base64格式")
            
            if not images_tensor:
                raise ValueError("没有可用的图像数据（仅支持base64格式）")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage = response_data.get('usage', {})
            usage_info = f"Token使用情况:\n"
            usage_info += f"- 输入Token: {usage.get('input_tokens', 0)}\n"
            usage_info += f"- 输出Token: {usage.get('output_tokens', 0)}\n"
            usage_info += f"- 总计Token: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[万擎 GPT] 图像生成完成")
            print(f"[万擎 GPT] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒）。图像生成可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像生成失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "WanQingGPTImageGeneration": WanQingGPTImageGenerationNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanQingGPTImageGeneration": "万擎 GPT 图像生成"
} 