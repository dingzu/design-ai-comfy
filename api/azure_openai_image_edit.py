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

class AzureOpenAIImageEditNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "Azure OpenAI API密钥"
                }),
                "endpoint": ("STRING", {
                    "default": "https://xiaolvgongcheng-ee-openai-swedencentral.openai.azure.com/",
                    "tooltip": "Azure OpenAI 端点 URL"
                }),
                "deployment_name": ("STRING", {
                    "default": "xiaolvgongcheng-ee-openai-swedencentral-gpt-image-1",
                    "tooltip": "Azure OpenAI 部署名称"
                }),
                "api_version": ("STRING", {
                    "default": "2025-04-01-preview",
                    "tooltip": "Azure OpenAI API 版本"
                }),
                "image": ("IMAGE", {
                    "tooltip": "待编辑的原始图像"
                }),
                "prompt": ("STRING", {
                    "default": "Add blue sky",
                    "multiline": True,
                    "tooltip": "编辑描述提示词"
                }),
                "image_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量"
                }),
                "image_size": (["1024x1024", "1024x1536", "1536x1024"], {
                    "default": "1024x1024",
                    "tooltip": "输出图像尺寸"
                }),
                "quality": (["low", "medium", "high"], {
                    "default": "high",
                    "tooltip": "图像质量"
                }),
                "output_format": (["PNG", "JPEG"], {
                    "default": "PNG",
                    "tooltip": "输出格式"
                }),
                "max_file_size_mb": ("FLOAT", {
                    "default": 4.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5,
                    "tooltip": "图片压缩的最大文件大小（MB），避免Payload Too Large错误"
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
                "mask": ("MASK", {
                    "tooltip": "编辑遮罩（可选）。白色区域表示要编辑的部分，不提供则编辑整个图像"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "edit_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        pass

    def tensor_to_pil(self, tensor):
        """将tensor转换为PIL图像"""
        # 处理batch维度
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        # 转换为numpy并确保在0-255范围内
        np_image = tensor.cpu().numpy()
        if np_image.max() <= 1.0:
            np_image = (np_image * 255).astype(np.uint8)
        else:
            np_image = np.clip(np_image, 0, 255).astype(np.uint8)
        
        return Image.fromarray(np_image)

    def mask_to_pil(self, mask_tensor, target_size=None):
        """将MASK tensor转换为PIL图像（带alpha通道的PNG格式）"""
        # 处理batch维度
        if len(mask_tensor.shape) == 3:
            mask_tensor = mask_tensor[0]  # 取第一个batch
        elif len(mask_tensor.shape) == 4:
            mask_tensor = mask_tensor[0, 0]  # 取第一个batch的第一个通道
        
        # 转换为numpy并确保在0-255范围内
        mask_np = mask_tensor.cpu().numpy()
        if mask_np.max() <= 1.0:
            mask_np = (mask_np * 255).astype(np.uint8)
        else:
            mask_np = np.clip(mask_np, 0, 255).astype(np.uint8)
        
        # 创建PIL图像从mask数据
        height, width = mask_np.shape
        mask_pil = Image.fromarray(mask_np, mode='L')
        
        # 如果提供了目标尺寸，调整遮罩尺寸以匹配原始图像
        if target_size is not None and (width, height) != target_size:
            print(f"[Azure OpenAI 编辑] 调整遮罩尺寸从 {(width, height)} 到 {target_size}")
            mask_pil = mask_pil.resize(target_size, Image.Resampling.LANCZOS)
        
        return mask_pil

    def compress_image(self, image, max_size_mb=4.0, format="JPEG", quality=85, target_size=None):
        """压缩图像到指定大小以下，可选保持目标尺寸"""
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        # 如果是遮罩图像（可能需要alpha通道），保持PNG格式
        if format == "PNG" and image.mode in ['RGBA', 'LA', 'L']:
            # 对于PNG遮罩，使用更激进的压缩策略
            current_quality = 9  # PNG压缩级别 (0-9, 9为最高压缩)
            
            # 先尝试不缩小尺寸，只调整压缩级别
            original_size = image.size
            scale_factor = 1.0
            
            while True:
                buffer = io.BytesIO()
                temp_image = image.copy()
                
                # 如果需要保持目标尺寸（如遮罩图像），即使压缩后也要调整回目标尺寸
                if target_size is not None and temp_image.size != target_size:
                    temp_image = temp_image.resize(target_size, Image.Resampling.LANCZOS)
                elif scale_factor < 1.0:
                    # 只有在没有目标尺寸限制时才缩小图像
                    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                    temp_image = temp_image.resize(new_size, Image.Resampling.LANCZOS)
                
                temp_image.save(buffer, format="PNG", optimize=True, compress_level=current_quality)
                
                if buffer.tell() <= max_size_bytes or (target_size is None and scale_factor <= 0.3):
                    buffer.seek(0)
                    final_size = temp_image.size
                    return buffer.getvalue(), final_size
                
                # 如果有目标尺寸限制，优先降低压缩质量而不是缩小尺寸
                if target_size is not None:
                    if current_quality > 0:
                        current_quality = max(0, current_quality - 1)
                    else:
                        # 质量已经到最低，接受当前结果
                        buffer.seek(0)
                        final_size = temp_image.size
                        return buffer.getvalue(), final_size
                else:
                    scale_factor *= 0.8
        else:
            # 对于JPEG格式的普通图像
            current_quality = quality
            scale_factor = 1.0
            original_size = image.size
            
            # 确保是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            while current_quality >= 20:
                buffer = io.BytesIO()
                temp_image = image.copy()
                
                # 如果需要保持目标尺寸，调整到目标尺寸
                if target_size is not None and temp_image.size != target_size:
                    temp_image = temp_image.resize(target_size, Image.Resampling.LANCZOS)
                elif current_quality == 20 and scale_factor > 0.3:
                    # 只有在没有目标尺寸限制时才缩小图像
                    scale_factor *= 0.8
                    new_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
                    temp_image = temp_image.resize(new_size, Image.Resampling.LANCZOS)
                    current_quality = quality  # 重置质量
                
                temp_image.save(buffer, format="JPEG", quality=current_quality, optimize=True)
                
                if buffer.tell() <= max_size_bytes:
                    buffer.seek(0)
                    final_size = temp_image.size
                    return buffer.getvalue(), final_size
                
                current_quality -= 10
        
        # 如果还是太大，返回最后的结果
        buffer.seek(0)
        final_size = temp_image.size
        return buffer.getvalue(), final_size

    def edit_image(self, api_key, endpoint, deployment_name, api_version, image, prompt, 
                   image_count, image_size, quality, output_format, max_file_size_mb, timeout, mask=None):
        """
        Azure OpenAI 图像编辑
        """
        # 用于调试的请求信息
        debug_info = {
            "url": "",
            "headers": {},
            "files_info": {},
            "request_size": 0,
            "error": None,
            "response_status": None,
            "response_content": ""
        }
        
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                debug_info["error"] = "API Key验证失败"
                print(f"[Azure OpenAI 编辑] 调试信息: {debug_info}")
                raise ValueError("API Key不能为空，请从Azure门户获取API密钥")
            
            if not endpoint or endpoint.strip() == "":
                debug_info["error"] = "端点验证失败"
                print(f"[Azure OpenAI 编辑] 调试信息: {debug_info}")
                raise ValueError("Azure OpenAI 端点不能为空")
            
            if not deployment_name or deployment_name.strip() == "":
                debug_info["error"] = "部署名称验证失败"
                print(f"[Azure OpenAI 编辑] 调试信息: {debug_info}")
                raise ValueError("部署名称不能为空")
            
            if not prompt or prompt.strip() == "":
                debug_info["error"] = "编辑描述验证失败"
                print(f"[Azure OpenAI 编辑] 调试信息: {debug_info}")
                raise ValueError("编辑描述不能为空")

            # 处理端点URL
            base_endpoint = endpoint.strip().rstrip('/')
            if not base_endpoint.startswith('http'):
                base_endpoint = f"https://{base_endpoint}"
            
            print(f"[Azure OpenAI 编辑] 使用尺寸: {image_size}")

            # 转换输入图像
            print(f"[Azure OpenAI 编辑] 开始处理输入图像...")
            
            # 转换原始图像为PIL
            input_image = self.tensor_to_pil(image)
            print(f"[Azure OpenAI 编辑] 原始图像尺寸: {input_image.size}, 模式: {input_image.mode}")
            
            # 转换遮罩图像为PIL
            mask_image = self.mask_to_pil(mask, input_image.size) if mask is not None else None
            if mask_image is not None:
                print(f"[Azure OpenAI 编辑] 遮罩图像尺寸: {mask_image.size}, 模式: {mask_image.mode}")
                # 验证尺寸是否匹配
                if mask_image.size != input_image.size:
                    print(f"[Azure OpenAI 编辑] 警告: 遮罩尺寸 {mask_image.size} 与原始图像尺寸 {input_image.size} 不匹配")
                else:
                    print(f"[Azure OpenAI 编辑] 确认: 遮罩尺寸与原始图像尺寸匹配 {input_image.size}")
            else:
                print("[Azure OpenAI 编辑] 未提供遮罩图像，将编辑整个原始图像")

            # 压缩图像以避免Payload Too Large错误
            print(f"[Azure OpenAI 编辑] 压缩图像，最大大小: {max_file_size_mb}MB")
            
            # 压缩原始图像
            image_data, compressed_size = self.compress_image(
                input_image, 
                max_size_mb=max_file_size_mb * 0.6,  # 给原始图像分配60%的空间
                format="PNG",  # Azure OpenAI 要求PNG格式
                quality=85
            )
            print(f"[Azure OpenAI 编辑] 原始图像压缩后大小: {len(image_data) / 1024:.1f}KB, 尺寸: {compressed_size}")
            
            # 压缩遮罩图像
            mask_data = None
            mask_compressed_size = None
            if mask_image is not None:
                mask_data, mask_compressed_size = self.compress_image(
                    mask_image,
                    max_size_mb=max_file_size_mb * 0.4,  # 给遮罩图像分配40%的空间
                    format="PNG",  # 遮罩必须是PNG格式
                    target_size=input_image.size  # 确保压缩后的遮罩尺寸与原始图像一致
                )
                print(f"[Azure OpenAI 编辑] 遮罩图像压缩后大小: {len(mask_data) / 1024:.1f}KB, 尺寸: {mask_compressed_size}")
            else:
                print(f"[Azure OpenAI 编辑] 跳过遮罩图像压缩（未提供遮罩）")

            # 构建Azure OpenAI API URL - 使用部署特定的端点
            url = f"{base_endpoint}/openai/deployments/{deployment_name}/images/edits?api-version={api_version}"
            debug_info["url"] = url
            
            # 构建multipart/form-data请求（按照成功的curl格式）
            files = {
                'image[]': ('beach.png', image_data, 'image/png'),  # 使用 image[] 格式
                'prompt': (None, prompt.strip()),
                'model': (None, 'gpt-image-1'),  # 添加模型参数
                'n': (None, str(image_count)),
                'size': (None, image_size),
                'quality': (None, quality)
            }

            if mask_data is not None:
                files['mask'] = ('mask.png', mask_data, 'image/png')
            
            # 设置请求头（requests会自动设置multipart/form-data的Content-Type）
            headers = {
                "api-key": api_key.strip(),
                "User-Agent": "ComfyUI-Azure-OpenAI-Edit/1.0"
            }
            debug_info["headers"] = {k: v if k != "api-key" else "***隐藏***" for k, v in headers.items()}
            
            # 记录文件信息用于调试
            debug_info["files_info"] = {
                'image[]': {
                    'filename': 'beach.png',
                    'size_kb': len(image_data) / 1024,
                    'content_type': 'image/png'
                },
                'prompt': prompt.strip(),
                'model': 'gpt-image-1',
                'n': str(image_count),
                'size': image_size,
                'quality': quality
            }
            
            if mask_data is not None:
                debug_info["files_info"]['mask'] = {
                    'filename': 'mask.png',
                    'size_kb': len(mask_data) / 1024,
                    'content_type': 'image/png'
                }
            
            total_request_size = len(image_data) + (len(mask_data) if mask_data is not None else 0)
            debug_info["request_size"] = total_request_size / 1024  # KB
            
            print(f"[Azure OpenAI 编辑] 发送请求到: {url}")
            print(f"[Azure OpenAI 编辑] 请求参数:")
            print(f"  - deployment: {deployment_name}")
            print(f"  - api_version: {api_version}")
            print(f"  - model: gpt-image-1")
            print(f"  - prompt: {prompt.strip()}")
            print(f"  - n: {image_count}")
            print(f"  - size: {image_size}")
            print(f"  - quality: {quality}")
            print(f"  - 原始图像: {len(image_data) / 1024:.1f}KB")
            if mask_data is not None:
                print(f"  - 遮罩图像: {len(mask_data) / 1024:.1f}KB")
            print(f"  - 总请求大小: {total_request_size / 1024:.1f}KB")
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=timeout
            )
            
            debug_info["response_status"] = response.status_code
            print(f"[Azure OpenAI 编辑] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
                debug_info["response_content"] = json.dumps(response_data, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 如果JSON解析失败，显示原始响应内容以便调试
                response_text = response.text if response.text else "空响应"
                debug_info["response_content"] = response_text
                debug_info["error"] = f"JSON解析失败，状态码: {response.status_code}"
                
                print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
                print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
                print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 编辑] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 编辑] 响应内容: {response_text}")
                print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 编辑] ==================")
                
                if response.status_code == 404:
                    raise ValueError(f"API端点不存在 (404): {url}\n响应内容: {response_text}\n\n💡 建议: \n1. 检查Azure OpenAI端点是否正确\n2. 确认部署名称是否正确\n3. 确认API版本是否支持图像编辑功能")
                elif response.status_code == 401:
                    raise ValueError(f"认证失败 (401): {response_text}\n\n💡 建议: \n1. 检查API密钥是否正确\n2. 确认API密钥是否有权限访问此部署")
                else:
                    raise ValueError(f"无效的JSON响应 (状态码: {response.status_code}): {response_text}")
            
            # 检查响应状态
            if not response.ok:
                error_msg = response_data.get('error', {}).get('message', '未知错误')
                error_type = response_data.get('error', {}).get('type', 'unknown_error')
                error_code = response_data.get('error', {}).get('code', 'unknown')
                
                debug_info["error"] = f"API错误 [{error_code}]: {error_msg} (类型: {error_type})"
                
                print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
                print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
                print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 编辑] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 编辑] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 编辑] ==================")
                
                # 提供详细的错误信息和解决建议
                if 'payload too large' in error_msg.lower() or response.status_code == 413:
                    error_msg += f"\n\n💡 建议: 请求体过大（当前约{total_request_size / 1024:.1f}KB）"
                    error_msg += f"\n  - 尝试减小 max_file_size_mb 参数（当前: {max_file_size_mb}MB）"
                    error_msg += f"\n  - 或使用更小的输入图像"
                elif 'invalid image' in error_msg.lower():
                    error_msg += "\n\n💡 建议: 图像格式不正确"
                    error_msg += "\n  - 确保图像是有效的PNG格式"
                    error_msg += "\n  - 图像尺寸应小于4MB"
                elif 'invalid mask' in error_msg.lower():
                    error_msg += "\n\n💡 建议: 遮罩图像格式不正确"
                    error_msg += "\n  - 遮罩图像必须是PNG格式"
                    error_msg += "\n  - 遮罩必须与原始图像具有相同的尺寸"
                elif response.status_code == 401:
                    error_msg += "\n\n💡 建议: 检查API密钥是否有效，从Azure门户获取正确的API密钥"
                elif response.status_code == 429:
                    error_msg += "\n\n💡 建议: 请求频率过高，请稍后重试"
                elif response.status_code == 403:
                    error_msg += "\n\n💡 建议: 权限不足，检查API密钥的权限和部署访问权限"
                
                raise ValueError(f"API错误 [{error_code}]: {error_msg}")
            
            # 处理编辑后的图像
            images_tensor = []
            image_data_list = response_data.get('data', [])
            
            if not image_data_list:
                debug_info["error"] = "响应中没有图像数据"
                print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
                print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
                print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 编辑] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 编辑] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 编辑] ==================")
                raise ValueError("响应中没有图像数据")
            
            print(f"[Azure OpenAI 编辑] 成功生成 {len(image_data_list)} 张图像")
            
            for idx, item in enumerate(image_data_list):
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
                    
                    print(f"[Azure OpenAI 编辑] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    print(f"[Azure OpenAI 编辑] 收到图像URL: {item['url']}")
                    try:
                        # 下载URL图像
                        img_response = requests.get(item['url'], timeout=30)
                        if img_response.ok:
                            result_image = Image.open(io.BytesIO(img_response.content))
                            
                            # 转换为RGB（如果不是的话）
                            if result_image.mode != 'RGB':
                                result_image = result_image.convert('RGB')
                            
                            # 转换为tensor
                            image_np = np.array(result_image).astype(np.float32) / 255.0
                            image_tensor = torch.from_numpy(image_np)[None,]
                            images_tensor.append(image_tensor)
                            
                            print(f"[Azure OpenAI 编辑] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                        else:
                            print(f"[Azure OpenAI 编辑] 下载图像失败: {img_response.status_code}")
                    except Exception as e:
                        print(f"[Azure OpenAI 编辑] 处理URL图像失败: {str(e)}")
            
            if not images_tensor:
                debug_info["error"] = "没有可用的图像数据"
                print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
                print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
                print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 编辑] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 编辑] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 编辑] ==================")
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage_info = f"Azure OpenAI 图像编辑使用情况:\n"
            usage_info += f"- 端点: {base_endpoint}\n"
            usage_info += f"- 部署: {deployment_name}\n"
            usage_info += f"- API版本: {api_version}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            usage_info += f"- 原始图像压缩: {compressed_size} -> {len(image_data) / 1024:.1f}KB\n"
            if mask_data is not None:
                usage_info += f"- 遮罩图像压缩: {mask_compressed_size} -> {len(mask_data) / 1024:.1f}KB"
            else:
                usage_info += f"- 遮罩图像: 未提供（编辑整个图像）"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[Azure OpenAI 编辑] 图像编辑完成")
            print(f"[Azure OpenAI 编辑] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except requests.exceptions.Timeout:
            debug_info["error"] = f"请求超时（{timeout}秒）"
            print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
            print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
            print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 编辑] ==================")
            raise ValueError(f"请求超时（{timeout}秒）。图像编辑可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            debug_info["error"] = "网络连接错误"
            print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
            print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
            print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 编辑] ==================")
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. Azure OpenAI端点地址是否可访问\n3. 防火墙设置")
        except requests.exceptions.RequestException as e:
            debug_info["error"] = f"请求异常: {str(e)}"
            print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
            print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
            print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 编辑] ==================")
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            debug_info["error"] = f"未知异常: {str(e)}"
            print(f"[Azure OpenAI 编辑] === 详细调试信息 ===")
            print(f"[Azure OpenAI 编辑] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 编辑] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 编辑] 请求体大小: {debug_info['request_size']:.1f}KB")
            print(f"[Azure OpenAI 编辑] 文件信息: {json.dumps(debug_info['files_info'], ensure_ascii=False, indent=2)}")
            if debug_info["response_status"]:
                print(f"[Azure OpenAI 编辑] 响应状态码: {debug_info['response_status']}")
            if debug_info["response_content"]:
                print(f"[Azure OpenAI 编辑] 响应内容: {debug_info['response_content']}")
            print(f"[Azure OpenAI 编辑] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 编辑] ==================")
            raise ValueError(f"图像编辑失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "AzureOpenAIImageEdit": AzureOpenAIImageEditNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AzureOpenAIImageEdit": "Azure OpenAI 图像编辑"
}
