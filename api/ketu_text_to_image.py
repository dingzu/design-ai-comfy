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

class KetuTextToImageNode:
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

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "task_info", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.api_url = "https://api-beijing.klingai.com/v1/images/generations"

    def encode_jwt_token(self, access_key, secret_key):
        """生成JWT token"""
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
        return token

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
            return encoded_string
        except Exception as e:
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
            "User-Agent": "ComfyUI-Ketu/1.0"
        }
        
        # 配置代理
        request_kwargs = {
            "headers": headers,
            "json": payload,
            "timeout": 30
        }
        if use_proxy:
            request_kwargs["proxies"] = {"http": None, "https": None}
        
        try:
            response = requests.post(self.api_url, **request_kwargs)
            response_data = response.json()
            
            if not response.ok:
                error_msg = response_data.get('message', '未知错误')
                raise ValueError(f"任务提交失败 (状态码: {response.status_code}): {error_msg}")
            
            if response_data.get('code') != 0:
                error_msg = response_data.get('message', '任务提交失败')
                raise ValueError(f"任务提交失败: {error_msg}")
            
            return response_data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"网络请求失败: {str(e)}")

    def query_task_status(self, jwt_token, task_id, use_proxy=True):
        """查询任务状态"""
        query_url = f"https://api-beijing.klingai.com/v1/images/generations/{task_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}",
            "User-Agent": "ComfyUI-Ketu/1.0"
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
                raise ValueError(f"查询任务状态失败 (状态码: {response.status_code}): {error_msg}")
            
            if response_data.get('code') != 0:
                error_msg = response_data.get('message', '查询任务状态失败')
                raise ValueError(f"查询任务状态失败: {error_msg}")
            
            return response_data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"查询请求失败: {str(e)}")

    def wait_for_completion(self, jwt_token, task_id, timeout, poll_interval, use_proxy=True):
        """等待任务完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                task_data = self.query_task_status(jwt_token, task_id, use_proxy)
                task_status = task_data.get('task_status', '')
                
                if task_status == 'succeed':
                    return task_data
                elif task_status == 'failed':
                    error_msg = task_data.get('task_status_msg', '任务执行失败')
                    raise ValueError(f"任务执行失败: {error_msg}")
                elif task_status in ['submitted', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    time.sleep(poll_interval)
                    continue
                    
            except Exception as e:
                print(f"[可图] 轮询查询失败: {str(e)}")
                time.sleep(poll_interval)
                continue
        
        raise ValueError(f"任务超时（{timeout}秒），请稍后重试")

    def download_image(self, image_url, use_proxy=True):
        """下载图像并转换为tensor"""
        try:
            # 配置代理
            request_kwargs = {"timeout": 60}
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            response = requests.get(image_url, **request_kwargs)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为tensor
            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            return image_tensor
            
        except Exception as e:
            raise ValueError(f"图像下载失败: {str(e)}")

    def generate_image(self, access_key, secret_key, prompt, model_name, aspect_ratio, 
                      wait_for_result, timeout, poll_interval, use_proxy=True, negative_prompt="", 
                      image=None, image_url="", image_reference="", 
                      image_fidelity=0.5, human_fidelity=0.45):
        """
        可图文生图主函数
        """
        try:
            # 验证认证信息
            if not access_key or not secret_key:
                raise ValueError("Access Key和Secret Key不能为空")
            
            # 检查是否有参考图像
            has_image = (image is not None) or (image_url and image_url.strip())
            
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
                raise ValueError(f"参数验证失败: {error_msg}")
            
            # 生成JWT token
            jwt_token = self.encode_jwt_token(access_key, secret_key)
            
            # 构建请求载荷
            payload = {
                "prompt": prompt.strip(),
                "aspect_ratio": aspect_ratio
            }
            
            # 添加可选参数
            if model_name != "kling-v1":  # 默认值不需要显式添加
                payload["model_name"] = model_name
            
            if negative_prompt and negative_prompt.strip():
                payload["negative_prompt"] = negative_prompt.strip()
            
            # 处理图像参数
            if image is not None:
                image_b64 = self.tensor_to_base64(image)
                payload["image"] = image_b64
                print(f"[可图] 使用输入图像tensor")
            elif image_url and image_url.strip():
                payload["image"] = image_url.strip()
                print(f"[可图] 使用图像URL: {image_url}")
            
            # 只有在提供参考图像时，才添加图像相关参数，避免API报错
            # 修复：image_fidelity parameter is not supported by current model
            if has_image:
                if image_reference:
                    payload["image_reference"] = image_reference
                
                # 只有在非默认值时才添加，减少不必要参数
                if image_fidelity != 0.5:
                    payload["image_fidelity"] = image_fidelity
                
                if human_fidelity != 0.45:
                    payload["human_fidelity"] = human_fidelity
                    
                print(f"[可图] 图像参考模式 - 参考类型: {image_reference}, 图像强度: {image_fidelity}, 面部强度: {human_fidelity}")
            else:
                print(f"[可图] 纯文生图模式 - 跳过图像参考参数")
            
            print(f"[可图] 开始生成图像，模型: {model_name}，比例: {aspect_ratio}")
            
            # 提交任务
            task_data = self.submit_task(jwt_token, payload, use_proxy)
            task_id = task_data.get('task_id')
            
            if not task_id:
                raise ValueError("任务提交成功但未获取到task_id")
            
            print(f"[可图] 任务已提交，task_id: {task_id}")
            
            # 如果不等待结果，返回空图像和任务信息
            if not wait_for_result:
                # 创建空图像tensor
                empty_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                
                task_info = json.dumps({
                    "task_id": task_id,
                    "status": "submitted",
                    "message": "任务已提交，请稍后查询结果"
                }, ensure_ascii=False, indent=2)
                
                usage_info = f"可图文生图任务提交成功\n任务ID: {task_id}\n状态: 已提交\n模型: {model_name}\n宽高比: {aspect_ratio}"
                
                return (empty_image, task_info, usage_info)
            
            # 等待任务完成
            print(f"[可图] 等待任务完成，超时时间: {timeout}秒")
            completed_data = self.wait_for_completion(jwt_token, task_id, timeout, poll_interval, use_proxy)
            
            # 提取图像URL
            task_result = completed_data.get('task_result', {})
            images_data = task_result.get('images', [])
            
            if not images_data:
                raise ValueError("任务完成但没有生成图像数据")
            
            # 下载图像
            image_tensors = []
            for i, img_data in enumerate(images_data):
                if isinstance(img_data, dict) and 'url' in img_data:
                    image_url = img_data['url']
                    print(f"[可图] 下载图像 {i+1}: {image_url}")
                    
                    image_tensor = self.download_image(image_url, use_proxy)
                    image_tensors.append(image_tensor)
            
            if not image_tensors:
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(image_tensors, dim=0)
            
            # 构建返回信息
            task_info = json.dumps(completed_data, ensure_ascii=False, indent=2)
            
            usage_info = f"可图文生图完成\n"
            usage_info += f"任务ID: {task_id}\n"
            usage_info += f"模型: {model_name}\n"
            usage_info += f"宽高比: {aspect_ratio}\n"
            usage_info += f"生成图像数量: {len(image_tensors)}\n"
            usage_info += f"提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
            
            print(f"[可图] 图像生成完成，共 {len(image_tensors)} 张图像")
            
            return (result_images, task_info, usage_info)
            
        except Exception as e:
            print(f"[可图] 图像生成失败: {str(e)}")
            # 返回错误信息
            error_image = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            
            error_info = json.dumps({
                "error": str(e),
                "status": "failed"
            }, ensure_ascii=False, indent=2)
            
            error_usage = f"可图文生图失败\n错误: {str(e)}"
            
            return (error_image, error_info, error_usage)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "KetuTextToImage": KetuTextToImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KetuTextToImage": "可图文生图 (Ketu T2I)"
}

