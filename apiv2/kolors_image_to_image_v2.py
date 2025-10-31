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

class KolorsImageToImageNodeV2:
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
                "model_name": (["kling-v2"], {
                    "default": "kling-v2",
                    "tooltip": "可图模型名称"
                }),
                "timeout": ("FLOAT", {
                    "default": 300.0,
                    "min": 60.0,
                    "max": 600.0,
                    "step": 10.0,
                    "tooltip": "总超时时间（秒）"
                }),
                "poll_interval": ("FLOAT", {
                    "default": 5.0,
                    "min": 1.0,
                    "max": 30.0,
                    "step": 1.0,
                    "tooltip": "轮询间隔（秒）"
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
                "custom_submit_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/ktu/images/generations",
                    "tooltip": "自定义任务提交端点路径"
                }),
                "custom_query_endpoint": ("STRING", {
                    "default": "/ai-serve/v1/ktu/images/generations/{task_id}",
                    "tooltip": "自定义任务查询端点路径（支持{task_id}占位符）"
                })
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "输入图像（可选，如果不提供则使用图像URL）"
                }),
                "image_url": ("STRING", {
                    "default": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seededit_i2i.jpeg",
                    "tooltip": "图像URL（当未提供输入图像时使用）"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "url",
                    "tooltip": "响应格式：url或b64_json"
                }),
                "size": ("STRING", {
                    "default": "adaptive",
                    "tooltip": "图像尺寸，如1024x1024或adaptive"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 4294967295,
                    "tooltip": "随机种子，-1为随机"
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 7.5,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.5,
                    "tooltip": "引导强度，控制生成图像与提示词的匹配程度"
                }),
                "steps": ("INT", {
                    "default": 20,
                    "min": 10,
                    "max": 100,
                    "tooltip": "推理步数"
                }),
                "strength": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "图像变化强度，0.1为轻微变化，1.0为完全重新生成"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词，描述不希望出现的内容"
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
        print("可图图生图 V2 执行日志:")
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
        
        # 返回纯base64字符串（与扩图API保持一致）
        base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64_string

    def submit_task(self, environment, api_key, payload, use_proxy, custom_base_url="", custom_submit_endpoint="/ai-serve/v1/ktu/images/generations"):
        """提交生成任务"""
        # 构建URL - 优先使用用户自定义的base_url
        if custom_base_url and custom_base_url.strip():
            base_url = custom_base_url.strip().rstrip('/')
            self._log(f"使用自定义base_url: {base_url}")
        else:
            base_url = self.environments[environment]
            self._log(f"使用环境配置: {environment} -> {base_url}")
        
        # 使用自定义提交端点路径
        endpoint = custom_submit_endpoint.strip() if custom_submit_endpoint.strip() else "/ai-serve/v1/ktu/images/generations"
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}"
        self._log(f"完整API地址: {url}")
        
        headers = {
            "x-api-key": api_key.strip(),
            "Content-Type": "application/json",
            "User-Agent": "ComfyUI-Kolors-I2I-V2/1.0"
        }
        
        self._log(f"提交任务到: {url}")
        
        # 配置代理
        request_kwargs = {
            "headers": headers,
            "json": payload,
            "timeout": 30
        }
        if use_proxy:
            request_kwargs["proxies"] = {"http": None, "https": None}
            self._log("API请求代理: 禁用系统代理")
        else:
            self._log("API请求代理: 使用系统代理")
        
        response = requests.post(url, **request_kwargs)
        
        self._log(f"响应状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            self._log("响应JSON解析成功")
        except json.JSONDecodeError:
            response_text = response.text if response.text else "空响应"
            self._log(f"JSON解析失败: {response_text[:200]}", "ERROR")
            raise ValueError(f"无效的JSON响应 (状态码: {response.status_code}): {response_text}")
        
        if not response.ok:
            error_msg = response_data.get('message', '未知错误')
            self._log(f"任务提交失败: {error_msg}", "ERROR")
            raise ValueError(f"任务提交失败 (状态码: {response.status_code}): {error_msg}")
        
        if response_data.get('code') != 0:
            error_msg = response_data.get('message', '未知错误')
            self._log(f"任务提交失败: {error_msg}", "ERROR")
            raise ValueError(f"任务提交失败: {error_msg}")
        
        return response_data.get('data', {})

    def poll_task_result(self, environment, api_key, task_id, timeout, poll_interval, use_proxy, custom_base_url="", custom_query_endpoint="/ai-serve/v1/ktu/images/generations/{task_id}"):
        """轮询任务结果"""
        # 构建URL - 优先使用用户自定义的base_url
        if custom_base_url and custom_base_url.strip():
            base_url = custom_base_url.strip().rstrip('/')
        else:
            base_url = self.environments[environment]
        
        # 使用自定义查询端点路径
        endpoint = custom_query_endpoint.strip() if custom_query_endpoint.strip() else "/ai-serve/v1/ktu/images/generations/{task_id}"
        endpoint = endpoint.lstrip('/').format(task_id=task_id)
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "x-api-key": api_key.strip(),
            "User-Agent": "ComfyUI-Kolors-I2I-V2/1.0"
        }
        
        self._log(f"轮询URL: {url}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self._log(f"轮询任务状态: {task_id}")
            
            try:
                # 配置代理
                poll_kwargs = {
                    "headers": headers,
                    "timeout": 30
                }
                if use_proxy:
                    poll_kwargs["proxies"] = {"http": None, "https": None}
                
                response = requests.get(url, **poll_kwargs)
                response_data = response.json()
                
                if not response.ok:
                    error_msg = response_data.get('message', '未知错误')
                    self._log(f"获取任务状态失败: {error_msg}", "ERROR")
                    raise ValueError(f"获取任务状态失败 (状态码: {response.status_code}): {error_msg}")
                
                if response_data.get('code') != 0:
                    error_msg = response_data.get('message', '未知错误')
                    self._log(f"获取任务状态失败: {error_msg}", "ERROR")
                    raise ValueError(f"获取任务状态失败: {error_msg}")
                
                data = response_data.get('data', {})
                task_status = data.get('task_status', '')
                
                self._log(f"任务状态: {task_status}")
                
                if task_status == 'succeed':
                    self._log("任务成功完成", "SUCCESS")
                    return response_data
                elif task_status == 'failed':
                    error_msg = data.get('fail_reason', '任务执行失败')
                    self._log(f"任务执行失败: {error_msg}", "ERROR")
                    raise ValueError(f"任务执行失败: {error_msg}")
                elif task_status in ['submitted', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    self._log(f"未知任务状态: {task_status}", "WARN")
                    time.sleep(poll_interval)
                    continue
                    
            except requests.exceptions.RequestException as e:
                self._log(f"轮询请求失败: {str(e)}", "ERROR")
                time.sleep(poll_interval)
                continue
        
        self._log(f"任务超时（{timeout}秒）", "ERROR")
        raise ValueError(f"任务超时（{timeout}秒），请稍后重试或增加超时时间")

    def generate_image(self, environment, api_key, prompt, model_name, timeout, poll_interval, use_proxy, 
                      image_download_proxy, image_proxy_url, custom_base_url="", 
                      custom_submit_endpoint="/ai-serve/v1/ktu/images/generations", 
                      custom_query_endpoint="/ai-serve/v1/ktu/images/generations/{task_id}",
                      image=None, image_url=None, response_format="url", size="adaptive", 
                      seed=-1, guidance_scale=7.5, steps=20, strength=0.8, negative_prompt=""):
        """
        可图图生图 V2
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
                self._log("参数验证失败: 提示词为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "提示词不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log("参数验证通过")

            # 处理输入图像
            self._log("开始处理输入图像")
            image_input = None
            if image is not None:
                # 使用提供的图像tensor
                image_input = self.tensor_to_base64(image)
                self._log(f"使用输入图像tensor，尺寸: {image.shape}")
                self._log(f"Base64长度: {len(image_input)}")
            elif image_url and image_url.strip():
                # 使用图像URL
                image_input = image_url.strip()
                self._log(f"使用图像URL: {image_input}")
            else:
                self._log("参数验证失败: 未提供输入图像", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "必须提供输入图像或图像URL"
                return (blank_image, False, error_msg, "", log_output)

            # 构建请求体
            self._log("构建请求体")
            payload = {
                "model_name": model_name,
                "prompt": prompt.strip(),
                "image": image_input,
                "response_format": response_format,
                "size": size
            }
            
            # 添加可选参数
            if seed != -1:
                payload["seed"] = seed
                self._log(f"随机种子: {seed}")
                
            if guidance_scale != 7.5:
                payload["guidance_scale"] = guidance_scale
                self._log(f"引导强度: {guidance_scale}")
                
            if steps != 20:
                payload["steps"] = steps
                self._log(f"推理步数: {steps}")
                
            if strength != 0.8:
                payload["strength"] = strength
                self._log(f"变化强度: {strength}")
                
            if negative_prompt and negative_prompt.strip():
                payload["negative_prompt"] = negative_prompt.strip()
                self._log(f"负面提示词: {negative_prompt.strip()[:50]}{'...' if len(negative_prompt.strip()) > 50 else ''}")
            
            # 检查请求体大小
            payload_str = json.dumps(payload, ensure_ascii=False)
            payload_size_mb = len(payload_str.encode('utf-8')) / (1024 * 1024)
            self._log(f"请求体大小: {payload_size_mb:.2f}MB")
            
            if payload_size_mb > 10:
                self._log("警告: 请求体过大，可能导致API失败", "WARN")
            
            self._log(f"提示词: {prompt.strip()[:100]}{'...' if len(prompt.strip()) > 100 else ''}")
            self._log(f"输入图像: {'Tensor格式' if image is not None else 'URL格式'}")
            self._log(f"尺寸: {size}")
            self._log(f"超时设置: {timeout}秒, 轮询间隔: {poll_interval}秒")
            
            # 提交任务
            task_data = self.submit_task(environment, api_key, payload, use_proxy, custom_base_url, custom_submit_endpoint)
            task_id = task_data.get('task_id')
            
            if not task_id:
                self._log("任务提交成功但未获取到task_id", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "任务提交成功但未获取到task_id"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log(f"任务已提交，task_id: {task_id}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 轮询任务结果
            result_data = self.poll_task_result(environment, api_key, task_id, timeout, poll_interval, use_proxy, custom_base_url, custom_query_endpoint)
            
            # 计算总耗时
            total_time = time.time() - start_time
            self._log(f"总耗时: {total_time:.1f}秒")
            
            # 处理生成的图像
            data = result_data.get('data', {})
            self._log("开始处理生成的图像")
            
            # 根据实际API响应结构提取图像
            task_result = data.get('task_result', {})
            images_data = task_result.get('images', [])
            
            # 提取图像URL列表
            image_urls = []
            if images_data:
                for img in images_data:
                    if isinstance(img, dict) and 'url' in img:
                        image_urls.append(img['url'])
                    elif isinstance(img, str):
                        image_urls.append(img)
            
            # 如果新格式没有找到，尝试旧格式兼容
            if not image_urls:
                image_urls = data.get('image_urls', [])
                if image_urls:
                    self._log("使用旧格式image_urls")
            
            self._log(f"提取到 {len(image_urls)} 个图像URL")
            
            if not image_urls:
                self._log("未找到图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "任务完成但没有生成图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            images_tensor = []
            for idx, image_url_result in enumerate(image_urls):
                self._log(f"下载图像 {idx + 1}: {image_url_result[:80]}...")
                
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
                    
                    self._log(f"图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
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
            usage_info = f"可图图生图结果:\n"
            usage_info += f"- 模型: {model_name}\n"
            usage_info += f"- 任务ID: {task_id}\n"
            usage_info += f"- 提示词: {prompt.strip()}\n"
            if negative_prompt and negative_prompt.strip():
                usage_info += f"- 负面提示词: {negative_prompt.strip()}\n"
            usage_info += f"- 输入图像: {'Tensor' if image is not None else 'URL'}\n"
            usage_info += f"- 响应格式: {response_format}\n"
            usage_info += f"- 图像尺寸: {size}\n"
            if seed != -1:
                usage_info += f"- 随机种子: {seed}\n"
            if guidance_scale != 7.5:
                usage_info += f"- 引导强度: {guidance_scale}\n"
            if steps != 20:
                usage_info += f"- 推理步数: {steps}\n"
            if strength != 0.8:
                usage_info += f"- 变化强度: {strength}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            usage_info += f"- 总耗时: {total_time:.1f}秒"
            
            # 记录API使用信息
            self._log(f"API使用信息: {usage_info.replace(chr(10), ' | ')}")
            self._log("图像编辑任务完成", "SUCCESS")
            
            # 打印并获取执行日志
            log_output = self._print_and_format_logs()
            
            # 返回完整的响应JSON
            response_json = json.dumps(result_data, ensure_ascii=False, indent=2)
            
            # 构建成功消息
            success_message = "图像编辑成功"
            
            return (result_images, True, success_message, response_json, log_output)
            
        except requests.exceptions.Timeout:
            self._log(f"请求超时（{timeout}秒）", "ERROR")
            log_output = self._print_and_format_logs()
            blank_image = self._create_blank_image()
            error_msg = f"请求超时。图像编辑可能需要较长时间，建议增加超时时间。"
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

# 节点映射
NODE_CLASS_MAPPINGS = {
    "KolorsImageToImageV2": KolorsImageToImageNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KolorsImageToImageV2": "可图图生图 V2"
}

