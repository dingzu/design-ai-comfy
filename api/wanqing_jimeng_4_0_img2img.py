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

class WanQingJiMeng40ImageToImageNode:
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
                    "default": "生成狗狗趴在草地上的近景画面",
                    "multiline": True,
                    "tooltip": "图像编辑描述提示词，建议结构：风格关键词 + 主要美学关键词 + 视觉内容 + 视觉上下文 + 补充美学关键词"
                }),
                "size": (["4K", "2K", "1K", "1024x1024", "1024x1536", "1536x1024", "adaptive"], {
                    "default": "2K",
                    "tooltip": "图像尺寸（4K支持超高清输出，adaptive自适应输入图像尺寸）"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "url",
                    "tooltip": "响应格式"
                }),
                "sequential_image_generation": (["enabled", "disabled"], {
                    "default": "disabled",
                    "tooltip": "顺序图像生成"
                }),
                "stream": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用流式响应"
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
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "输入图像（可选，如果不提供则使用图像URL）"
                }),
                "image_url": ("STRING", {
                    "default": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_imageToimage.png",
                    "tooltip": "图像URL（当未提供输入图像时使用）"
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量（1-4张）"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "step": 1,
                    "tooltip": "随机种子，-1为随机生成"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词，描述不希望出现的内容"
                }),
                "quality": (["hd", "standard"], {
                    "default": "hd",
                    "tooltip": "图像质量：hd（高清）或 standard（标准）"
                }),
                "style": (["natural", "vivid"], {
                    "default": "vivid",
                    "tooltip": "图像风格：natural（自然）或 vivid（生动）"
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.5,
                    "tooltip": "引导强度，控制生成图像与提示词的匹配程度"
                }),
                "steps": ("INT", {
                    "default": 50,
                    "min": 10,
                    "max": 100,
                    "step": 1,
                    "tooltip": "推理步数，更多步数通常得到更高质量图像"
                }),
                "strength": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "图像变化强度，0.0保持原图，1.0完全重新生成"
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

    def generate_image(self, environment, api_key, prompt, size, response_format, 
                      sequential_image_generation, stream, watermark, timeout, use_proxy, 
                      custom_base_url="", custom_endpoint="/llm-serve/v1/images/generations",
                      image=None, image_url=None, n=1, seed=-1, negative_prompt="", 
                      quality="hd", style="vivid", guidance_scale=7.5, steps=50, strength=0.8):
        """
        万擎即梦4.0图生图 - 支持4K超高清、多图生成、风格控制等高级功能
        
        支持的功能:
        - 4K超高清图像生成
        - 多图像生成 (1-4张)
        - 可重复结果 (种子控制)
        - 负面提示词过滤
        - 质量和风格控制
        - 精细的引导参数调节
        - 图像变化强度控制
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
                print(f"[万擎即梦4.0图生图] 使用输入图像tensor，尺寸: {image.shape}")
                print(f"[万擎即梦4.0图生图] 图像格式: data URI (长度: {len(image_input)} 字符)")
            elif image_url and image_url.strip():
                # 使用图像URL
                image_input = image_url.strip()
                print(f"[万擎即梦4.0图生图] 使用图像URL: {image_input}")
                # 验证URL格式
                if not (image_input.startswith('http://') or image_input.startswith('https://') or image_input.startswith('data:')):
                    print(f"[万擎即梦4.0图生图] 警告: URL格式可能不正确，应以http://、https://或data:开头")
            else:
                raise ValueError("必须提供输入图像或图像URL")

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
                "model": "doubao-seedream-4-0-250828",
                "prompt": prompt.strip(),
                "image": image_input,
                "size": size,
                "sequential_image_generation": sequential_image_generation,
                "stream": stream,
                "response_format": response_format,
                "watermark": watermark
            }
            
            # 添加图像数量
            if n > 1:
                payload["n"] = n
                
            # 添加随机种子
            if seed != -1:
                payload["seed"] = seed
                
            # 添加负面提示词
            if negative_prompt and negative_prompt.strip():
                payload["negative_prompt"] = negative_prompt.strip()
                
            # 添加质量设置
            if quality != "hd":
                payload["quality"] = quality
                
            # 添加风格设置
            if style != "vivid":
                payload["style"] = style
                
            # 添加引导强度
            if guidance_scale != 7.5:
                payload["guidance_scale"] = guidance_scale
                
            # 添加推理步数
            if steps != 50:
                payload["steps"] = steps
                
            # 添加图像变化强度
            if strength != 0.8:
                payload["strength"] = strength
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-JiMeng-4.0-I2I/1.0"
            }
            
            print(f"[万擎即梦4.0图生图] 发送请求到: {url}")
            print(f"[万擎即梦4.0图生图] 请求参数:")
            print(f"  - model: doubao-seedream-4-0-250828")
            print(f"  - prompt: {prompt.strip()}")
            print(f"  - image: {'base64数据' if image is not None else image_input}")
            print(f"  - size: {size}")
            print(f"  - n: {n}")
            if seed != -1:
                print(f"  - seed: {seed}")
            if negative_prompt and negative_prompt.strip():
                print(f"  - negative_prompt: {negative_prompt.strip()[:50]}...")
            if quality != "hd":
                print(f"  - quality: {quality}")
            if style != "vivid":
                print(f"  - style: {style}")
            if guidance_scale != 7.5:
                print(f"  - guidance_scale: {guidance_scale}")
            if steps != 50:
                print(f"  - steps: {steps}")
            if strength != 0.8:
                print(f"  - strength: {strength}")
            print(f"  - sequential_image_generation: {sequential_image_generation}")
            print(f"  - stream: {stream}")
            print(f"  - response_format: {response_format}")
            print(f"  - watermark: {watermark}")
            
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
            
            print(f"[万擎即梦4.0图生图] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_text = response.text if response.text else "空响应"
                print(f"[万擎即梦4.0图生图] 响应内容: {response_text}")
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
            
            print(f"[万擎即梦4.0图生图] 成功生成 {len(image_data)} 张图像")
            
            for idx, item in enumerate(image_data):
                if 'b64_json' in item:
                    # 处理 base64 编码的图像
                    b64_data = item['b64_json']
                    image_size = item.get('size', '未知')
                    print(f"[万擎即梦4.0图生图] API返回的图像尺寸: {image_size}")
                    
                    image_bytes = base64.b64decode(b64_data)
                    result_image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB（如果不是的话）
                    if result_image.mode != 'RGB':
                        result_image = result_image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(result_image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    print(f"[万擎即梦4.0图生图] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    image_url_result = item['url']
                    image_size = item.get('size', '未知')
                    print(f"[万擎即梦4.0图生图] 收到图像URL: {image_url_result}")
                    print(f"[万擎即梦4.0图生图] API返回的图像尺寸: {image_size}")
                    
                    try:
                        # 配置代理
                        download_kwargs = {"timeout": 30}
                        if use_proxy:
                            download_kwargs["proxies"] = {"http": None, "https": None}
                        
                        img_response = requests.get(image_url_result, **download_kwargs)
                        img_response.raise_for_status()
                        result_image = Image.open(io.BytesIO(img_response.content))
                        
                        # 转换为RGB
                        if result_image.mode != 'RGB':
                            result_image = result_image.convert('RGB')
                        
                        # 转换为tensor
                        image_np = np.array(result_image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        
                        print(f"[万擎即梦4.0图生图] 下载图像 {idx + 1}: 实际尺寸{result_image.size}, 模式: {result_image.mode}")
                        
                    except Exception as e:
                        print(f"[万擎即梦4.0图生图] 下载图像失败: {str(e)}")
                        continue
            
            if not images_tensor:
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage = response_data.get('usage', {})
            usage_info = f"万擎即梦4.0图生图结果:\n"
            usage_info += f"- 模型: doubao-seedream-4-0-250828\n"
            usage_info += f"- 请求尺寸: {size}\n"
            
            # 显示实际生成的图像尺寸
            actual_sizes = []
            for item in image_data:
                if 'size' in item:
                    actual_sizes.append(item['size'])
            if actual_sizes:
                usage_info += f"- 实际尺寸: {', '.join(actual_sizes)}\n"
            
            usage_info += f"- 响应格式: {response_format}\n"
            usage_info += f"- 请求图像数量: {n}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            usage_info += f"- 输入图像: {'Tensor' if image is not None else 'URL'}\n"
            
            if seed != -1:
                usage_info += f"- 随机种子: {seed}\n"
            if negative_prompt and negative_prompt.strip():
                usage_info += f"- 负面提示词: {negative_prompt.strip()[:50]}{'...' if len(negative_prompt.strip()) > 50 else ''}\n"
            if quality != "hd":
                usage_info += f"- 图像质量: {quality}\n"
            if style != "vivid":
                usage_info += f"- 图像风格: {style}\n"
            if guidance_scale != 7.5:
                usage_info += f"- 引导强度: {guidance_scale}\n"
            if steps != 50:
                usage_info += f"- 推理步数: {steps}\n"
            if strength != 0.8:
                usage_info += f"- 变化强度: {strength}\n"
                
            usage_info += f"- 顺序生成: {sequential_image_generation}\n"
            usage_info += f"- 流式响应: {'是' if stream else '否'}\n"
            usage_info += f"- 水印: {'是' if watermark else '否'}\n"
            
            if usage:
                usage_info += f"- 生成图像统计: {usage.get('generated_images', 0)}\n"
                usage_info += f"- 输出Token: {usage.get('output_tokens', 0)}\n"
                usage_info += f"- 总计Token: {usage.get('total_tokens', usage.get('output_tokens', 0))}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[万擎即梦4.0图生图] 图像生成完成")
            print(f"[万擎即梦4.0图生图] {usage_info}")
            
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
    "WanQingJiMeng40ImageToImage": WanQingJiMeng40ImageToImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanQingJiMeng40ImageToImage": "万擎即梦4.0图生图"
}
