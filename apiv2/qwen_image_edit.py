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
                    "tooltip": "是否使用代理服务器（用于API调用）"
                }),
                "image_download_proxy": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "图片下载是否使用代理（线上环境访问外部图片URL可能需要启用）"
                }),
                "image_proxy_url": ("STRING", {
                    "default": "http://10.20.254.26:11080",
                    "tooltip": "图片下载代理服务器地址"
                }),
                "custom_base_url": ("STRING", {
                    "default": "http://llm-gateway.internal",
                    "tooltip": "自定义API基础URL（优先级高于环境选择）"
                }),
                "custom_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/qwen-image/multimodal-generation/generation",
                    "tooltip": "自定义API端点路径"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "success", "message", "response_json", "usage_info")
    FUNCTION = "edit_image"
    CATEGORY = "✨✨✨design-ai/api-v2"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
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
        print("Qwen-Image Edit 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        # 创建白色背景图片
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def edit_image(self, environment, api_key, image, prompt, negative_prompt, 
                   watermark, timeout, use_proxy, image_download_proxy, image_proxy_url="http://http://10.20.254.26:11080", custom_base_url="http://llm-gateway.internal", custom_endpoint="/ai-serve/v1/qwen-image/multimodal-generation/generation"):
        """
        Qwen-Image 图像编辑（异步API）
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log("开始图像编辑任务")
        
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
                self._log("参数验证失败: 编辑指令为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "编辑指令不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            if image is None:
                self._log("参数验证失败: 输入图像为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "输入图像不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log("参数验证通过")

            # 转换图像为base64
            self._log("开始转换图像为base64")
            image_base64 = self._image_to_base64(image)
            self._log(f"图像转换完成, base64长度: {len(image_base64)}")

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
                self._log(f"使用自定义base_url: {base_url}")
            else:
                base_url = self.environments[environment]
                self._log(f"使用环境配置: {environment} -> {base_url}")
            
            # 使用自定义端点路径
            endpoint = custom_endpoint.strip() if custom_endpoint.strip() else "/ai-serve/v1/qwen-image/multimodal-generation/generation"
            endpoint = endpoint.lstrip('/')  # 移除开头的斜杠
            api_url = f"{base_url}/{endpoint}"
            self._log(f"完整API地址: {api_url}")
            
            # 构建请求体 - 新的消息格式
            self._log("构建请求体")
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
            
            self._log(f"编辑指令: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            self._log(f"负面提示词: {negative_prompt[:50] if negative_prompt else '无'}{'...' if negative_prompt and len(negative_prompt) > 50 else ''}")
            self._log(f"水印设置: {'启用' if watermark else '禁用'}")
            self._log(f"超时设置: {timeout}秒")
            
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
            
            # 发送同步请求
            self._log("发送API请求...")
            response = requests.post(api_url, **request_kwargs)
            
            self._log(f"收到响应, 状态码: {response.status_code}")
            
            # 解析响应
            self._log("解析响应JSON")
            try:
                result = response.json()
                self._log("响应JSON解析成功")
            except json.JSONDecodeError as e:
                self._log(f"JSON解析失败: {str(e)}", "ERROR")
                self._log(f"响应内容: {response.text[:200]}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = f"无效的JSON响应: {response.text}"
                return (blank_image, False, error_msg, "", log_output)
            
            # 检查响应状态
            if not response.ok:
                error_msg = result.get('error', {}).get('message', response.text)
                self._log(f"API返回错误: {error_msg}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                final_error_msg = f"请求失败 [{response.status_code}]: {error_msg}"
                return (blank_image, False, final_error_msg, "", log_output)
            
            # 处理结果
            self._log("开始处理API响应结果")
            result_images, response_json, api_usage_info = self._process_result(result, image_download_proxy, image_proxy_url)
            
            # 记录API使用信息
            self._log(f"API使用信息: {api_usage_info.replace(chr(10), ' | ')}")
            self._log("图像编辑任务完成", "SUCCESS")
            
            # 打印并获取执行日志
            log_output = self._print_and_format_logs()
            
            # 构建成功消息
            success_message = "图像编辑成功"
            
            return (result_images, True, success_message, response_json, log_output)
            
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
        except requests.exceptions.RequestException as e:
            self._log(f"请求异常: {str(e)}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"请求失败: {str(e)}"
            return (blank_image, False, error_msg, "", log_output)
        except Exception as e:
            self._log(f"未知异常: {str(e)}", "ERROR")
            import traceback
            self._log(f"异常堆栈: {traceback.format_exc()}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"图像编辑失败: {str(e)}"
            return (blank_image, False, error_msg, "", log_output)

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
            
            self._log(f"图像尺寸: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
            
        except Exception as e:
            self._log(f"图像转换异常: {str(e)}", "ERROR")
            raise ValueError(f"图像转换失败: {str(e)}")

    def _process_result(self, result, image_download_proxy, image_proxy_url):
        """处理编辑结果"""
        try:
            # 提取结果数据 - 新的choices格式
            choices = result.get("output", {}).get("choices", [])
            if not choices:
                self._log("响应中没有choices数据", "ERROR")
                raise ValueError("响应中没有choices数据")
            
            images_tensor = []
            image_urls = []
            
            self._log(f"发现 {len(choices)} 个结果选项")
            
            for idx, choice in enumerate(choices):
                message = choice.get("message", {})
                content = message.get("content", [])
                
                for content_item in content:
                    if "image" in content_item:
                        image_url = content_item["image"]
                        if not image_url:
                            self._log(f"选项 {idx + 1} 没有图像URL", "WARN")
                            continue
                        
                        image_urls.append(image_url)
                        
                        # 下载图像
                        try:
                            self._log(f"开始下载图像 {idx + 1}/{len(choices)}")
                            
                            # 配置图片下载代理设置
                            download_kwargs = {"timeout": 60}
                            if image_download_proxy:
                                # 使用指定的代理服务器
                                self._log(f"图片下载代理: 使用 {image_proxy_url}")
                                download_kwargs["proxies"] = {
                                    "http": image_proxy_url,
                                    "https": image_proxy_url
                                }
                            else:
                                # 禁用代理（用于内部网络或直连）
                                self._log("图片下载代理: 禁用")
                                download_kwargs["proxies"] = {"http": None, "https": None}
                            
                            self._log(f"图片URL前缀: {image_url[:80]}...")
                            img_response = requests.get(image_url, **download_kwargs)
                            self._log(f"图片下载响应状态码: {img_response.status_code}")
                            
                            if img_response.status_code == 200:
                                image = Image.open(io.BytesIO(img_response.content))
                                
                                # 转换为RGB（如果不是的话）
                                if image.mode != 'RGB':
                                    self._log(f"图像模式转换: {image.mode} -> RGB")
                                    image = image.convert('RGB')
                                
                                # 转换为tensor
                                image_np = np.array(image).astype(np.float32) / 255.0
                                image_tensor = torch.from_numpy(image_np)[None,]
                                images_tensor.append(image_tensor)
                                
                                self._log(f"图像 {idx + 1} 下载成功: {image.size}, 模式: {image.mode}")
                            else:
                                self._log(f"图像 {idx + 1} 下载失败 - 状态码: {img_response.status_code}", "ERROR")
                                self._log(f"失败响应: {img_response.text[:150]}", "ERROR")
                                
                        except Exception as e:
                            self._log(f"下载图像 {idx + 1} 异常: {type(e).__name__} - {str(e)}", "ERROR")
            
            if not images_tensor:
                self._log("没有成功下载的图像", "ERROR")
                raise ValueError("没有成功下载的图像")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            self._log(f"成功处理 {len(images_tensor)} 张图像")
            
            # 格式化使用信息
            usage = result.get('usage', {})
            usage_info = f"API使用统计:\n"
            usage_info += f"- 图像宽度: {usage.get('width', 'N/A')}\n"
            usage_info += f"- 图像高度: {usage.get('height', 'N/A')}\n"
            usage_info += f"- 图像数量: {usage.get('image_count', len(images_tensor))}\n"
            usage_info += f"- 成功下载: {len(images_tensor)}\n"
            usage_info += f"- 请求ID: {result.get('request_id', 'N/A')}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            return (result_images, response_json, usage_info)
            
        except Exception as e:
            self._log(f"结果处理失败: {str(e)}", "ERROR")
            raise ValueError(f"结果处理失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenImageEdit": QwenImageEditNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEdit": "Qwen-Image 图像编辑"
}
