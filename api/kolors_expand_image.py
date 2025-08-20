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

class KolorsExpandImageNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "environment": (["staging", "prod", "idc"], {
                    "default": "staging",
                    "tooltip": "选择万擎网关环境"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "万擎网关API密钥 (x-api-key)"
                }),
                "prompt": ("STRING", {
                    "default": "自然扩展图片内容",
                    "multiline": True,
                    "tooltip": "扩展图片描述提示词"
                }),
                "model_name": (["kling-v2"], {
                    "default": "kling-v2",
                    "tooltip": "可图模型名称"
                }),
                "up_expansion_ratio": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "向上扩展比例（0.0为不扩展）"
                }),
                "down_expansion_ratio": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "向下扩展比例（0.0为不扩展）"
                }),
                "left_expansion_ratio": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "向左扩展比例（0.0为不扩展）"
                }),
                "right_expansion_ratio": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "向右扩展比例（0.0为不扩展）"
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

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "expand_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal"
        }

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
        
        # 返回纯base64字符串（扩图API可能不需要data URI前缀）
        base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64_string

    def submit_task(self, environment, api_key, payload):
        """提交扩展任务"""
        base_url = self.environments[environment]
        url = f"{base_url}/ai-serve/v1/ktu/images/editing/expand"
        
        headers = {
            "x-api-key": api_key.strip(),
            "Content-Type": "application/json",
            "User-Agent": "ComfyUI-Kolors-Expand/1.0"
        }
        
        print(f"[可图扩图] 提交任务到: {url}")
        print(f"[可图扩图] 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"[可图扩图] 响应状态码: {response.status_code}")
        print(f"[可图扩图] 响应头: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"[可图扩图] 响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            response_text = response.text if response.text else "空响应"
            print(f"[可图扩图] 响应文本: {response_text}")
            raise ValueError(f"无效的JSON响应 (状态码: {response.status_code}): {response_text}")
        
        if not response.ok:
            error_msg = response_data.get('message', '未知错误')
            if "too large" in error_msg.lower():
                raise ValueError(f"扩展参数过大：{error_msg}\n\n💡 建议：\n1. 降低扩展比例（建议总扩展不超过原图3倍）\n2. 使用较小的原始图像\n3. 分步进行扩展")
            raise ValueError(f"任务提交失败 (状态码: {response.status_code}): {error_msg}")
        
        if response_data.get('code') != 0:
            error_msg = response_data.get('message', '未知错误')
            if "too large" in error_msg.lower():
                raise ValueError(f"扩展参数过大：{error_msg}\n\n💡 建议：\n1. 降低扩展比例（建议总扩展不超过原图3倍）\n2. 使用较小的原始图像\n3. 分步进行扩展")
            raise ValueError(f"任务提交失败: {error_msg}")
        
        return response_data.get('data', {})

    def poll_task_result(self, environment, api_key, task_id, timeout, poll_interval):
        """轮询任务结果"""
        base_url = self.environments[environment]
        url = f"{base_url}/ai-serve/v1/ktu/images/editing/expand/{task_id}"
        
        headers = {
            "x-api-key": api_key.strip(),
            "User-Agent": "ComfyUI-Kolors-Expand/1.0"
        }
        
        print(f"[可图扩图] 轮询URL: {url}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            print(f"[可图扩图] 轮询任务状态: {task_id}")
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response_data = response.json()
                
                print(f"[可图扩图] 轮询响应状态码: {response.status_code}")
                print(f"[可图扩图] 轮询响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                if not response.ok:
                    error_msg = response_data.get('message', '未知错误')
                    raise ValueError(f"获取任务状态失败 (状态码: {response.status_code}): {error_msg}")
                
                if response_data.get('code') != 0:
                    error_msg = response_data.get('message', '未知错误')
                    raise ValueError(f"获取任务状态失败: {error_msg}")
                
                data = response_data.get('data', {})
                task_status = data.get('task_status', '')
                
                print(f"[可图扩图] 任务状态: {task_status}")
                
                if task_status == 'succeed':
                    return response_data
                elif task_status == 'failed':
                    error_msg = data.get('fail_reason', '任务执行失败')
                    raise ValueError(f"任务执行失败: {error_msg}")
                elif task_status in ['submitted', 'processing']:
                    time.sleep(poll_interval)
                    continue
                else:
                    print(f"[可图扩图] 未知任务状态: {task_status}")
                    time.sleep(poll_interval)
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"[可图扩图] 轮询请求失败: {str(e)}")
                time.sleep(poll_interval)
                continue
        
        raise ValueError(f"任务超时（{timeout}秒），请稍后重试或增加超时时间")

    def expand_image(self, environment, api_key, prompt, model_name, 
                    up_expansion_ratio, down_expansion_ratio, left_expansion_ratio, right_expansion_ratio,
                    timeout, poll_interval, image=None, image_url=None):
        """
        可图扩图
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("提示词不能为空")

            # 检查扩展比例
            total_expansion = up_expansion_ratio + down_expansion_ratio + left_expansion_ratio + right_expansion_ratio
            if total_expansion > 4:  # 保守估计，总扩展不超过合理范围
                print(f"[可图扩图] 警告: 扩展比例较大（总计: {total_expansion:.1f}），可能导致失败。建议降低扩展比例。")

            # 处理输入图像
            image_input = None
            if image is not None:
                # 使用提供的图像tensor，转换为base64
                image_input = self.tensor_to_base64(image)
                print(f"[可图扩图] 使用输入图像tensor，尺寸: {image.shape}")
                print(f"[可图扩图] Base64前缀: {image_input[:50]}...")
            elif image_url and image_url.strip():
                # 使用图像URL
                image_input = image_url.strip()
                print(f"[可图扩图] 使用图像URL: {image_input}")
            else:
                raise ValueError("必须提供输入图像或图像URL")

            # 构建请求体
            payload = {
                "model_name": model_name,
                "prompt": prompt.strip(),
                "image": image_input,
                "up_expansion_ratio": up_expansion_ratio,
                "down_expansion_ratio": down_expansion_ratio,
                "left_expansion_ratio": left_expansion_ratio,
                "right_expansion_ratio": right_expansion_ratio
            }
            
            # 提交任务
            task_data = self.submit_task(environment, api_key, payload)
            task_id = task_data.get('task_id')
            
            if not task_id:
                raise ValueError("任务提交成功但未获取到task_id")
            
            print(f"[可图扩图] 任务已提交，task_id: {task_id}")
            
            # 轮询任务结果
            result_data = self.poll_task_result(environment, api_key, task_id, timeout, poll_interval)
            
            # 处理生成的图像
            data = result_data.get('data', {})
            print(f"[可图扩图] 完整响应数据结构:")
            print(f"[可图扩图] result_data keys: {list(result_data.keys())}")
            print(f"[可图扩图] data keys: {list(data.keys())}")
            
            # 根据实际API响应结构提取图像
            task_result = data.get('task_result', {})
            images_data = task_result.get('images', [])
            
            print(f"[可图扩图] task_result keys: {list(task_result.keys())}")
            print(f"[可图扩图] images_data: {images_data}")
            
            # 提取图像URL列表
            image_urls = []
            if images_data:
                for img in images_data:
                    if isinstance(img, dict) and 'url' in img:
                        image_urls.append(img['url'])
                    elif isinstance(img, str):
                        image_urls.append(img)
            
            print(f"[可图扩图] 提取到的图像URLs: {image_urls}")
            
            if not image_urls:
                print(f"[可图扩图] 未找到图像数据，完整task_result: {json.dumps(task_result, ensure_ascii=False, indent=2)}")
                raise ValueError("任务完成但没有生成图像数据")
            
            print(f"[可图扩图] 成功生成 {len(image_urls)} 张图像")
            
            images_tensor = []
            for idx, image_url in enumerate(image_urls):
                print(f"[可图扩图] 下载图像 {idx + 1}: {image_url}")
                
                try:
                    img_response = requests.get(image_url, timeout=60)
                    img_response.raise_for_status()
                    result_image = Image.open(io.BytesIO(img_response.content))
                    
                    # 转换为RGB
                    if result_image.mode != 'RGB':
                        result_image = result_image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(result_image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    print(f"[可图扩图] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                except Exception as e:
                    print(f"[可图扩图] 下载图像失败: {str(e)}")
                    continue
            
            if not images_tensor:
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage_info = f"可图扩图结果:\n"
            usage_info += f"- 模型: {model_name}\n"
            usage_info += f"- 任务ID: {task_id}\n"
            usage_info += f"- 提示词: {prompt.strip()}\n"
            usage_info += f"- 输入图像: {'Tensor (base64)' if image is not None else 'URL'}\n"
            usage_info += f"- 上扩展: {up_expansion_ratio:.1f} ({'不扩展' if up_expansion_ratio == 0 else f'+{up_expansion_ratio*100:.0f}%'})\n"
            usage_info += f"- 下扩展: {down_expansion_ratio:.1f} ({'不扩展' if down_expansion_ratio == 0 else f'+{down_expansion_ratio*100:.0f}%'})\n"
            usage_info += f"- 左扩展: {left_expansion_ratio:.1f} ({'不扩展' if left_expansion_ratio == 0 else f'+{left_expansion_ratio*100:.0f}%'})\n"
            usage_info += f"- 右扩展: {right_expansion_ratio:.1f} ({'不扩展' if right_expansion_ratio == 0 else f'+{right_expansion_ratio*100:.0f}%'})\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(result_data, ensure_ascii=False, indent=2)
            
            print(f"[可图扩图] 图像扩展完成")
            print(f"[可图扩图] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时。图像扩展可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像扩展失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "KolorsExpandImage": KolorsExpandImageNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KolorsExpandImage": "可图扩图"
} 