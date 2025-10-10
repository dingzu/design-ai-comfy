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

class QwenImageText2ImgNode:
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

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info", "task_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        self.environments = {
            "staging": "https://llm-gateway-staging-sgp.corp.kuaishou.com",
            "prod": "https://llm-gateway-prod.corp.kuaishou.com", 
            "idc": "http://llm-gateway.internal",
            "overseas": "http://llm-gateway-sgp.internal",
            "domestic": "http://llm-gateway.internal"
        }

    def generate_image(self, environment, api_key, prompt, image_count, 
                      image_size, prompt_extend, watermark, timeout, poll_interval, use_proxy, image_download_proxy, custom_base_url="", custom_submit_endpoint="/ai-serve/v1/qwen-image/text2image/image-synthesis", custom_query_endpoint="/ai-serve/v1/qwen-image-tasks/{task_id}"):
        """
        Qwen-Image 文本生成图像（异步API）
        """
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                raise ValueError("API Key不能为空，请联系 @于淼 获取万擎网关key")
            
            if not prompt or prompt.strip() == "":
                raise ValueError("图像描述不能为空")

            # 构建URL - 优先使用用户自定义的base_url
            if custom_base_url and custom_base_url.strip():
                base_url = custom_base_url.strip().rstrip('/')
            else:
                base_url = self.environments[environment]
            
            # 使用自定义提交端点路径
            submit_endpoint = custom_submit_endpoint.strip() if custom_submit_endpoint.strip() else "/ai-serve/v1/qwen-image/text2image/image-synthesis"
            submit_endpoint = submit_endpoint.lstrip('/')  # 移除开头的斜杠
            submit_url = f"{base_url}/{submit_endpoint}"
            
            # 构建请求体
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
            
            # 设置请求头
            headers = {
                "X-DashScope-Async": "enable",
                "x-api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-QwenImage-Text2Img/1.0"
            }
            
            print(f"[Qwen-Image] 发送请求到: {submit_url}")
            print(f"[Qwen-Image] 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
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
            
            print(f"[Qwen-Image] 任务提交响应状态码: {response.status_code}")
            
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
            
            print(f"[Qwen-Image] 任务提交成功，任务ID: {task_id}")
            
            # 2. 轮询任务状态
            result = self._poll_task_status(base_url, api_key, task_id, timeout, poll_interval, use_proxy, custom_query_endpoint)
            
            if not result:
                raise ValueError("任务执行失败或超时")
            
            # 3. 处理结果
            return self._process_result(result, task_id, image_download_proxy)
            
        except requests.exceptions.Timeout:
            raise ValueError(f"请求超时（{timeout}秒）。Qwen-Image生成可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. 万擎网关地址是否可访问\n3. 环境选择是否正确")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"图像生成失败: {str(e)}")

    def _poll_task_status(self, base_url, api_key, task_id, timeout, poll_interval, use_proxy, custom_query_endpoint="/ai-serve/v1/qwen-image-tasks/{task_id}"):
        """轮询任务状态"""
        # 使用自定义查询端点路径
        query_endpoint = custom_query_endpoint.strip() if custom_query_endpoint.strip() else "/ai-serve/v1/qwen-image-tasks/{task_id}"
        query_endpoint = query_endpoint.lstrip('/').format(task_id=task_id)  # 移除开头的斜杠并替换占位符
        query_url = f"{base_url}/{query_endpoint}"
        headers = {"x-api-key": api_key}
        
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)
        
        print(f"[Qwen-Image] 开始轮询任务状态，最大尝试次数: {max_attempts}")
        
        for attempt in range(max_attempts):
            try:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print(f"[Qwen-Image] 任务查询超时（{elapsed:.1f}s）")
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
                    print(f"[Qwen-Image] 查询失败 {response.status_code}: {response.text}")
                    time.sleep(poll_interval)
                    continue
                
                result = response.json()
                task_status = result.get("output", {}).get("task_status")
                
                print(f"[Qwen-Image] 查询尝试 {attempt + 1}/{max_attempts}, 状态: {task_status}, 耗时: {elapsed:.1f}s")
                
                if task_status == "SUCCEEDED":
                    print("[Qwen-Image] 任务成功完成！")
                    return result
                
                elif task_status == "FAILED":
                    error_msg = result.get("output", {}).get("message", "任务失败")
                    raise ValueError(f"任务执行失败: {error_msg}")
                
                elif task_status in ["PENDING", "RUNNING"]:
                    time.sleep(poll_interval)
                
                else:
                    print(f"[Qwen-Image] 未知任务状态: {task_status}")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                print(f"[Qwen-Image] 查询异常: {str(e)}")
                time.sleep(poll_interval)
        
        return None

    def _process_result(self, result, task_id, image_download_proxy):
        """处理生成结果"""
        try:
            # 提取结果数据
            results = result.get("output", {}).get("results", [])
            if not results:
                raise ValueError("响应中没有图像数据")
            
            images_tensor = []
            image_urls = []
            
            print(f"[Qwen-Image] 处理 {len(results)} 个结果")
            
            for idx, item in enumerate(results):
                image_url = item.get("url")
                if not image_url:
                    print(f"[Qwen-Image] 结果 {idx + 1} 没有图像URL")
                    continue
                
                image_urls.append(image_url)
                
                # 下载图像
                try:
                    print(f"[Qwen-Image] 下载图像 {idx + 1}: {image_url}")
                    
                    # 配置图片下载代理设置
                    download_kwargs = {"timeout": 60}
                    if image_download_proxy:
                        # 启用系统默认代理（用于访问外部图片URL）
                        print(f"[Qwen-Image] 图片下载启用代理")
                        # 不设置proxies参数，使用系统默认代理
                    else:
                        # 禁用代理（用于内部网络或直连）
                        print(f"[Qwen-Image] 图片下载禁用代理")
                        download_kwargs["proxies"] = {"http": None, "https": None}
                    
                    img_response = requests.get(image_url, **download_kwargs)
                    print(f"[Qwen-Image] 下载响应状态码: {img_response.status_code}")
                    
                    if img_response.status_code == 200:
                        image = Image.open(io.BytesIO(img_response.content))
                        
                        # 转换为RGB（如果不是的话）
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # 转换为tensor
                        image_np = np.array(image).astype(np.float32) / 255.0
                        image_tensor = torch.from_numpy(image_np)[None,]
                        images_tensor.append(image_tensor)
                        
                        print(f"[Qwen-Image] 图像 {idx + 1} 下载成功: {image.size}, 模式: {image.mode}")
                    else:
                        print(f"[Qwen-Image] 图像下载失败 - 状态码: {img_response.status_code}")
                        print(f"[Qwen-Image] 响应内容: {img_response.text[:200]}")
                        if hasattr(img_response, 'headers'):
                            print(f"[Qwen-Image] 响应头: {dict(img_response.headers)}")
                        
                except Exception as e:
                    print(f"[Qwen-Image] 下载图像 {idx + 1} 异常: {str(e)}")
                    print(f"[Qwen-Image] 异常类型: {type(e).__name__}")
                    import traceback
                    print(f"[Qwen-Image] 异常堆栈: {traceback.format_exc()}")
            
            if not images_tensor:
                raise ValueError("没有成功下载的图像")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化任务信息
            output = result.get("output", {})
            task_info = f"任务信息:\n"
            task_info += f"- 任务ID: {task_id}\n"
            task_info += f"- 提交时间: {output.get('submit_time', 'N/A')}\n"
            task_info += f"- 开始时间: {output.get('scheduled_time', 'N/A')}\n"
            task_info += f"- 完成时间: {output.get('end_time', 'N/A')}\n"
            task_info += f"- 图像URLs: {len(image_urls)}"
            
            # 格式化使用信息
            usage = output.get('usage', {})
            usage_info = f"使用统计:\n"
            usage_info += f"- 生成图像数量: {usage.get('image_count', len(images_tensor))}\n"
            usage_info += f"- 成功下载: {len(images_tensor)}"
            
            # 添加提示词信息
            if results:
                first_result = results[0]
                if 'orig_prompt' in first_result:
                    usage_info += f"\n- 原始提示词: {first_result['orig_prompt'][:100]}..."
                if 'actual_prompt' in first_result:
                    usage_info += f"\n- 扩展提示词: {first_result['actual_prompt'][:100]}..."
            
            # 返回完整的响应JSON
            response_json = json.dumps(result, ensure_ascii=False, indent=2)
            
            print(f"[Qwen-Image] 图像生成完成")
            print(f"[Qwen-Image] {usage_info}")
            
            return (result_images, response_json, usage_info, task_info)
            
        except Exception as e:
            raise ValueError(f"结果处理失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "QwenImageText2Img": QwenImageText2ImgNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageText2Img": "Qwen-Image 文本生成图像"
}
