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

class JiMengImageToImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["staging", "prod", "idc"], {
                    "default": "staging",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "改成爱心形状的泡泡",
                    "multiline": True,
                    "tooltip": "图像编辑描述提示词"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "b64_json",
                    "tooltip": "响应格式"
                }),
                "size": (["1024x1024", "1024x1536", "1536x1024", "adaptive"], {
                    "default": "adaptive",
                    "tooltip": "图像尺寸"
                }),
                "seed": ("INT", {
                    "default": 21,
                    "min": 0,
                    "max": 2147483647,
                    "step": 1,
                    "tooltip": "随机种子"
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 5.5,
                    "min": 0.1,
                    "max": 20.0,
                    "step": 0.1,
                    "tooltip": "引导强度"
                }),
                "watermark": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否添加水印"
                }),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "请求超时时间（秒）"
                })
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "输入图像（可选，如果不提供则使用图像URL）"
                }),
                "image_url": ("STRING", {
                    "default": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seededit_i2i.jpeg",
                    "tooltip": "图像URL（当未提供输入图像时使用）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal"
        }

    def tensor_to_base64(self, tensor):
        """将tensor转换为base64编码的图像"""
        # 处理batch维度
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        # 转换为numpy并确保在0-255范围内
        np_image = tensor.cpu().numpy()
        if np_image.max() <= 1.0:
            np_image = (np_image * 255).astype(np.uint8)
        else:
            np_image = np.clip(np_image, 0, 255).astype(np.uint8)
        
        # 转换为PIL图像
        pil_image = Image.fromarray(np_image)
        
        # 转换为base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        
        # 返回data URI格式，火山引擎API期望这种格式
        base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_string}"

    def generate_image(self, environment, api_key, prompt, response_format, size, 
                      seed, guidance_scale, watermark, timeout, image=None, image_url=None):
        """
        即梦图生图
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("图像编辑描述不能为空")

            # 处理输入图像
            image_input = None
            if image is not None:
                # 使用提供的图像tensor
                image_input = self.tensor_to_base64(image)
                print(f"[即梦图生图] 使用输入图像tensor，尺寸: {image.shape}")
                print(f"[即梦图生图] 图像格式: data URI (长度: {len(image_input)} 字符)")
            elif image_url and image_url.strip():
                # 使用图像URL
                image_input = image_url.strip()
                print(f"[即梦图生图] 使用图像URL: {image_input}")
                # 验证URL格式
                if not (image_input.startswith('http://') or image_input.startswith('https://') or image_input.startswith('data:')):
                    print(f"[即梦图生图] 警告: URL格式可能不正确，应以http://、https://或data:开头")
            else:
                raise ValueError("必须提供输入图像或图像URL")

            # 构建URL
            base_url = self.environments[environment]
            url = f"{base_url}/llm-serve/v1/images/generations"
            
            # 构建请求体
            payload = {
                "model": "doubao-seededit-3-0-i2i-250628",
                "prompt": prompt.strip(),
                "image": image_input,
                "response_format": response_format,
                "size": size,
                "seed": seed,
                "guidance_scale": guidance_scale,
                "watermark": watermark
            }
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-JiMeng-I2I/1.0"
            }
            
            print(f"[即梦图生图] 发送请求到: {url}")
            print(f"[即梦图生图] 请求参数:")
            print(f"  - model: doubao-seededit-3-0-i2i-250628")
            print(f"  - prompt: {prompt.strip()}")
            print(f"  - image: {'base64数据' if image is not None else image_input}")
            print(f"  - response_format: {response_format}")
            print(f"  - size: {size}")
            print(f"  - seed: {seed}")
            print(f"  - guidance_scale: {guidance_scale}")
            print(f"  - watermark: {watermark}")
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            print(f"[即梦图生图] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_text = response.text if response.text else "空响应"
                print(f"[即梦图生图] 响应内容: {response_text}")
                raise ValueError(f"无效的JSON响应 (状态码: {response.status_code}): {response_text}")
            
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
                elif 'invalid_image' in error_type.lower():
                    error_msg += "\n\n💡 建议: 检查输入图像格式是否正确，支持常见图像格式"
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
            
            print(f"[即梦图生图] 成功生成 {len(image_data)} 张图像")
            
            for idx, item in enumerate(image_data):
                if 'b64_json' in item:
                    # 处理 base64 编码的图像
                    b64_data = item['b64_json']
                    image_bytes = base64.b64decode(b64_data)
                    result_image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB（如果不是的话）
                    if result_image.mode != 'RGB':
                        result_image = result_image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(result_image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    print(f"[即梦图生图] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    image_url_result = item['url']
                    print(f"[即梦图生图] 收到图像URL: {image_url_result}")
                    
                    if response_format == "url":
                        # 如果用户选择了URL格式，下载图像
                        try:
                            img_response = requests.get(image_url_result, timeout=30)
                            img_response.raise_for_status()
                            result_image = Image.open(io.BytesIO(img_response.content))
                            
                            # 转换为RGB
                            if result_image.mode != 'RGB':
                                result_image = result_image.convert('RGB')
                            
                            # 转换为tensor
                            image_np = np.array(result_image).astype(np.float32) / 255.0
                            image_tensor = torch.from_numpy(image_np)[None,]
                            images_tensor.append(image_tensor)
                            
                            print(f"[即梦图生图] 下载图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                            
                        except Exception as e:
                            print(f"[即梦图生图] 下载图像失败: {str(e)}")
                            continue
                    else:
                        print(f"[即梦图生图] 警告: 跳过URL形式的图像，当前仅支持base64格式")
            
            if not images_tensor:
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage = response_data.get('usage', {})
            usage_info = f"即梦图生图结果:\n"
            usage_info += f"- 模型: doubao-seededit-3-0-i2i-250628\n"
            usage_info += f"- 种子: {seed}\n"
            usage_info += f"- 引导强度: {guidance_scale}\n"
            usage_info += f"- 尺寸: {size}\n"
            usage_info += f"- 水印: {'是' if watermark else '否'}\n"
            usage_info += f"- 输入图像: {'Tensor' if image is not None else 'URL'}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            
            if usage:
                usage_info += f"- 输入Token: {usage.get('input_tokens', 0)}\n"
                usage_info += f"- 输出Token: {usage.get('output_tokens', 0)}\n"
                usage_info += f"- 总计Token: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[即梦图生图] 图像生成完成")
            print(f"[即梦图生图] {usage_info}")
            
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
    "JiMengImageToImage": JiMengImageToImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JiMengImageToImage": "即梦图生图"
} 