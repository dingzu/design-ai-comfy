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

class AzureOpenAIText2ImgNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "Azure OpenAI API密钥"
                }),
                "endpoint": ("STRING", {
                    "default": "https://xiaolvgongcheng-ee-openai-swedencentral.openai.azure.com/",
                    "tooltip": "Azure OpenAI 端点 URL"
                }),
                "deployment_name": ("STRING", {
                    "default": "xiaolvgongcheng-ee-openai-swedencentral-gpt-image-1",
                    "tooltip": "Azure OpenAI 部署名称（GPT Image 部署）"
                }),
                "api_version": ("STRING", {
                    "default": "2024-02-01",
                    "tooltip": "Azure OpenAI API 版本"
                }),
                "prompt": ("STRING", {
                    "default": "A beautiful sunset over mountains with vibrant colors",
                    "multiline": True,
                    "tooltip": "图像生成提示词"
                }),
                "image_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4,
                    "step": 1,
                    "tooltip": "生成图像数量"
                }),
                "image_size": (["1024x1024", "1024x1536", "1536x1024", "auto"], {
                    "default": "auto",
                    "tooltip": "输出图像尺寸"
                }),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "请求超时时间（秒）"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "response_json", "usage_info")
    FUNCTION = "generate_image"
    CATEGORY = "✨✨✨design-ai/api"

    def __init__(self):
        pass

    def generate_image(self, api_key, endpoint, deployment_name, api_version, prompt, 
                      image_count, image_size, timeout):
        """
        Azure OpenAI 文生图
        """
        # 用于调试的请求信息
        debug_info = {
            "url": "",
            "headers": {},
            "payload": {},
            "error": None,
            "response_status": None,
            "response_content": ""
        }
        
        try:
            # 验证必需参数
            if not api_key or api_key.strip() == "":
                debug_info["error"] = "API Key验证失败"
                print(f"[Azure OpenAI 文生图] 调试信息: {debug_info}")
                raise ValueError("API Key不能为空，请从Azure门户获取API密钥")
            
            if not endpoint or endpoint.strip() == "":
                debug_info["error"] = "端点验证失败"
                print(f"[Azure OpenAI 文生图] 调试信息: {debug_info}")
                raise ValueError("Azure OpenAI 端点不能为空")
            
            if not deployment_name or deployment_name.strip() == "":
                debug_info["error"] = "部署名称验证失败"
                print(f"[Azure OpenAI 文生图] 调试信息: {debug_info}")
                raise ValueError("部署名称不能为空")
            
            if not prompt or prompt.strip() == "":
                debug_info["error"] = "提示词验证失败"
                print(f"[Azure OpenAI 文生图] 调试信息: {debug_info}")
                raise ValueError("提示词不能为空")

            # 处理端点URL
            base_endpoint = endpoint.strip().rstrip('/')
            if not base_endpoint.startswith('http'):
                base_endpoint = f"https://{base_endpoint}"
            
            print(f"[Azure OpenAI 文生图] 使用尺寸: {image_size}")

            # 构建Azure OpenAI API URL
            url = f"{base_endpoint}/openai/deployments/{deployment_name}/images/generations?api-version={api_version}"
            debug_info["url"] = url
            
            # 构建请求载荷
            payload = {
                "prompt": prompt.strip(),
                "n": image_count,
                "size": image_size
            }
            debug_info["payload"] = payload
            
            # 设置请求头
            headers = {
                "api-key": api_key.strip(),
                "Content-Type": "application/json",
                "User-Agent": "ComfyUI-Azure-OpenAI-Text2Img/1.0"
            }
            debug_info["headers"] = {k: v if k != "api-key" else "***隐藏***" for k, v in headers.items()}
            
            print(f"[Azure OpenAI 文生图] 发送请求到: {url}")
            print(f"[Azure OpenAI 文生图] 请求参数:")
            print(f"  - deployment: {deployment_name}")
            print(f"  - api_version: {api_version}")
            print(f"  - prompt: {prompt.strip()}")
            print(f"  - n: {image_count}")
            print(f"  - size: {image_size}")
            
            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            debug_info["response_status"] = response.status_code
            print(f"[Azure OpenAI 文生图] 响应状态码: {response.status_code}")
            
            # 解析响应
            try:
                response_data = response.json()
                debug_info["response_content"] = json.dumps(response_data, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # 如果JSON解析失败，显示原始响应内容以便调试
                response_text = response.text if response.text else "空响应"
                debug_info["response_content"] = response_text
                debug_info["error"] = f"JSON解析失败，状态码: {response.status_code}"
                
                print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
                print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 文生图] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 文生图] 响应内容: {response_text}")
                print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 文生图] ==================")
                
                if response.status_code == 404:
                    raise ValueError(f"API端点不存在 (404): {url}\n响应内容: {response_text}\n\n💡 建议: \n1. 检查Azure OpenAI端点是否正确\n2. 确认部署名称是否正确\n3. 确认API版本是否支持图像生成功能")
                elif response.status_code == 401:
                    raise ValueError(f"认证失败 (401): {response_text}\n\n💡 建议: \n1. 检查API密钥是否正确\n2. 确认API密钥是否有权限访问此部署")
                else:
                    raise ValueError(f"无效的JSON响应 (状态码: {response.status_code}): {response_text}")
            
            # 检查响应状态
            if not response.ok:
                error_msg = response_data.get('error', {}).get('message', '未知错误')
                error_type = response_data.get('error', {}).get('type', 'unknown_error')
                error_code = response_data.get('error', {}).get('code', 'unknown')
                
                debug_info["error"] = f"API错误 [{error_code}]: {error_msg} (类型: {error_type})"
                
                print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
                print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 文生图] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 文生图] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 文生图] ==================")
                
                # 提供详细的错误信息和解决建议
                if 'content policy' in error_msg.lower():
                    error_msg += "\n\n💡 建议: 提示词违反了内容政策"
                    error_msg += "\n  - 请使用更加中性和安全的提示词"
                    error_msg += "\n  - 避免包含暴力、色情或其他敏感内容"
                elif 'invalid prompt' in error_msg.lower():
                    error_msg += "\n\n💡 建议: 提示词格式不正确"
                    error_msg += "\n  - 确保提示词是有效的文本"
                    error_msg += "\n  - 提示词长度不要超过限制"
                elif response.status_code == 401:
                    error_msg += "\n\n💡 建议: 检查API密钥是否有效，从Azure门户获取正确的API密钥"
                elif response.status_code == 429:
                    error_msg += "\n\n💡 建议: 请求频率过高，请稍后重试"
                elif response.status_code == 403:
                    error_msg += "\n\n💡 建议: 权限不足，检查API密钥的权限和部署访问权限"
                
                raise ValueError(f"API错误 [{error_code}]: {error_msg}")
            
            # 处理生成的图像
            images_tensor = []
            image_data_list = response_data.get('data', [])
            
            if not image_data_list:
                debug_info["error"] = "响应中没有图像数据"
                print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
                print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 文生图] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 文生图] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 文生图] ==================")
                raise ValueError("响应中没有图像数据")
            
            print(f"[Azure OpenAI 文生图] 成功生成 {len(image_data_list)} 张图像")
            
            for idx, item in enumerate(image_data_list):
                if 'b64_json' in item:
                    # 处理 base64 编码的图像
                    b64_data = item['b64_json']
                    image_bytes = base64.b64decode(b64_data)
                    result_image = Image.open(io.BytesIO(image_bytes))
                    
                    # 转换为RGB（如果不是的话）
                    if result_image.mode != 'RGB':
                        result_image = result_image.convert('RGB')
                    
                    # 转换为tensor
                    image_np = np.array(result_image).astype(np.float32) / 255.0
                    image_tensor = torch.from_numpy(image_np)[None,]
                    images_tensor.append(image_tensor)
                    
                    print(f"[Azure OpenAI 文生图] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                    
                elif 'url' in item:
                    # 处理URL形式的图像
                    print(f"[Azure OpenAI 文生图] 收到图像URL: {item['url']}")
                    try:
                        # 下载URL图像
                        img_response = requests.get(item['url'], timeout=30)
                        if img_response.ok:
                            result_image = Image.open(io.BytesIO(img_response.content))
                            
                            # 转换为RGB（如果不是的话）
                            if result_image.mode != 'RGB':
                                result_image = result_image.convert('RGB')
                            
                            # 转换为tensor
                            image_np = np.array(result_image).astype(np.float32) / 255.0
                            image_tensor = torch.from_numpy(image_np)[None,]
                            images_tensor.append(image_tensor)
                            
                            print(f"[Azure OpenAI 文生图] 图像 {idx + 1}: {result_image.size}, 模式: {result_image.mode}")
                        else:
                            print(f"[Azure OpenAI 文生图] 下载图像失败: {img_response.status_code}")
                    except Exception as e:
                        print(f"[Azure OpenAI 文生图] 处理URL图像失败: {str(e)}")
            
            if not images_tensor:
                debug_info["error"] = "没有可用的图像数据"
                print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
                print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
                print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
                print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
                print(f"[Azure OpenAI 文生图] 响应状态码: {debug_info['response_status']}")
                print(f"[Azure OpenAI 文生图] 响应内容: {debug_info['response_content']}")
                print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
                print(f"[Azure OpenAI 文生图] ==================")
                raise ValueError("没有可用的图像数据")
            
            # 合并所有图像
            result_images = torch.cat(images_tensor, dim=0)
            
            # 格式化使用信息
            usage_info = f"Azure OpenAI 文生图使用情况:\n"
            usage_info += f"- 端点: {base_endpoint}\n"
            usage_info += f"- 部署: {deployment_name}\n"
            usage_info += f"- API版本: {api_version}\n"
            usage_info += f"- 生成图像数量: {len(images_tensor)}\n"
            usage_info += f"- 图像尺寸: {image_size}\n"
            usage_info += f"- 提示词: {prompt.strip()}"
            
            # 返回完整的响应JSON
            response_json = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            print(f"[Azure OpenAI 文生图] 图像生成完成")
            print(f"[Azure OpenAI 文生图] {usage_info}")
            
            return (result_images, response_json, usage_info)
            
        except requests.exceptions.Timeout:
            debug_info["error"] = f"请求超时（{timeout}秒）"
            print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
            print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 文生图] ==================")
            raise ValueError(f"请求超时（{timeout}秒）。图像生成可能需要较长时间，建议增加超时时间。")
        except requests.exceptions.ConnectionError:
            debug_info["error"] = "网络连接错误"
            print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
            print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 文生图] ==================")
            raise ValueError(f"网络连接错误。请检查:\n1. 网络连接\n2. Azure OpenAI端点地址是否可访问\n3. 防火墙设置")
        except requests.exceptions.RequestException as e:
            debug_info["error"] = f"请求异常: {str(e)}"
            print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
            print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
            print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 文生图] ==================")
            raise ValueError(f"请求失败: {str(e)}")
        except Exception as e:
            debug_info["error"] = f"未知异常: {str(e)}"
            print(f"[Azure OpenAI 文生图] === 详细调试信息 ===")
            print(f"[Azure OpenAI 文生图] 请求URL: {debug_info['url']}")
            print(f"[Azure OpenAI 文生图] 请求头: {debug_info['headers']}")
            print(f"[Azure OpenAI 文生图] 请求载荷: {json.dumps(debug_info['payload'], ensure_ascii=False, indent=2)}")
            if debug_info["response_status"]:
                print(f"[Azure OpenAI 文生图] 响应状态码: {debug_info['response_status']}")
            if debug_info["response_content"]:
                print(f"[Azure OpenAI 文生图] 响应内容: {debug_info['response_content']}")
            print(f"[Azure OpenAI 文生图] 错误: {debug_info['error']}")
            print(f"[Azure OpenAI 文生图] ==================")
            raise ValueError(f"图像生成失败: {str(e)}")

# 节点映射
NODE_CLASS_MAPPINGS = {
    "AzureOpenAIText2Img": AzureOpenAIText2ImgNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AzureOpenAIText2Img": "Azure OpenAI 文生图"
}
