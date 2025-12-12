import torch
import numpy as np
import requests
import time
import json
import base64
import io
from typing import List
from PIL import Image


class GeminiMultiImageAdvancedV2:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "environment": (["prod", "staging", "idc", "overseas", "domestic"], {
                    "default": "prod",
                    "tooltip": "选择万擎网关环境"
                }),
                "model": (["gemini-3-pro-image-preview"], {
                    "default": "gemini-3-pro-image-preview",
                    "tooltip": "固定使用Gemini 3 Pro Image Preview模型"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "创建一张创意图片",
                    "multiline": True,
                    "tooltip": "提示词"
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
                    "tooltip": "是否禁用系统代理（建议保持开启）"
                }),
                "auto_size": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "开启后不下发 generationConfig，交由服务端自动尺寸"
                }),
                "aspect_ratio": (["", "1:1", "4:5", "5:4", "3:4", "4:3", "16:9", "9:16"], {
                    "default": "",
                    "tooltip": "可选输出宽高比（留空使用默认）"
                }),
                "image_size": (["", "1K", "2K", "4K"], {
                    "default": "",
                    "tooltip": "可选输出分辨率（留空使用默认）"
                }),
                "custom_base_url": ("STRING", {
                    "default": "",
                    "tooltip": "自定义API基础URL（优先级高于环境选择）"
                }),
                "custom_endpoint": ("STRING", {
                    "default": "",
                    "tooltip": "自定义API端点路径（留空则使用默认）"
                })
            },
            "optional": {
                "image_1": ("IMAGE", {"tooltip": "可选图像1"}),
                "image_2": ("IMAGE", {"tooltip": "可选图像2"}),
                "image_3": ("IMAGE", {"tooltip": "可选图像3"}),
                "image_4": ("IMAGE", {"tooltip": "可选图像4"}),
                "image_5": ("IMAGE", {"tooltip": "可选图像5"}),
                "image_6": ("IMAGE", {"tooltip": "可选图像6"}),
                "image_7": ("IMAGE", {"tooltip": "可选图像7"}),
                "image_8": ("IMAGE", {"tooltip": "可选图像8"})
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
        self.execution_logs: List[str] = []

    # 基础工具方法
    def _log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_logs.append(log_entry)

    def _get_execution_log(self):
        return "\n".join(self.execution_logs)

    def _clear_logs(self):
        self.execution_logs = []

    def _print_and_format_logs(self):
        log_output = self._get_execution_log()
        print("\n" + "=" * 80)
        print("Gemini 多图高级模式执行日志 V2:")
        print("=" * 80)
        print(log_output)
        print("=" * 80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def _image_to_base64(self, image_tensor):
        try:
            img = image_tensor[0] if len(image_tensor.shape) == 4 else image_tensor
            image_np = (img.cpu().numpy() * 255).astype(np.uint8)
            pil_image = Image.fromarray(image_np)
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=95)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            self._log(f"图像转换完成: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
        except Exception as e:
            raise ValueError(f"图像转换失败: {str(e)}")

    def _find_data_fields(self, obj, path=""):
        found_fields = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if key.lower() == "inlinedata" and isinstance(value, dict):
                    if "data" in value and isinstance(value["data"], str) and len(value["data"]) > 100:
                        found_fields.append((f"{new_path}.data", value["data"]))
                elif key.lower() == "data" and isinstance(value, str) and len(value) > 100:
                    found_fields.append((new_path, value))
                elif isinstance(value, (dict, list)):
                    found_fields.extend(self._find_data_fields(value, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                found_fields.extend(self._find_data_fields(item, f"{path}[{i}]"))
        return found_fields

    def _debug_response_structure(self, obj, indent=0):
        spaces = "  " * indent
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    self._log(f"{spaces}{key}: {type(value).__name__} (length: {len(value)})")
                    if indent < 3:
                        self._debug_response_structure(value, indent + 1)
                else:
                    value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    self._log(f"{spaces}{key}: {type(value).__name__} = {value_str}")
        elif isinstance(obj, list):
            self._log(f"{spaces}[list with {len(obj)} items]")
            for i, item in enumerate(obj[:3]):
                self._log(f"{spaces}[{i}]:")
                if indent < 3:
                    self._debug_response_structure(item, indent + 1)

    def _build_api_url(self, environment, custom_base_url, custom_endpoint):
        if custom_base_url and custom_base_url.strip():
            base_url = custom_base_url.strip().rstrip("/")
            self._log(f"使用自定义base_url: {base_url}")
        else:
            base_url = self.environments[environment]
            self._log(f"使用环境配置: {environment} -> {base_url}")

        if custom_endpoint and custom_endpoint.strip():
            endpoint = custom_endpoint.strip()
            self._log(f"使用自定义endpoint: {endpoint}")
        else:
            endpoint = "/ai-serve/v1/gemini-3-pro-image-preview:generateContent"
            self._log(f"使用默认endpoint: {endpoint}")

        endpoint = endpoint.lstrip("/")
        api_url = f"{base_url}/{endpoint}"
        self._log(f"完整API地址: {api_url}")
        return api_url

    def generate_image(
        self,
        environment,
        model,
        api_key,
        prompt,
        timeout,
        use_proxy,
        auto_size,
        aspect_ratio,
        image_size,
        custom_base_url="",
        custom_endpoint="",
        image_1=None,
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
        image_6=None,
        image_7=None,
        image_8=None,
    ):
        # 准备日志
        self._clear_logs()
        self._log(f"开始Gemini多图高级任务 (模型: {model})")

        try:
            # 参数验证
            self._log("开始参数验证")
            if not api_key or api_key.strip() == "":
                self._log("参数验证失败: API Key为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                return (blank_image, False, "API Key不能为空，请联系 @于淼 获取万擎网关key", "", log_output)

            if not prompt or prompt.strip() == "":
                self._log("参数验证失败: 提示词为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                return (blank_image, False, "提示词不能为空", "", log_output)

            self._log("参数验证通过")

            # 收集图片
            images = [img for img in [image_1, image_2, image_3, image_4, image_5, image_6, image_7, image_8] if img is not None]
            image_count_input = len(images)
            mode = "image_to_image" if image_count_input > 0 else "text_to_image"
            self._log(f"自动检测模式: {mode} (输入图片数量: {image_count_input})")

            # 构建URL
            api_url = self._build_api_url(environment, custom_base_url, custom_endpoint)

            # 构建请求体
            self._log("构建请求体")
            parts = [{"text": prompt.strip()}]
            if images:
                for idx, img in enumerate(images[:8]):
                    try:
                        image_base64 = self._image_to_base64(img)
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        })
                        self._log(f"已添加第 {idx + 1} 张图像到请求体")
                    except Exception as e:
                        self._log(f"处理输入图像 {idx + 1} 失败: {str(e)}", "ERROR")
                        log_output = self._print_and_format_logs()
                        blank_image = self._create_blank_image()
                        return (blank_image, False, f"处理输入图像失败: {str(e)}", "", log_output)

            payload = {
                "contents": [{
                    "parts": parts
                }]
            }

            # generationConfig
            # generationConfig（非自动尺寸模式才下发）
            if not auto_size:
                generation_config = {}
                generation_config["responseModalities"] = ["IMAGE"]  # 固定仅图像
                image_config = {}
                if aspect_ratio:
                    image_config["aspectRatio"] = aspect_ratio
                if image_size:
                    image_config["imageSize"] = image_size
                if image_config:
                    generation_config["imageConfig"] = image_config
                if generation_config:
                    payload["generationConfig"] = generation_config

            self._log(f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-Gemini-Multi-Image-V2/1.0"
            }

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

            if not response.ok:
                error_msg = result.get("error", {}).get("message", "未知错误")
                error_code = result.get("error", {}).get("code", "unknown")
                self._log(f"API返回错误: {error_msg}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                return (blank_image, False, f"API错误 [{error_code}]: {error_msg}", "", log_output)

            # 处理结果
            self._log("开始处理响应结果")
            images_tensor = []
            image_count = 0
            image_data_found = False

            # 根级data
            if "data" in result and result["data"]:
                try:
                    self._log("在根级找到data字段")
                    image_data = base64.b64decode(result["data"])
                    image_obj = Image.open(io.BytesIO(image_data))
                    if image_obj.mode != "RGB":
                        image_obj = image_obj.convert("RGB")
                    image_np = np.array(image_obj).astype(np.float32) / 255.0
                    images_tensor.append(torch.from_numpy(image_np)[None, ...])
                    image_count += 1
                    image_data_found = True
                    self._log(f"图像 {image_count}: {image_obj.size}, 模式: {image_obj.mode}")
                except Exception as e:
                    self._log(f"处理根级data字段失败: {str(e)}", "ERROR")

            # candidates 结构
            if not image_data_found:
                candidates = result.get("candidates", [])
                if candidates:
                    self._log(f"处理 {len(candidates)} 个候选结果")
                    for idx, candidate in enumerate(candidates):
                        content = candidate.get("content", {})
                        parts_resp = content.get("parts", [])
                        self._log(f"候选结果 {idx} 有 {len(parts_resp)} 个parts")
                        for part_idx, part in enumerate(parts_resp):
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
                                    if image_obj.mode != "RGB":
                                        image_obj = image_obj.convert("RGB")
                                    image_np = np.array(image_obj).astype(np.float32) / 255.0
                                    images_tensor.append(torch.from_numpy(image_np)[None, ...])
                                    image_count += 1
                                    image_data_found = True
                                    self._log(f"图像 {image_count}: {image_obj.size}, 模式: {image_obj.mode}")
                                except Exception as e:
                                    self._log(f"处理图像 {idx}-{part_idx} 时出错: {str(e)}", "ERROR")
                                    continue
                else:
                    self._log("响应中没有candidates字段", "WARN")

            # 递归搜索
            if not image_data_found:
                self._log("递归搜索data字段...")
                found_data_fields = self._find_data_fields(result)
                for field_path, data_value in found_data_fields:
                    try:
                        self._log(f"尝试处理data字段: {field_path}")
                        image_data = base64.b64decode(data_value)
                        image_obj = Image.open(io.BytesIO(image_data))
                        if image_obj.mode != "RGB":
                            image_obj = image_obj.convert("RGB")
                        image_np = np.array(image_obj).astype(np.float32) / 255.0
                        images_tensor.append(torch.from_numpy(image_np)[None, ...])
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
                return (blank_image, False, "没有成功处理的图像，请查看日志获取详细信息", "", log_output)

            result_images = torch.cat(images_tensor, dim=0)
            self._log(f"成功处理 {len(images_tensor)} 张图像")

            # 使用信息
            usage_info = "Gemini 多图高级模式结果:\n"
            usage_info += f"- 模型: {model}\n"
            usage_info += f"- 模式: {mode}\n"
            usage_info += f"- 输入图像数量: {image_count_input}\n"
            usage_info += f"- 输出图像数量: {image_count}\n"
            candidates_count = len(result.get("candidates", []))
            if candidates_count > 0:
                usage_info += f"- 候选结果数: {candidates_count}\n"
            usage_metadata = result.get("usageMetadata", {})
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
            return (blank_image, False, f"请求超时（{timeout}秒）。", "", log_output)
        except requests.exceptions.ConnectionError as e:
            self._log(f"网络连接错误: {str(e)}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = "网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确"
            return (blank_image, False, error_msg, "", log_output)
        except Exception as e:
            self._log(f"未知异常: {str(e)}", "ERROR")
            import traceback
            self._log(f"异常堆栈: {traceback.format_exc()}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            return (blank_image, False, f"图像生成失败: {str(e)}", "", log_output)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "GeminiMultiImageAdvancedV2": GeminiMultiImageAdvancedV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiMultiImageAdvancedV2": "gemini-multi-image-advanced-v2"
}

