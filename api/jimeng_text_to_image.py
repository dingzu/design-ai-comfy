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

class JiMengTextToImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["staging", "prod", "idc", "overseas", "domestic"], {
                    "default": "staging",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "鱼眼镜头，一只猫咪的头部，画面呈现出猫咪的五官因为拍摄方式扭曲的效果。",
                    "multiline": True,
                    "tooltip": "图像描述提示词"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "b64_json",
                    "tooltip": "响应格式"
                }),
                "size": (["1024x1024", "1024x1536", "1536x1024", "adaptive"], {
                    "default": "1024x1024",
                    "tooltip": "图像尺寸"
                }),
                "seed": ("INT", {
                    "default": 12,
                    "min": 0,
                    "max": 2147483647,
                    "step": 1,
                    "tooltip": "随机种子"
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 2.5,
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
                    "default": "/llm-serve/v1/images/generations",
                    "tooltip": "自定义API端点路径"
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
            "idc": "http://llm-gateway.internal",
            "overseas": "http://llm-gateway-sgp.internal",
            "domestic": "http://llm-gateway.internal"
        }

    def generate_image(self, environment, api_key, prompt, response_format, size, 
                      seed, guidance_scale, watermark, timeout, use_proxy, custom_base_url="", custom_endpoint="/llm-serve/v1/images/generations"):
        """
        即梦文生图
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("图像描述不能为空")

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
            else:
                base_url = self.environments[environment]
            
            # 使用自定义端点路径
            endpoint = custom_endpoint.strip() if custom_endpoint.strip() else "/llm-serve/v1/images/generations"
            endpoint = endpoint.lstrip('/')  # 移除开头的斜杠
            url = f"{base_url}/{endpoint}"
            
            # 构建请求体
            payload = {
                "model": "doubao-seedream-3-0-t2i-250415",
                "prompt": prompt.strip(),
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
                "User-Agent": "ComfyUI-JiMeng-T2I/1.0"
            }
            
            print(f"[即梦文生图] 发送请求到: {url}")
            print(f"[即梦文生图] 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            # 配置代理
            request_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": timeout
            }
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            # 发送请求
            response = requests.post(url, **request_kwargs)
            
            print(f"[即梦文生图] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_text = response.text if response.text else "空响应"
                print(f"[即梦文生图] 响应内容: {response_text}")
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
            
            print(f"[即梦文生图] 成功生成 {len(image_data)} 张图像")
            
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
                    
                    print(f"[即梦文生图] 图像 {idx + 1}: {image.size}, 模式: {image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    image_url = item['url']
                    print(f"[即梦文生图] 收到图像URL: {image_url}")
                    
                    if response_format == "url":
                        # 如果用户选择了URL格式，下载图像
                        try:
                            # 配置代理
                            download_kwargs = {"timeout": 30}
                            if use_proxy:
                                download_kwargs["proxies"] = {"http": None, "https": None}
                            
                            img_response = requests.get(image_url, **download_kwargs)
                            img_response.raise_for_status()
                            image = Image.open(io.BytesIO(img_response.content))
                            
                            # 转换为RGB
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            # 转换为tensor
                            image_np = np.array(image).astype(np.float32) / 255.0
                            image_tensor = torch.from_numpy(image_np)[None,]
                            images_tensor.append(image_tensor)
                            
                            print(f"[即梦文生图] 下载图像 {idx + 1}: {image.size}, 模式: {image.mode}")
                            
                        except Exception as e:
                            print(f"[即梦文生图] 下载图像失败: {str(e)}")
                            continue
                    else:
                        print(f"[即梦文生图] 警告: 跳过URL形式的图像，当前仅支持base64格式")
            
            if not images_tensor:
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage = response_data.get('usage', {})
            usage_info = f"即梦文生图结果:\n"
            usage_info += f"- 模型: doubao-seedream-3-0-t2i-250415\n"
            usage_info += f"- 种子: {seed}\n"
            usage_info += f"- 引导强度: {guidance_scale}\n"
            usage_info += f"- 尺寸: {size}\n"
            usage_info += f"- 水印: {'是' if watermark else '否'}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            
            if usage:
                usage_info += f"- 输入Token: {usage.get('input_tokens', 0)}\n"
                usage_info += f"- 输出Token: {usage.get('output_tokens', 0)}\n"
                usage_info += f"- 总计Token: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[即梦文生图] 图像生成完成")
            print(f"[即梦文生图] {usage_info}")
            
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
    "JiMengTextToImage": JiMengTextToImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JiMengTextToImage": "即梦文生图"
} 