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

class QwenImageText2ImgNodeV2:
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
                "prompt": ("STRING", {
                    "default": "生成一个美丽的风景画",
                    "multiline": True,
                    "tooltip": "图像描述提示词"
                }),
                "image_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量"
                }),
                "image_size": (["1328*1328", "1664*928", "1472*1140", "1140*1472", "928*1664"], {
                    "default": "1328*1328",
                    "tooltip": "图像尺寸 (支持的固定尺寸)"
                }),
                "prompt_extend": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否开启提示词扩展"
                }),
                "watermark": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否添加水印"
                }),
                "timeout": ("FLOAT", {
                    "default": 180.0,
                    "min": 60.0,
                    "max": 600.0,
                    "step": 30.0,
                    "tooltip": "请求超时时间（秒）"
                }),
                "poll_interval": ("FLOAT", {
                    "default": 5.0,
                    "min": 2.0,
                    "max": 30.0,
                    "step": 1.0,
                    "tooltip": "任务状态查询间隔（秒）"
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
                    "default": "",
                    "tooltip": "自定义API基础URL（优先级高于环境选择）"
                }),
                "custom_submit_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/qwen-image/text2image/image-synthesis",
                    "tooltip": "自定义任务提交端点路径"
                }),
                "custom_query_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/qwen-image-tasks/{task_id}",
                    "tooltip": "自定义任务查询端点路径（支持{task_id}占位符）"
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
        print("Qwen-Image 文本生成图像 V2 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def generate_image(self, environment, api_key, prompt, image_count, 
                      image_size, prompt_extend, watermark, timeout, poll_interval, 
                      use_proxy, image_download_proxy, image_proxy_url, 
                      custom_base_url="", custom_submit_endpoint="/ai-serve/v1/qwen-image/text2image/image-synthesis", 
                      custom_query_endpoint="/ai-serve/v1/qwen-image-tasks/{task_id}"):
        """
        Qwen-Image 文本生成图像（异步API）V2
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log("开始Qwen-Image图像生成任务")
        
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
            
            # 使用自定义提交端点路径
            submit_endpoint = custom_submit_endpoint.strip() if custom_submit_endpoint.strip() else "/ai-serve/v1/qwen-image/text2image/image-synthesis"
            submit_endpoint = submit_endpoint.lstrip('/')
            submit_url = f"{base_url}/{submit_endpoint}"
            self._log(f"提交API地址: {submit_url}")
            
            # 构建请求体
            self._log("构建请求体")
            payload = {
                "model": "qwen-image",
                "input": {
                    "prompt": prompt.strip()
                },
                "parameters": {
                    "size": image_size,
                    "n": image_count,
                    "prompt_extend": prompt_extend,
                    "watermark": watermark
                }
            }
            
            self._log(f"提示词: {prompt.strip()[:100]}{'...' if len(prompt.strip()) > 100 else ''}")
            self._log(f"模型: qwen-image")
            self._log(f"图像尺寸: {image_size}")
            self._log(f"生成数量: {image_count}")
            self._log(f"提示词扩展: {'启用' if prompt_extend else '禁用'}")
            self._log(f"水印: {'启用' if watermark else '禁用'}")
            self._log(f"超时设置: {timeout}秒")
            self._log(f"轮询间隔: {poll_interval}秒")
            
            # 设置请求头
            headers = {
                "X-DashScope-Async": "enable",
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-QwenImage-Text2Img-V2/1.0"
            }
            
            # 配置代理
            submit_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": 30
            }
            if use_proxy:
                submit_kwargs["proxies"] = {"http": None, "https": None}
                self._log("API请求代理: 禁用系统代理")
            else:
                self._log("API请求代理: 使用系统代理")
            
            # 1. 提交任务
            self._log("发送任务提交请求...")
            response = requests.post(submit_url, **submit_kwargs)
            
            self._log(f"任务提交响应状态码: {response.status_code}")
            
            # 解析提交响应
            try:
                submit_result = response.json()
                self._log("提交响应JSON解析成功")
            except json.JSONDecodeError as e:
                self._log(f"JSON解析失败: {str(e)}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = f"无效的JSON响应: {response.text}"
                return (blank_image, False, error_msg, "", log_output)
            
            # 检查提交状态
            if not response.ok:
                error_msg = submit_result.get('error', {}).get('message', response.text)
                self._log(f"任务提交失败: {error_msg}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                full_error_msg = f"任务提交失败 [{response.status_code}]: {error_msg}"
                return (blank_image, False, full_error_msg, "", log_output)
            
            # 获取任务ID
            task_id = submit_result.get("output", {}).get("task_id")
            if not task_id:
                self._log("未获取到任务ID", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "未获取到任务ID"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log(f"任务提交成功，任务ID: {task_id}")
            
            # 2. 轮询任务状态
            result = self._poll_task_status(base_url, api_key, task_id, timeout, poll_interval, use_proxy, custom_query_endpoint)
            
            if not result:
                self._log("任务执行失败或超时", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "任务执行失败或超时"
                return (blank_image, False, error_msg, "", log_output)
            
            # 3. 处理结果
            return self._process_result(result, task_id, image_download_proxy, image_proxy_url)
            
        except requests.exceptions.Timeout:
            self._log(f"请求超时（{timeout}秒）", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"请求超时（{timeout}秒）。Qwen-Image生成可能需要较长时间，建议增加超时时间。"
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

    def _poll_task_status(self, base_url, api_key, task_id, timeout, poll_interval, use_proxy, custom_query_endpoint="/ai-serve/v1/qwen-image-tasks/{task_id}"):
        """轮询任务状态"""
        # 使用自定义查询端点路径
        query_endpoint = custom_query_endpoint.strip() if custom_query_endpoint.strip() else "/ai-serve/v1/qwen-image-tasks/{task_id}"
        query_endpoint = query_endpoint.lstrip('/').format(task_id=task_id)
        query_url = f"{base_url}/{query_endpoint}"
        
        self._log(f"查询API地址: {query_url}")
        
        headers = {"x-api-key": api_key}
        
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)
        
        self._log(f"开始轮询任务状态，最大尝试次数: {max_attempts}")
        
        for attempt in range(max_attempts):
            try:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    self._log(f"任务查询超时（{elapsed:.1f}s）", "ERROR")
                    break
                
                # 配置代理
                poll_kwargs = {
                    "headers": headers,
                    "timeout": 30
                }
                if use_proxy:
                    poll_kwargs["proxies"] = {"http": None, "https": None}
                
                response = requests.get(query_url, **poll_kwargs)
                
                if response.status_code != 200:
                    self._log(f"查询失败 {response.status_code}: {response.text}", "WARN")
                    time.sleep(poll_interval)
                    continue
                
                result = response.json()
                task_status = result.get("output", {}).get("task_status")
                
                self._log(f"查询尝试 {attempt + 1}/{max_attempts}, 状态: {task_status}, 耗时: {elapsed:.1f}s")
                
                if task_status == "SUCCEEDED":
                    self._log("任务成功完成！", "SUCCESS")
                    return result
                
                elif task_status == "FAILED":
                    error_msg = result.get("output", {}).get("message", "任务失败")
                    self._log(f"任务执行失败: {error_msg}", "ERROR")
                    raise ValueError(f"任务执行失败: {error_msg}")
                
                elif task_status in ["PENDING", "RUNNING"]:
                    time.sleep(poll_interval)
                
                else:
                    self._log(f"未知任务状态: {task_status}", "WARN")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                self._log(f"查询异常: {str(e)}", "WARN")
                time.sleep(poll_interval)
        
        return None

    def _process_result(self, result, task_id, image_download_proxy, image_proxy_url):
        """处理生成结果"""
        try:
            self._log("开始处理生成结果")
            
            # 提取结果数据
            results = result.get("output", {}).get("results", [])
            if not results:
                self._log("响应中没有图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "响应中没有图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            images_tensor = []
            image_urls = []
            
            self._log(f"处理 {len(results)} 个结果")
            
            for idx, item in enumerate(results):
                image_url = item.get("url")
                if not image_url:
                    self._log(f"结果 {idx + 1} 没有图像URL", "WARN")
                    continue
                
                image_urls.append(image_url)
                
                # 下载图像
                try:
                    self._log(f"下载图像 {idx + 1}: {image_url[:80]}...")
                    
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
                    
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        
                        # 转换为RGB
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # 转换为tensor
                        image_np = np.array(image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        
                        self._log(f"图像 {idx + 1} 下载成功: {image.size}, 模式: {image.mode}")
                    else:
                        self._log(f"图像下载失败 - 状态码: {img_response.status_code}", "ERROR")
                        
                except Exception as e:
                    self._log(f"下载图像 {idx + 1} 异常: {str(e)}", "ERROR")
            
            if not images_tensor:
                self._log("没有成功下载的图像", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "没有成功下载的图像"
                return (blank_image, False, error_msg, "", log_output)
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            self._log(f"成功处理 {len(images_tensor)} 张图像")
            
            # 格式化任务信息和使用信息
            output = result.get("output", {})
            usage = output.get('usage', {})
            
            combined_info = f"任务信息:\n"
            combined_info += f"- 任务ID: {task_id}\n"
            combined_info += f"- 提交时间: {output.get('submit_time', 'N/A')}\n"
            combined_info += f"- 完成时间: {output.get('end_time', 'N/A')}\n"
            combined_info += f"- 生成图像数量: {usage.get('image_count', len(images_tensor))}\n"
            combined_info += f"- 成功下载: {len(images_tensor)}\n"
            combined_info += f"- 图像URLs: {len(image_urls)}"
            
            # 添加提示词信息
            if results:
                first_result = results[0]
                if 'orig_prompt' in first_result:
                    combined_info += f"\n- 原始提示词: {first_result['orig_prompt'][:100]}..."
                if 'actual_prompt' in first_result:
                    combined_info += f"\n- 扩展提示词: {first_result['actual_prompt'][:100]}..."
            
            # 记录使用信息
            self._log(f"使用统计: {combined_info.replace(chr(10), ' | ')}")
            self._log("图像生成任务完成", "SUCCESS")
            
            # 打印并获取执行日志
            log_output = self._print_and_format_logs()
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            # 构建成功消息
            success_message = f"图像生成成功，任务ID: {task_id}"
            
            return (result_images, True, success_message, response_json, log_output)
            
        except Exception as e:
            self._log(f"结果处理失败: {str(e)}", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"结果处理失败: {str(e)}"
            return (blank_image, False, error_msg, "", log_output)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenImageText2ImgV2": QwenImageText2ImgNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageText2ImgV2": "Qwen-Image 文本生成图像 V2"
}

