import torch
import numpy as np
import requests
import time
import json
import base64
import io
import os
from PIL import Image
from urllib.parse import urlparse
import jwt
from typing import List, Dict, Any, Optional, Tuple
import folder_paths

class KetuTextToImageNodeV2:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "access_key": ("STRING", {
                    "default": "",
                    "tooltip": "可图API Access Key"
                }),
                "secret_key": ("STRING", {
                    "default": "",
                    "tooltip": "可图API Secret Key"
                }),
                "prompt": ("STRING", {
                    "default": "一个美丽的风景画，高质量，8K分辨率",
                    "multiline": True,
                    "tooltip": "文本提示词，不能超过2500个字符"
                }),
                "model_name": (["kling-v1", "kling-v1-5", "kling-v2", "kling-v2-new", "kling-v2-1"], {
                    "default": "kling-v1",
                    "tooltip": "选择可图模型"
                }),
                "aspect_ratio": (["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9"], {
                    "default": "16:9",
                    "tooltip": "图像宽高比"
                }),
                "wait_for_result": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否等待图像生成完成"
                }),
                "timeout": ("INT", {
                    "default": 300,
                    "min": 60,
                    "max": 600,
                    "step": 10,
                    "tooltip": "总超时时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 30,
                    "step": 1,
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
                })
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词，不能超过2500个字符"
                }),
                "image": ("IMAGE", {
                    "tooltip": "参考图像（可选，用于图像参考功能）"
                }),
                "image_url": ("STRING", {
                    "default": "",
                    "tooltip": "参考图像URL（当没有提供图像tensor时使用）"
                }),
                "image_reference": (["", "subject", "face"], {
                    "default": "",
                    "tooltip": "图像参考类型：subject（角色特征）、face（人物长相，仅kling-v1-5支持）"
                }),
                "image_fidelity": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "图像参考强度"
                }),
                "human_fidelity": ("FLOAT", {
                    "default": 0.45,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "面部参考强度，仅image_reference为subject时生效"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "success", "message", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api-v2"

    def __init__(self):
        self.api_url = "https://api-beijing.klingai.com/v1/images/generations"
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
        print("可图文生图 V2 执行日志:")
        print("="*80)
        print(log_output)
        print("="*80 + "\n")
        return log_output

    def _create_blank_image(self, width=512, height=512):
        """创建空白图片tensor"""
        blank_array = np.ones((1, height, width, 3), dtype=np.float32)
        return torch.from_numpy(blank_array)

    def encode_jwt_token(self, access_key, secret_key):
        """生成JWT token"""
        try:
            headers = {
                "alg": "HS256",
                "typ": "JWT"
            }
            payload = {
                "iss": access_key,
                "exp": int(time.time()) + 1800,  # 30分钟有效期
                "nbf": int(time.time()) - 5      # 开始生效时间
            }
            token = jwt.encode(payload, secret_key, headers=headers)
            self._log("JWT token 生成成功")
            return token
        except Exception as e:
            self._log(f"JWT token 生成失败: {str(e)}", "ERROR")
            raise

    def tensor_to_base64(self, image_tensor):
        """将图像tensor转换为base64编码"""
        try:
            # 确保tensor在正确的范围内 [0, 1]
            if image_tensor.max() <= 1.0:
                image_np = (image_tensor.squeeze().cpu().numpy() * 255).astype(np.uint8)
            else:
                image_np = image_tensor.squeeze().cpu().numpy().astype(np.uint8)
            
            # 转换为PIL图像
            if len(image_np.shape) == 3:
                image = Image.fromarray(image_np)
            else:
                raise ValueError("图像tensor格式不正确")
            
            # 转换为base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            self._log(f"图像转换为base64成功，尺寸: {image.size}")
            return encoded_string
        except Exception as e:
            self._log(f"图像转换失败: {str(e)}", "ERROR")
            raise ValueError(f"图像转换失败: {e}")

    def validate_parameters(self, **kwargs):
        """验证API参数"""
        # 验证必需参数
        prompt = kwargs.get('prompt', '').strip()
        if not prompt:
            return False, "prompt参数不能为空"
        
        if len(prompt) > 2500:
            return False, "prompt参数不能超过2500个字符"
        
        # 验证可选参数
        negative_prompt = kwargs.get('negative_prompt', '').strip()
        if negative_prompt and len(negative_prompt) > 2500:
            return False, "negative_prompt参数不能超过2500个字符"
        
        # 验证模型名称
        model_name = kwargs.get('model_name', 'kling-v1')
        valid_models = ['kling-v1', 'kling-v1-5', 'kling-v2', 'kling-v2-new', 'kling-v2-1']
        if model_name not in valid_models:
            return False, f"model_name必须是以下之一: {', '.join(valid_models)}"
        
        # 验证image_reference
        image_reference = kwargs.get('image_reference')
        has_image = kwargs.get('has_image', False)
        
        if image_reference:
            valid_references = ['subject', 'face']
            if image_reference not in valid_references:
                return False, f"image_reference必须是以下之一: {', '.join(valid_references)}"
            
            # 检查是否有参考图像
            if not has_image:
                return False, "设置了image_reference但未提供参考图像，请连接图像输入或提供image_url"
            
            # kling-v1-5 + face 的特殊要求
            if image_reference == 'face' and model_name != 'kling-v1-5':
                return False, "image_reference为face时，model_name必须是kling-v1-5"
        
        return True, ""

    def submit_task(self, jwt_token, payload, use_proxy=True):
        """提交生成任务"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "User-Agent": "ComfyUI-Ketu-V2/1.0"
        }
        
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
        
        try:
            self._log(f"提交任务到: {self.api_url}")
            response = requests.post(self.api_url, **request_kwargs)
            
            self._log(f"收到响应, 状态码: {response.status_code}")
            
            response_data = response.json()
            
            if not response.ok:
                error_msg = response_data.get('message', '未知错误')
                self._log(f"任务提交失败: {error_msg}", "ERROR")
                raise ValueError(f"任务提交失败 (状态码: {response.status_code}): {error_msg}")
            
            if response_data.get('code') != 0:
                error_msg = response_data.get('message', '任务提交失败')
                self._log(f"任务提交失败: {error_msg}", "ERROR")
                raise ValueError(f"任务提交失败: {error_msg}")
            
            self._log("任务提交成功")
            return response_data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            self._log(f"网络请求失败: {str(e)}", "ERROR")
            raise ValueError(f"网络请求失败: {str(e)}")

    def query_task_status(self, jwt_token, task_id, use_proxy=True):
        """查询任务状态"""
        query_url = f"https://api-beijing.klingai.com/v1/images/generations/{task_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "User-Agent": "ComfyUI-Ketu-V2/1.0"
        }
        
        # 配置代理
        request_kwargs = {
            "headers": headers,
            "timeout": 30
        }
        if use_proxy:
            request_kwargs["proxies"] = {"http": None, "https": None}
        
        try:
            response = requests.get(query_url, **request_kwargs)
            response_data = response.json()
            
            if not response.ok:
                error_msg = response_data.get('message', '未知错误')
                self._log(f"查询任务状态失败: {error_msg}", "ERROR")
                raise ValueError(f"查询任务状态失败 (状态码: {response.status_code}): {error_msg}")
            
            if response_data.get('code') != 0:
                error_msg = response_data.get('message', '查询任务状态失败')
                self._log(f"查询任务状态失败: {error_msg}", "ERROR")
                raise ValueError(f"查询任务状态失败: {error_msg}")
            
            return response_data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            self._log(f"查询请求失败: {str(e)}", "ERROR")
            raise ValueError(f"查询请求失败: {str(e)}")

    def wait_for_completion(self, jwt_token, task_id, timeout, poll_interval, use_proxy=True):
        """等待任务完成"""
        start_time = time.time()
        self._log(f"开始轮询任务状态，最大等待时间: {timeout}秒")
        
        attempt = 0
        while time.time() - start_time < timeout:
            attempt += 1
            try:
                elapsed = time.time() - start_time
                task_data = self.query_task_status(jwt_token, task_id, use_proxy)
                task_status = task_data.get('task_status', '')
                
                self._log(f"轮询尝试 {attempt}, 状态: {task_status}, 耗时: {elapsed:.1f}s")
                
                if task_status == 'succeed':
                    self._log("任务成功完成", "SUCCESS")
                    return task_data
                elif task_status == 'failed':
                    error_msg = task_data.get('task_status_msg', '任务执行失败')
                    self._log(f"任务执行失败: {error_msg}", "ERROR")
                    raise ValueError(f"任务执行失败: {error_msg}")
                elif task_status in ['submitted', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    self._log(f"未知任务状态: {task_status}", "WARN")
                    time.sleep(poll_interval)
                    continue
                    
            except Exception as e:
                self._log(f"轮询查询失败: {str(e)}", "WARN")
                time.sleep(poll_interval)
                continue
        
        self._log(f"任务超时（{timeout}秒）", "ERROR")
        raise ValueError(f"任务超时（{timeout}秒），请稍后重试")

    def download_image(self, image_url, image_download_proxy, image_proxy_url):
        """下载图像并转换为tensor"""
        try:
            self._log(f"开始下载图像: {image_url[:80]}...")
            
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
            
            response = requests.get(image_url, **download_kwargs)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为tensor
            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            self._log(f"图像下载成功: {image.size}, 模式: {image.mode}")
            return image_tensor
            
        except Exception as e:
            self._log(f"图像下载失败: {str(e)}", "ERROR")
            raise ValueError(f"图像下载失败: {str(e)}")

    def generate_image(self, access_key, secret_key, prompt, model_name, aspect_ratio, 
                      wait_for_result, timeout, poll_interval, use_proxy, 
                      image_download_proxy, image_proxy_url, 
                      negative_prompt="", image=None, image_url="", image_reference="", 
                      image_fidelity=0.5, human_fidelity=0.45):
        """
        可图文生图 V2
        """
        # 清空并初始化日志
        self._clear_logs()
        self._log("开始可图文生图任务")
        
        try:
            # 验证认证信息
            self._log("开始参数验证")
            if not access_key or not secret_key:
                self._log("参数验证失败: Access Key或Secret Key为空", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "Access Key和Secret Key不能为空"
                return (blank_image, False, error_msg, "", log_output)
            
            # 检查是否有参考图像
            has_image = (image is not None) or (image_url and image_url.strip())
            self._log(f"参考图像: {'有' if has_image else '无'}")
            
            # 验证参数
            params = {
                'prompt': prompt,
                'model_name': model_name,
                'negative_prompt': negative_prompt,
                'image_reference': image_reference if image_reference else None,
                'image_fidelity': image_fidelity,
                'human_fidelity': human_fidelity,
                'aspect_ratio': aspect_ratio,
                'has_image': has_image
            }
            
            is_valid, error_msg = self.validate_parameters(**params)
            if not is_valid:
                self._log(f"参数验证失败: {error_msg}", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                full_error_msg = f"参数验证失败: {error_msg}"
                return (blank_image, False, full_error_msg, "", log_output)
            
            self._log("参数验证通过")
            
            # 生成JWT token
            self._log("生成JWT token")
            jwt_token = self.encode_jwt_token(access_key, secret_key)
            
            # 构建请求载荷
            self._log("构建请求载荷")
            payload = {
                "prompt": prompt.strip(),
                "aspect_ratio": aspect_ratio
            }
            
            # 添加可选参数
            if model_name != "kling-v1":
                payload["model_name"] = model_name
                self._log(f"模型: {model_name}")
            
            if negative_prompt and negative_prompt.strip():
                payload["negative_prompt"] = negative_prompt.strip()
                self._log(f"负面提示词: {negative_prompt.strip()[:50]}{'...' if len(negative_prompt.strip()) > 50 else ''}")
            
            # 处理图像参数
            if image is not None:
                image_b64 = self.tensor_to_base64(image)
                payload["image"] = image_b64
                self._log("使用输入图像tensor")
            elif image_url and image_url.strip():
                payload["image"] = image_url.strip()
                self._log(f"使用图像URL: {image_url[:80]}...")
            
            # 只有在提供参考图像时，才添加图像相关参数
            if has_image:
                if image_reference:
                    payload["image_reference"] = image_reference
                    self._log(f"图像参考类型: {image_reference}")
                
                if image_fidelity != 0.5:
                    payload["image_fidelity"] = image_fidelity
                    self._log(f"图像参考强度: {image_fidelity}")
                
                if human_fidelity != 0.45:
                    payload["human_fidelity"] = human_fidelity
                    self._log(f"面部参考强度: {human_fidelity}")
                    
                self._log(f"图像参考模式启用")
            else:
                self._log("纯文生图模式")
            
            self._log(f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            self._log(f"宽高比: {aspect_ratio}")
            self._log(f"超时设置: {timeout}秒, 轮询间隔: {poll_interval}秒")
            
            # 提交任务
            task_data = self.submit_task(jwt_token, payload, use_proxy)
            task_id = task_data.get('task_id')
            
            if not task_id:
                self._log("任务提交成功但未获取到task_id", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "任务提交成功但未获取到task_id"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log(f"任务已提交，task_id: {task_id}")
            
            # 如果不等待结果，返回空图像和任务信息
            if not wait_for_result:
                self._log("不等待结果，直接返回", "INFO")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                
                response_json = json.dumps({
                    "task_id": task_id,
                    "status": "submitted",
                    "message": "任务已提交，请稍后查询结果"
                }, ensure_ascii=False, indent=2)
                
                usage_info = f"可图文生图任务提交成功\n任务ID: {task_id}\n状态: 已提交\n模型: {model_name}\n宽高比: {aspect_ratio}"
                
                success_message = "任务已提交，未等待结果"
                return (blank_image, True, success_message, response_json, log_output)
            
            # 等待任务完成
            start_time = time.time()
            completed_data = self.wait_for_completion(jwt_token, task_id, timeout, poll_interval, use_proxy)
            total_time = time.time() - start_time
            self._log(f"总耗时: {total_time:.1f}秒")
            
            # 提取图像URL
            self._log("开始处理生成的图像")
            task_result = completed_data.get('task_result', {})
            images_data = task_result.get('images', [])
            
            if not images_data:
                self._log("任务完成但没有生成图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "任务完成但没有生成图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            self._log(f"收到 {len(images_data)} 个图像数据")
            
            # 下载图像
            image_tensors = []
            for i, img_data in enumerate(images_data):
                if isinstance(img_data, dict) and 'url' in img_data:
                    image_url_result = img_data['url']
                    
                    try:
                        image_tensor = self.download_image(image_url_result, image_download_proxy, image_proxy_url)
                        image_tensors.append(image_tensor)
                    except Exception as e:
                        self._log(f"下载图像 {i+1} 失败: {str(e)}", "ERROR")
                        continue
            
            if not image_tensors:
                self._log("没有可用的图像数据", "ERROR")
                log_output = self._print_and_format_logs()
                blank_image = self._create_blank_image()
                error_msg = "没有可用的图像数据"
                return (blank_image, False, error_msg, "", log_output)
            
            # 合并所有图像
            result_images = torch.cat(image_tensors, dim=0)
            self._log(f"成功处理 {len(image_tensors)} 张图像")
            
            # 构建返回信息
            usage_info = f"可图文生图完成\n"
            usage_info += f"任务ID: {task_id}\n"
            usage_info += f"模型: {model_name}\n"
            usage_info += f"宽高比: {aspect_ratio}\n"
            usage_info += f"生成图像数量: {len(image_tensors)}\n"
            usage_info += f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            usage_info += f"总耗时: {total_time:.1f}秒"
            
            # 记录API使用信息
            self._log(f"API使用信息: {usage_info.replace(chr(10), ' | ')}")
            self._log("图像生成任务完成", "SUCCESS")
            
            # 打印并获取执行日志
            log_output = self._print_and_format_logs()
            
            # 返回完整的响应JSON
            response_json = json.dumps(completed_data, ensure_ascii=False, indent=2)
            
            # 构建成功消息
            success_message = f"图像生成成功，共 {len(image_tensors)} 张"
            
            return (result_images, True, success_message, response_json, log_output)
            
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
    "KetuTextToImageV2": KetuTextToImageNodeV2
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KetuTextToImageV2": "可图文生图 V2 (Ketu T2I)"
}

