import torch
import numpy as np
import requests
import time
import json
import base64
import io
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple

class GeminiImageNodeV2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["prod", "staging", "idc", "overseas", "domestic"], {
                    "default": "prod",
                    "tooltip": "选择万擎网关环境"
                }),
                "model": (["gemini-2.5-flash-image", "gemini-3-pro-image-preview"], {
                    "default": "gemini-2.5-flash-image",
                    "tooltip": "选择Gemini模型版本"
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
                }),
                "custom_base_url": ("STRING", {
                    "default": "",
                    "tooltip": "自定义API基础URL（优先级高于环境选择）"
                }),
                "custom_endpoint": ("STRING", {
                    "default": "",
                    "tooltip": "自定义API端点路径（留空则根据模型自动选择）"
                })
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "要编辑的输入图像（仅在图片编辑模式下需要）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "success", "message", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api-v2"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod-sgp.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal",
            "overseas": "http://llm-gateway-sgp.internal",
            "domestic": "http://llm-gateway.internal"
        }
        self.execution_logs = []
    
    def _log(self, message, level="INFO"):
        """统一的日志记录方法"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_logs.append(log_entry)
    
    def _get_execution_log(self):
        """获取完整的执行日志"""
        return "\n".join(self.execution_logs)
    
    def _clear_logs(self):
        """清空日志"""
        self.execution_logs = []
    
    def _print_and_format_logs(self):
        """打印并格式化日志输出"""
        log_output = self._get_execution_log()
        print("\n" + "="*80)
        print("Gemini 图像生成 V2 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

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
            
            self._log(f"图像转换完成: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
            
        except Exception as e:
            raise ValueError(f"图像转换失败: {str(e)}")

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
                    self._log(f"{spaces}{key}: {type(value).__name__} (length: {len(value)})")
                    if indent < 3:  # 限制递归深度
                        self._debug_response_structure(value, indent + 1)
                else:
                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    self._log(f"{spaces}{key}: {type(value).__name__} = {value_str}")
        elif isinstance(obj, list):
            self._log(f"{spaces}[list with {len(obj)} items]")
            for i, item in enumerate(obj[:3]):  # 只显示前3个元素
                self._log(f"{spaces}[{i}]:")
                if indent < 3:
                    self._debug_response_structure(item, indent + 1)

    def generate_image(self, environment, model, api_key, prompt, mode, timeout, use_proxy, custom_base_url="", custom_endpoint="", image=None):
        """
        Gemini 图像生成或编辑 V2
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log(f"开始Gemini图像任务 (模型: {model})")
        
        try:
            # 验证必需参数
            self._log("开始参数验证")
            if not api_key or api_key.strip() == "":
                self._log("参数验证失败: API Key为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "API Key不能为空，请联系 @于淼 获取万擎网关key"
                return (blank_image, False, error_msg, "", log_output)
            
            if not prompt or prompt.strip() == "":
                self._log("参数验证失败: 提示词为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "提示词不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            # 验证图片编辑模式下的输入图像
            if mode == "image_edit" and image is None:
                self._log("参数验证失败: 图片编辑模式未提供输入图像", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "图片编辑模式下必须提供输入图像"
                return (blank_image, False, error_msg, "", log_output)

            self._log("参数验证通过")

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
                self._log(f"使用自定义base_url: {base_url}")
            else:
                base_url = self.environments[environment]
                self._log(f"使用环境配置: {environment} -> {base_url}")
            
            # 确定endpoint
            if custom_endpoint and custom_endpoint.strip():
                endpoint = custom_endpoint.strip()
                self._log(f"使用自定义endpoint: {endpoint}")
            else:
                if model == "gemini-3-pro-image-preview":
                    endpoint = "/ai-serve/v1/gemini-3-pro-image-preview:generateContent"
                else: # gemini-2.5-flash-image
                    endpoint = "/ai-serve/v1/gemini-2.5-flash-image:generateContent"
                self._log(f"根据模型 {model} 选择endpoint: {endpoint}")
            
            endpoint = endpoint.lstrip('/')
            api_url = f"{base_url}/{endpoint}"
            self._log(f"完整API地址: {api_url}")
            
            # 构建请求体
            self._log("构建请求体")
            parts = [{"text": prompt.strip()}]
            
            # 如果是图片编辑模式，添加图像数据
            if mode == "image_edit" and image is not None:
                try:
                    image_base64 = self._image_to_base64(image)
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    })
                    self._log("已添加图像数据到请求体")
                except Exception as e:
                    self._log(f"处理输入图像失败: {str(e)}", "ERROR")
                    log_output = self._print_and_format_logs()
                    blank_image = self._create_blank_image()
                    error_msg = f"处理输入图像失败: {str(e)}"
                    return (blank_image, False, error_msg, "", log_output)
            
            payload = {
                "contents": [{
                    "parts": parts
                }]
            }
            
            self._log(f"模式: {mode}")
            self._log(f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-Gemini-Image-V2/1.0"
            }
            
            # 配置代理
            request_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": timeout
            }
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
                self._log("API请求代理: 禁用系统代理")
            else:
                self._log("API请求代理: 使用系统代理")
            
            # 发送请求
            self._log("发送API请求...")
            response = requests.post(api_url, **request_kwargs)
            
            self._log(f"收到响应, 状态码: {response.status_code}")
            
            # 解析响应
            self._log("解析响应JSON")
            try:
                result = response.json()
                self._log("响应JSON解析成功")
            except json.JSONDecodeError as e:
                response_text = response.text if response.text else "空响应"
                self._log(f"JSON解析失败: {str(e)}", "ERROR")
                self._log(f"响应内容: {response_text[:200]}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = f"无效的JSON响应 (状态码: {response.status_code}): {response_text}"
                return (blank_image, False, error_msg, "", log_output)
            
            # 检查响应状态
            if not response.ok:
                error_msg = result.get('error', {}).get('message', '未知错误')
                error_code = result.get('error', {}).get('code', 'unknown')
                
                self._log(f"API返回错误: {error_msg}", "ERROR")
                
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                full_error_msg = f"API错误 [{error_code}]: {error_msg}"
                return (blank_image, False, full_error_msg, "", log_output)
            
            # 处理结果
            self._log("开始处理响应结果")
            images_tensor = []
            image_count = 0
            image_data_found = False
            
            # 方法1：检查根级的data字段
            if "data" in result and result["data"]:
                try:
                    self._log(f"在根级找到data字段")
                    image_data = base64.b64decode(result["data"])
                    image_obj = Image.open(io.BytesIO(image_data))
                    
                    if image_obj.mode != 'RGB':
                        image_obj = image_obj.convert('RGB')
                    
                    image_np = np.array(image_obj).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    image_count += 1
                    image_data_found = True
                    self._log(f"图像 {image_count}: {image_obj.size}, 模式: {image_obj.mode}")
                    
                except Exception as e:
                    self._log(f"处理根级data字段失败: {str(e)}", "ERROR")
            
            # 方法2：检查标准Gemini格式 candidates.content.parts
            if not image_data_found:
                candidates = result.get("candidates", [])
                if candidates:
                    self._log(f"处理 {len(candidates)} 个候选结果")
                    for idx, candidate in enumerate(candidates):
                        content = candidate.get("content", {})
                        parts = content.get("parts", [])
                        self._log(f"候选结果 {idx} 有 {len(parts)} 个parts")
                        
                        for part_idx, part in enumerate(parts):
                            image_data_str = None
                            
                            if "inlineData" in part and part["inlineData"]:
                                inline_data = part["inlineData"]
                                if "data" in inline_data and inline_data["data"]:
                                    image_data_str = inline_data["data"]
                                    self._log(f"在candidates[{idx}].content.parts[{part_idx}].inlineData找到图像数据")
                            
                            elif "data" in part and part["data"]:
                                image_data_str = part["data"]
                                self._log(f"在candidates[{idx}].content.parts[{part_idx}]找到直接data字段")
                            
                            if image_data_str:
                                try:
                                    image_data = base64.b64decode(image_data_str)
                                    image_obj = Image.open(io.BytesIO(image_data))
                                    
                                    if image_obj.mode != 'RGB':
                                        image_obj = image_obj.convert('RGB')
                                    
                                    image_np = np.array(image_obj).astype(np.float32) / 255.0
                                    image_tensor = torch.from_numpy(image_np)[None,]
                                    images_tensor.append(image_tensor)
                                    image_count += 1
                                    image_data_found = True
                                    self._log(f"图像 {image_count}: {image_obj.size}, 模式: {image_obj.mode}")
                                    
                                except Exception as e:
                                    self._log(f"处理图像 {idx}-{part_idx} 时出错: {str(e)}", "ERROR")
                                    continue
                else:
                    self._log(f"响应中没有candidates字段", "WARN")

            # 方法3：递归搜索任何可能的data字段
            if not image_data_found:
                self._log(f"递归搜索data字段...")
                found_data_fields = self._find_data_fields(result)
                for field_path, data_value in found_data_fields:
                    try:
                        self._log(f"尝试处理data字段: {field_path}")
                        image_data = base64.b64decode(data_value)
                        image_obj = Image.open(io.BytesIO(image_data))
                        
                        if image_obj.mode != 'RGB':
                            image_obj = image_obj.convert('RGB')
                        
                        image_np = np.array(image_obj).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        image_count += 1
                        image_data_found = True
                        self._log(f"图像 {image_count}: {image_obj.size}, 模式: {image_obj.mode}")
                        break
                        
                    except Exception as e:
                        self._log(f"处理data字段 {field_path} 失败: {str(e)}", "WARN")
                        continue

            if not images_tensor:
                self._log("没有成功处理的图像", "ERROR")
                self._log("完整响应结构调试:")
                self._debug_response_structure(result)
                
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "没有成功处理的图像，请查看日志获取详细信息"
                return (blank_image, False, error_msg, "", log_output)

            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            self._log(f"成功处理 {len(images_tensor)} 张图像")
            
            # 格式化使用信息
            usage_info = f"Gemini 图像生成结果:\n"
            usage_info += f"- 模型: {model}\n"
            usage_info += f"- 模式: {mode}\n"
            usage_info += f"- 生成图像数量: {image_count}\n"
            
            candidates_count = len(result.get("candidates", []))
            if candidates_count > 0:
                usage_info += f"- 候选结果数: {candidates_count}\n"
            
            usage_metadata = result.get('usageMetadata', {})
            if usage_metadata:
                usage_info += f"- 提示Token数: {usage_metadata.get('promptTokenCount', 'N/A')}\n"
                usage_info += f"- 候选Token数: {usage_metadata.get('candidatesTokenCount', 'N/A')}\n"
                usage_info += f"- 总Token数: {usage_metadata.get('totalTokenCount', 'N/A')}"

            self._log(f"API使用信息: {usage_info.replace(chr(10), ' | ')}")
            self._log("任务完成", "SUCCESS")

            log_output = self._print_and_format_logs()
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            return (result_images, True, "图像生成成功", response_json, log_output)

        except requests.exceptions.Timeout:
            self._log(f"请求超时（{timeout}秒）", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"请求超时（{timeout}秒）。"
            return (blank_image, False, error_msg, "", log_output)
        except requests.exceptions.ConnectionError as e:
            self._log(f"网络连接错误: {str(e)}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确"
            return (blank_image, False, error_msg, "", log_output)
        except Exception as e:
            self._log(f"未知异常: {str(e)}", "ERROR")
            import traceback
            self._log(f"异常堆栈: {traceback.format_exc()}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"图像生成失败: {str(e)}"
            return (blank_image, False, error_msg, "", log_output)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "GeminiImageNodeV2": GeminiImageNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiImageNodeV2": "gemini-image-v2"
}
