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

class WanQingJiMeng40TextToImageNodeV2:
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
                    "default": "星际穿越，黑洞，黑洞里冲出一辆快支离破碎的复古列车，抢视觉冲击力，电影大片，末日既视感，动感，对比色，oc渲染，光线追踪，动态模糊，景深，超现实主义，深蓝，画面通过细腻的丰富的色彩层次塑造主体与场景，质感真实，暗黑风背景的光影效果营造出氛围，整体兼具艺术幻想感，夸张的广角透视效果，耀光，反射，极致的光影，强引力，吞噬",
                    "multiline": True,
                    "tooltip": "图像描述提示词，建议结构：风格关键词 + 主要美学关键词 + 视觉内容 + 视觉上下文 + 补充美学关键词"
                }),
                "size": (["4K", "2K", "1K", "1024x1024", "1024x1536", "1536x1024"], {
                    "default": "2K",
                    "tooltip": "图像尺寸（4K支持超高清输出）"
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
                "image_download_proxy": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "图片下载是否使用代理（线上环境访问外部图片URL可能需要启用）"
                }),
                "image_proxy_url": ("STRING", {
                    "default": "http://http://10.20.254.26:11080",
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
        print("万擎即梦4.0文生图 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        # 创建白色背景图片
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def generate_image(self, environment, api_key, prompt, size, response_format, 
                      sequential_image_generation, stream, watermark, timeout, use_proxy, 
                      image_download_proxy, image_proxy_url, custom_base_url="", custom_endpoint="/llm-serve/v1/images/generations",
                      n=1, seed=-1, negative_prompt="", quality="hd", style="vivid", 
                      guidance_scale=7.5, steps=50):
        """
        万擎即梦4.0文生图 - 支持4K超高清、多图生成、风格控制等高级功能
        
        支持的功能:
        - 4K超高清图像生成
        - 多图像生成 (1-4张)
        - 可重复结果 (种子控制)
        - 负面提示词过滤
        - 质量和风格控制
        - 精细的引导参数调节
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log("开始图像生成任务")
        
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
                self._log("参数验证失败: 图像描述为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "图像描述不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log("参数验证通过")

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
                self._log(f"使用自定义base_url: {base_url}")
            else:
                base_url = self.environments[environment]
                self._log(f"使用环境配置: {environment} -> {base_url}")
            
            # 使用自定义端点路径
            endpoint = custom_endpoint.strip() if custom_endpoint.strip() else "/llm-serve/v1/images/generations"
            endpoint = endpoint.lstrip('/')  # 移除开头的斜杠
            url = f"{base_url}/{endpoint}"
            self._log(f"完整API地址: {url}")
            
            # 构建请求体
            self._log("构建请求体")
            payload = {
                "model": "doubao-seedream-4-0-250828",
                "prompt": prompt.strip(),
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
            
            # 设置请求头
            headers = {
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-JiMeng-4.0-T2I/1.0"
            }
            
            # 记录请求信息
            self._log(f"发送请求到: {url}")
            self._log(f"提示词: {prompt.strip()[:100]}{'...' if len(prompt.strip()) > 100 else ''}")
            self._log(f"尺寸: {size}, 生成数量: {n}")
            
            if seed != -1:
                self._log(f"随机种子: {seed}")
            if negative_prompt and negative_prompt.strip():
                self._log(f"负面提示词: {negative_prompt.strip()[:50]}{'...' if len(negative_prompt.strip()) > 50 else ''}")
            if quality != "hd":
                self._log(f"图像质量: {quality}")
            if style != "vivid":
                self._log(f"图像风格: {style}")
            if guidance_scale != 7.5:
                self._log(f"引导强度: {guidance_scale}")
            if steps != 50:
                self._log(f"推理步数: {steps}")
            
            self._log(f"水印: {'启用' if watermark else '禁用'}, 流式响应: {'启用' if stream else '禁用'}")
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
                self._log(f"JSON解析失败: {str(e)}", "ERROR")
                self._log(f"响应内容: {response.text[:200]}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                response_text = response.text if response.text else "空响应"
                response_text = response_text[:1000] + "..." if len(response_text) > 1000 else response_text
                error_msg = f"无效的JSON响应:\n"
                error_msg += f"- 状态码: {response.status_code}\n"
                error_msg += f"- 响应内容: {response_text}"
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
                    image_size = item.get('size', '未知')
                    
                    image_bytes = base64.b64decode(b64_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB（如果不是的话）
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    self._log(f"图像 {idx + 1}: {image.size}, 模式: {image.mode}, 尺寸: {image_size}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    image_url = item['url']
                    image_size = item.get('size', '未知')
                    self._log(f"收到图像URL: {image_url[:80]}..., 尺寸: {image_size}")
                    
                    try:
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
                        
                        self._log(f"下载图像 {idx + 1}: 实际尺寸{image.size}, 模式: {image.mode}")
                        
                    except Exception as e:
                        self._log(f"下载图像 {idx + 1} 失败: {str(e)}", "ERROR")
                        continue
            
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
            usage_info = f"万擎即梦4.0文生图结果:\n"
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
                
            usage_info += f"- 顺序生成: {sequential_image_generation}\n"
            usage_info += f"- 流式响应: {'是' if stream else '否'}\n"
            usage_info += f"- 水印: {'是' if watermark else '否'}\n"
            
            if usage:
                usage_info += f"- 生成图像统计: {usage.get('generated_images', 0)}\n"
                usage_info += f"- 输出Token: {usage.get('output_tokens', 0)}\n"
                usage_info += f"- 总计Token: {usage.get('total_tokens', usage.get('output_tokens', 0))}"
            
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
    "WanQingJiMeng40TextToImageV2": WanQingJiMeng40TextToImageNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanQingJiMeng40TextToImageV2": "万擎即梦4.0文生图 V2"
}
