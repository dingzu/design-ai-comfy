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
                "environment": (["prod", "staging", "idc"], {
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
                "edit_type": (["edit", "inpaint", "outpaint"], {
                    "default": "edit",
                    "tooltip": "编辑类型: edit(普通编辑), inpaint(修复), outpaint(扩展)"
                }),
                "image_size": (["auto", "1328*1328", "1664*928", "1472*1140", "1140*1472", "928*1664"], {
                    "default": "auto",
                    "tooltip": "输出图像尺寸"
                }),
                "image_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量"
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
                    "tooltip": "是否使用代理服务器"
                })
            },
            "optional": {
                "mask": ("MASK", {
                    "tooltip": "编辑蒙版（可选，用于inpaint等操作）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info", "task_info")
    FUNCTION = "edit_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal"
        }

    def edit_image(self, environment, api_key, image, prompt, edit_type, 
                   image_size, image_count, watermark, timeout, poll_interval, use_proxy, mask=None):
        """
        Qwen-Image 图像编辑（异步API）
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("编辑指令不能为空")
            
            if image is None:
                raise ValueError("输入图像不能为空")

            # 转换图像为base64
            image_base64 = self._image_to_base64(image)
            
            # 处理蒙版（如果提供）
            mask_base64 = None
            if mask is not None:
                mask_base64 = self._mask_to_base64(mask)

            # 构建URL
            base_url = self.environments[environment]
            submit_url = f"{base_url}/ai-serve/v1/qwen-image/image2image/image-synthesis"
            
            # 构建请求体
            payload = {
                "model": "qwen-image",
                "input": {
                    "prompt": prompt.strip(),
                    "image": image_base64
                },
                "parameters": {
                    "edit_type": edit_type,
                    "size": image_size,
                    "n": image_count,
                    "watermark": watermark
                }
            }
            
            # 如果有蒙版，添加到输入中
            if mask_base64:
                payload["input"]["mask"] = mask_base64
            
            # 设置请求头
            headers = {
                "X-DashScope-Async": "enable",
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-QwenImage-Edit/1.0"
            }
            
            print(f"[Qwen-Image Edit] 发送请求到: {submit_url}")
            print(f"[Qwen-Image Edit] 编辑类型: {edit_type}")
            print(f"[Qwen-Image Edit] 编辑指令: {prompt}")
            print(f"[Qwen-Image Edit] 图像尺寸: {image_size}")
            print(f"[Qwen-Image Edit] 是否有蒙版: {'是' if mask_base64 else '否'}")
            
            # 配置代理
            submit_kwargs = {
                "headers": headers,
                "json": payload,
                "timeout": 30  # 提交任务的超时时间较短
            }
            if use_proxy:
                submit_kwargs["proxies"] = {"http": None, "https": None}
            
            # 1. 提交任务
            response = requests.post(submit_url, **submit_kwargs)
            
            print(f"[Qwen-Image Edit] 任务提交响应状态码: {response.status_code}")
            
            # 解析提交响应
            try:
                submit_result = response.json()
            except json.JSONDecodeError:
                raise ValueError(f"无效的JSON响应: {response.text}")
            
            # 检查提交状态
            if not response.ok:
                error_msg = submit_result.get('error', {}).get('message', response.text)
                raise ValueError(f"任务提交失败 [{response.status_code}]: {error_msg}")
            
            # 获取任务ID
            task_id = submit_result.get("output", {}).get("task_id")
            if not task_id:
                raise ValueError("未获取到任务ID")
            
            print(f"[Qwen-Image Edit] 任务提交成功，任务ID: {task_id}")
            
            # 2. 轮询任务状态
            result = self._poll_task_status(base_url, api_key, task_id, timeout, poll_interval, use_proxy)
            
            if not result:
                raise ValueError("任务执行失败或超时")
            
            # 3. 处理结果
            return self._process_result(result, task_id, edit_type, use_proxy)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒）。Qwen-Image编辑可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像编辑失败: {str(e)}")

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
            
            print(f"[Qwen-Image Edit] 图像转换完成: {pil_image.size}, 模式: {pil_image.mode}")
            return image_base64
            
        except Exception as e:
            raise ValueError(f"图像转换失败: {str(e)}")

    def _mask_to_base64(self, mask_tensor):
        """将蒙版tensor转换为base64"""
        try:
            # 获取第一个蒙版（如果是批量）
            if len(mask_tensor.shape) == 3:
                mask = mask_tensor[0]
            else:
                mask = mask_tensor
            
            # 转换为numpy并转换到0-255范围
            mask_np = (mask.cpu().numpy() * 255).astype(np.uint8)
            
            # 创建PIL图像（灰度）
            pil_mask = Image.fromarray(mask_np, mode='L')
            
            # 转换为base64
            buffer = io.BytesIO()
            pil_mask.save(buffer, format="PNG")
            mask_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            print(f"[Qwen-Image Edit] 蒙版转换完成: {pil_mask.size}")
            return mask_base64
            
        except Exception as e:
            raise ValueError(f"蒙版转换失败: {str(e)}")

    def _poll_task_status(self, base_url, api_key, task_id, timeout, poll_interval, use_proxy):
        """轮询任务状态"""
        query_url = f"{base_url}/ai-serve/v1/qwen-image-tasks/{task_id}"
        headers = {"x-api-key": api_key}
        
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)
        
        print(f"[Qwen-Image Edit] 开始轮询任务状态，最大尝试次数: {max_attempts}")
        
        for attempt in range(max_attempts):
            try:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print(f"[Qwen-Image Edit] 任务查询超时（{elapsed:.1f}s）")
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
                    print(f"[Qwen-Image Edit] 查询失败 {response.status_code}: {response.text}")
                    time.sleep(poll_interval)
                    continue
                
                result = response.json()
                task_status = result.get("output", {}).get("task_status")
                
                print(f"[Qwen-Image Edit] 查询尝试 {attempt + 1}/{max_attempts}, 状态: {task_status}, 耗时: {elapsed:.1f}s")
                
                if task_status == "SUCCEEDED":
                    print("[Qwen-Image Edit] 任务成功完成！")
                    return result
                
                elif task_status == "FAILED":
                    error_msg = result.get("output", {}).get("message", "任务失败")
                    raise ValueError(f"任务执行失败: {error_msg}")
                
                elif task_status in ["PENDING", "RUNNING"]:
                    time.sleep(poll_interval)
                
                else:
                    print(f"[Qwen-Image Edit] 未知任务状态: {task_status}")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                print(f"[Qwen-Image Edit] 查询异常: {str(e)}")
                time.sleep(poll_interval)
        
        return None

    def _process_result(self, result, task_id, edit_type, use_proxy):
        """处理编辑结果"""
        try:
            # 提取结果数据
            results = result.get("output", {}).get("results", [])
            if not results:
                raise ValueError("响应中没有图像数据")
            
            images_tensor = []
            image_urls = []
            
            print(f"[Qwen-Image Edit] 处理 {len(results)} 个结果")
            
            for idx, item in enumerate(results):
                image_url = item.get("url")
                if not image_url:
                    print(f"[Qwen-Image Edit] 结果 {idx + 1} 没有图像URL")
                    continue
                
                image_urls.append(image_url)
                
                # 下载图像
                try:
                    print(f"[Qwen-Image Edit] 下载图像 {idx + 1}: {image_url}")
                    # 配置代理
                    download_kwargs = {"timeout": 60}
                    if use_proxy:
                        download_kwargs["proxies"] = {"http": None, "https": None}
                    
                    img_response = requests.get(image_url, **download_kwargs)
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        
                        # 转换为RGB（如果不是的话）
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # 转换为tensor
                        image_np = np.array(image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        
                        print(f"[Qwen-Image Edit] 图像 {idx + 1}: {image.size}, 模式: {image.mode}")
                    else:
                        print(f"[Qwen-Image Edit] 图像下载失败 {img_response.status_code}")
                        
                except Exception as e:
                    print(f"[Qwen-Image Edit] 下载图像 {idx + 1} 异常: {str(e)}")
            
            if not images_tensor:
                raise ValueError("没有成功下载的图像")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化任务信息
            output = result.get("output", {})
            task_info = f"编辑任务信息:\n"
            task_info += f"- 任务ID: {task_id}\n"
            task_info += f"- 编辑类型: {edit_type}\n"
            task_info += f"- 提交时间: {output.get('submit_time', 'N/A')}\n"
            task_info += f"- 开始时间: {output.get('scheduled_time', 'N/A')}\n"
            task_info += f"- 完成时间: {output.get('end_time', 'N/A')}\n"
            task_info += f"- 图像URLs: {len(image_urls)}"
            
            # 格式化使用信息
            usage = output.get('usage', {})
            usage_info = f"使用统计:\n"
            usage_info += f"- 编辑图像数量: {usage.get('image_count', len(images_tensor))}\n"
            usage_info += f"- 成功下载: {len(images_tensor)}"
            
            # 添加提示词信息
            if results:
                first_result = results[0]
                if 'orig_prompt' in first_result:
                    usage_info += f"\n- 原始指令: {first_result['orig_prompt'][:100]}..."
                if 'actual_prompt' in first_result:
                    usage_info += f"\n- 处理后指令: {first_result['actual_prompt'][:100]}..."
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            print(f"[Qwen-Image Edit] 图像编辑完成")
            print(f"[Qwen-Image Edit] {usage_info}")
            
            return (result_images, response_json, usage_info, task_info)
            
        except Exception as e:
            raise ValueError(f"结果处理失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenImageEdit": QwenImageEditNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEdit": "Qwen-Image 图像编辑"
}
