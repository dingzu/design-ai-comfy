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

class Gemini25FlashImagePreviewNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["prod", "staging", "idc"], {
                    "default": "prod",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "创建一张美丽的风景图",
                    "multiline": True,
                    "tooltip": "图像生成或编辑指令"
                }),
                "mode": (["text_to_image", "image_edit"], {
                    "default": "text_to_image",
                    "tooltip": "选择模式：文生图或图片编辑"
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
                })
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "要编辑的输入图像（仅在图片编辑模式下需要）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "generate_or_edit_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod-sgp.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal"
        }

    def generate_or_edit_image(self, environment, api_key, prompt, mode, timeout, use_proxy, image=None):
        """
        Gemini-2.5-Flash-Image-Preview 图像生成或编辑
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("提示词不能为空")
            
            # 验证图片编辑模式下的输入图像
            if mode == "image_edit" and image is None:
                raise ValueError("图片编辑模式下必须提供输入图像")

            # 构建URL
            base_url = self.environments[environment]
            api_url = f"{base_url}/ai-serve/v1/gemini-2.5-flash-image-preview:generateContent"
            
            # 构建请求体
            parts = [{"text": prompt.strip()}]
            
            # 如果是图片编辑模式，添加图像数据
            if mode == "image_edit" and image is not None:
                image_base64 = self._image_to_base64(image)
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }
                })
            
            payload = {
                "contents": [{
                    "parts": parts
                }]
            }
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-Gemini-Flash-Image/1.0"
            }
            
            print(f"[Gemini Flash Image] 发送请求到: {api_url}")
            print(f"[Gemini Flash Image] 模式: {mode}")
            print(f"[Gemini Flash Image] 提示词: {prompt}")
            
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
            
            print(f"[Gemini Flash Image] 响应状态码: {response.status_code}")
            
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
            return self._process_result(result, mode)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒）。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像{'编辑' if mode == 'image_edit' else '生成'}失败: {str(e)}")

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
            
            # 确保是RGB模式
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=95)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            print(f"[Gemini Flash Image] 图像转换完成: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
            
        except Exception as e:
            raise ValueError(f"图像转换失败: {str(e)}")

    def _process_result(self, result, mode):
        """处理生成结果"""
        try:
            print(f"[Gemini Flash Image] 原始响应结构: {list(result.keys())}")
            
            images_tensor = []
            image_count = 0
            
            # 尝试多种可能的响应格式
            image_data_found = False
            
            # 方法1：检查根级的data字段（基于curl示例）
            if "data" in result and result["data"]:
                try:
                    print(f"[Gemini Flash Image] 在根级找到data字段")
                    image_data = base64.b64decode(result["data"])
                    image = Image.open(io.BytesIO(image_data))
                    
                    # 转换为RGB（如果不是的话）
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    image_count += 1
                    image_data_found = True
                    
                    print(f"[Gemini Flash Image] 图像 {image_count}: {image.size}, 模式: {image.mode}")
                    
                except Exception as e:
                    print(f"[Gemini Flash Image] 处理根级data字段失败: {str(e)}")
            
            # 方法2：检查标准Gemini格式 candidates.content.parts
            if not image_data_found:
                candidates = result.get("candidates", [])
                if candidates:
                    print(f"[Gemini Flash Image] 处理 {len(candidates)} 个候选结果")
                    
                    for idx, candidate in enumerate(candidates):
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])
                        print(f"[Gemini Flash Image] 候选结果 {idx} 有 {len(parts)} 个parts")
                        
                        for part_idx, part in enumerate(parts):
                            # 检查是否包含base64图像数据 - 修复后的格式
                            image_data_str = None
                            
                            # 方法1: 检查inlineData.data（实际API格式）
                            if "inlineData" in part and part["inlineData"]:
                                inline_data = part["inlineData"]
                                if "data" in inline_data and inline_data["data"]:
                                    image_data_str = inline_data["data"]
                                    print(f"[Gemini Flash Image] 在candidates[{idx}].content.parts[{part_idx}].inlineData找到图像数据")
                            
                            # 方法2: 检查直接的data字段（兼容其他格式）
                            elif "data" in part and part["data"]:
                                image_data_str = part["data"]
                                print(f"[Gemini Flash Image] 在candidates[{idx}].content.parts[{part_idx}]找到直接data字段")
                            
                            if image_data_str:
                                try:
                                    # 解码base64图像
                                    image_data = base64.b64decode(image_data_str)
                                    image = Image.open(io.BytesIO(image_data))
                                    
                                    # 转换为RGB（如果不是的话）
                                    if image.mode != 'RGB':
                                        image = image.convert('RGB')
                                    
                                    # 转换为tensor
                                    image_np = np.array(image).astype(np.float32) / 255.0
                                    image_tensor = torch.from_numpy(image_np)[None,]
                                    images_tensor.append(image_tensor)
                                    image_count += 1
                                    image_data_found = True
                                    
                                    print(f"[Gemini Flash Image] 图像 {image_count}: {image.size}, 模式: {image.mode}")
                                    
                                except Exception as e:
                                    print(f"[Gemini Flash Image] 处理图像 {idx}-{part_idx} 时出错: {str(e)}")
                                    continue
                            else:
                                # 调试输出part结构
                                part_keys = list(part.keys()) if isinstance(part, dict) else []
                                print(f"[Gemini Flash Image] part[{part_idx}] 键: {part_keys}")
                else:
                    print(f"[Gemini Flash Image] 响应中没有candidates字段")
            
            # 方法3：递归搜索任何可能的data字段
            if not image_data_found:
                print(f"[Gemini Flash Image] 递归搜索data字段...")
                found_data_fields = self._find_data_fields(result)
                for field_path, data_value in found_data_fields:
                    try:
                        print(f"[Gemini Flash Image] 尝试处理data字段: {field_path}")
                        image_data = base64.b64decode(data_value)
                        image = Image.open(io.BytesIO(image_data))
                        
                        # 转换为RGB（如果不是的话）
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # 转换为tensor
                        image_np = np.array(image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        image_count += 1
                        image_data_found = True
                        
                        print(f"[Gemini Flash Image] 图像 {image_count}: {image.size}, 模式: {image.mode}")
                        break  # 找到一个有效图像就停止
                        
                    except Exception as e:
                        print(f"[Gemini Flash Image] 处理data字段 {field_path} 失败: {str(e)}")
                        continue
            
            if not images_tensor:
                # 详细输出响应结构用于调试
                print(f"[Gemini Flash Image] 完整响应结构调试:")
                self._debug_response_structure(result)
                
                # 提供更详细的错误信息
                error_details = []
                candidates_count = len(result.get("candidates", []))
                error_details.append(f"候选结果数量: {candidates_count}")
                
                if candidates_count > 0:
                    for i, candidate in enumerate(result["candidates"][:2]):  # 只检查前两个
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])
                        error_details.append(f"候选结果 {i}: {len(parts)} 个parts")
                        
                        for j, part in enumerate(parts[:3]):  # 只检查前三个part
                            part_keys = list(part.keys()) if isinstance(part, dict) else []
                            error_details.append(f"  part {j}: 键 {part_keys}")
                            
                            if "inlineData" in part:
                                inline_keys = list(part["inlineData"].keys()) if isinstance(part["inlineData"], dict) else []
                                error_details.append(f"    inlineData: 键 {inline_keys}")
                
                error_msg = "没有成功处理的图像。" + "\n调试信息:\n" + "\n".join(error_details)
                raise ValueError(error_msg)
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage_info = f"使用统计:\n"
            usage_info += f"- 模式: {mode}\n"
            usage_info += f"- 生成图像数量: {image_count}\n"
            
            # 添加候选结果统计
            candidates_count = len(result.get("candidates", []))
            if candidates_count > 0:
                usage_info += f"- 候选结果数: {candidates_count}\n"
            
            # 添加token使用统计（如果有的话）
            usage_metadata = result.get('usageMetadata', {})
            if usage_metadata:
                usage_info += f"- 提示Token数: {usage_metadata.get('promptTokenCount', 'N/A')}\n"
                usage_info += f"- 候选Token数: {usage_metadata.get('candidatesTokenCount', 'N/A')}\n"
                usage_info += f"- 总Token数: {usage_metadata.get('totalTokenCount', 'N/A')}\n"
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            print(f"[Gemini Flash Image] 图像{'编辑' if mode == 'image_edit' else '生成'}完成")
            print(f"[Gemini Flash Image] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except Exception as e:
            raise ValueError(f"结果处理失败: {str(e)}")

    def _find_data_fields(self, obj, path=""):
        """递归查找所有可能的data字段"""
        found_fields = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                # 优先查找inlineData.data结构
                if key.lower() == "inlinedata" and isinstance(value, dict):
                    if "data" in value and isinstance(value["data"], str) and len(value["data"]) > 100:
                        found_fields.append((f"{new_path}.data", value["data"]))
                # 查找直接的data字段
                elif key.lower() == "data" and isinstance(value, str) and len(value) > 100:
                    # 可能是base64图像数据
                    found_fields.append((new_path, value))
                elif isinstance(value, (dict, list)):
                    found_fields.extend(self._find_data_fields(value, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                found_fields.extend(self._find_data_fields(item, f"{path}[{i}]"))
        
        return found_fields

    def _debug_response_structure(self, obj, indent=0):
        """调试输出响应结构"""
        spaces = "  " * indent
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    print(f"{spaces}{key}: {type(value).__name__} (length: {len(value)})")
                    if indent < 3:  # 限制递归深度
                        self._debug_response_structure(value, indent + 1)
                else:
                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"{spaces}{key}: {type(value).__name__} = {value_str}")
        elif isinstance(obj, list):
            print(f"{spaces}[list with {len(obj)} items]")
            for i, item in enumerate(obj[:3]):  # 只显示前3个元素
                print(f"{spaces}[{i}]:")
                if indent < 3:
                    self._debug_response_structure(item, indent + 1)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "Gemini25FlashImagePreview": Gemini25FlashImagePreviewNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Gemini25FlashImagePreview": "Gemini-2.5-Flash 图像预览"
}
