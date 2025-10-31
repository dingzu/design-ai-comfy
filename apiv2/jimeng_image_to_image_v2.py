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

class JiMengImageToImageNodeV2:
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
                }),
                "use_proxy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否使用代理服务器"
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
                    "default": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seededit_i2i.jpeg",
                    "tooltip": "图像URL（当未提供输入图像时使用）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "success", "message", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api-v2"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging.corp.kuaishou.com",
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
        print("即梦图生图 V2 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

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
                      seed, guidance_scale, watermark, timeout, use_proxy, 
                      image_download_proxy, image_proxy_url, 
                      custom_base_url="", custom_endpoint="/llm-serve/v1/images/generations", 
                      image=None, image_url=None):
        """
        即梦图生图 V2
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log("开始即梦图生图任务")
        
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
                self._log("参数验证失败: 图像编辑描述为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "图像编辑描述不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log("参数验证通过")

            # 处理输入图像
            self._log("开始处理输入图像")
            image_input = None
            if image is not None:
                # 使用提供的图像tensor
                image_input = self.tensor_to_base64(image)
                self._log(f"使用输入图像tensor，尺寸: {image.shape}")
                self._log(f"图像格式: data URI (长度: {len(image_input)} 字符)")
            elif image_url and image_url.strip():
                # 使用图像URL
                image_input = image_url.strip()
                self._log(f"使用图像URL: {image_input}")
                # 验证URL格式
                if not (image_input.startswith('http://') or image_input.startswith('https://') or image_input.startswith('data:')):
                    self._log("警告: URL格式可能不正确，应以http://、https://或data:开头", "WARN")
            else:
                self._log("参数验证失败: 未提供输入图像", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "必须提供输入图像或图像URL"
                return (blank_image, False, error_msg, "", log_output)

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
                self._log(f"使用自定义base_url: {base_url}")
            else:
                base_url = self.environments[environment]
                self._log(f"使用环境配置: {environment} -> {base_url}")
            
            # 使用自定义端点路径
            endpoint = custom_endpoint.strip() if custom_endpoint.strip() else "/llm-serve/v1/images/generations"
            endpoint = endpoint.lstrip('/')
            url = f"{base_url}/{endpoint}"
            self._log(f"完整API地址: {url}")
            
            # 构建请求体
            self._log("构建请求体")
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
            
            self._log(f"模型: doubao-seededit-3-0-i2i-250628")
            self._log(f"提示词: {prompt.strip()[:100]}{'...' if len(prompt.strip()) > 100 else ''}")
            self._log(f"输入图像: {'Tensor格式' if image is not None else 'URL格式'}")
            self._log(f"响应格式: {response_format}")
            self._log(f"图像尺寸: {size}")
            self._log(f"随机种子: {seed}")
            self._log(f"引导强度: {guidance_scale}")
            self._log(f"水印: {'启用' if watermark else '禁用'}")
            self._log(f"超时设置: {timeout}秒")
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-JiMeng-I2I-V2/1.0"
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
            response = requests.post(url, **request_kwargs)
            
            self._log(f"收到响应, 状态码: {response.status_code}")
            
            # 解析响应
            self._log("解析响应JSON")
            try:
                response_data = response.json()
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
                error_msg = response_data.get('error', {}).get('message', '未知错误')
                error_type = response_data.get('error', {}).get('type', 'unknown_error')
                error_code = response_data.get('error', {}).get('code', 'unknown')
                
                self._log(f"API返回错误: {error_msg}", "ERROR")
                
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
                
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                full_error_msg = f"API错误 [{error_code}]: {error_msg}"
                return (blank_image, False, full_error_msg, "", log_output)
            
            # 处理生成的图像
            self._log("开始处理生成的图像")
            images_tensor = []
            image_data = response_data.get('data', [])
            
            if not image_data:
                self._log("响应中没有图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "响应中没有图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log(f"收到 {len(image_data)} 个图像数据")
            
            for idx, item in enumerate(image_data):
                if 'b64_json' in item:
                    # 处理 base64 编码的图像
                    b64_data = item['b64_json']
                    image_bytes = base64.b64decode(b64_data)
                    result_image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB
                    if result_image.mode != 'RGB':
                        result_image = result_image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(result_image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    self._log(f"图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    image_url_result = item['url']
                    self._log(f"收到图像URL: {image_url_result[:80]}...")
                    
                    if response_format == "url":
                        # 如果用户选择了URL格式，下载图像
                        try:
                            self._log(f"下载图像 {idx + 1}")
                            
                            # 配置图片下载代理设置
                            download_kwargs = {"timeout": 30}
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
                            
                            self._log(f"图像 {idx + 1} 下载成功: {result_image.size}, 模式: {result_image.mode}")
                            
                        except Exception as e:
                            self._log(f"下载图像 {idx + 1} 失败: {str(e)}", "ERROR")
                            continue
                    else:
                        self._log("警告: 跳过URL形式的图像，当前仅支持base64格式", "WARN")
            
            if not images_tensor:
                self._log("没有可用的图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "没有可用的图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            self._log(f"成功处理 {len(images_tensor)} 张图像")
            
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
            
            # 记录API使用信息
            self._log(f"API使用信息: {usage_info.replace(chr(10), ' | ')}")
            self._log("图像生成任务完成", "SUCCESS")
            
            # 打印并获取执行日志
            log_output = self._print_and_format_logs()
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            # 构建成功消息
            success_message = "图像生成成功"
            
            return (result_images, True, success_message, response_json, log_output)
            
        except requests.exceptions.Timeout:
            self._log(f"请求超时（{timeout}秒）", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"请求超时（{timeout}秒）。图像生成可能需要较长时间，建议增加超时时间。"
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
            error_msg = f"图像生成失败: {str(e)}"
            return (blank_image, False, error_msg, "", log_output)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "JiMengImageToImageV2": JiMengImageToImageNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JiMengImageToImageV2": "即梦图生图 V2"
}

