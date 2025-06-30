import requests
import json
import re
from typing import Dict, Any, Optional

class WanqingFlexibleAPINode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_url": ("STRING", {
                    "default": "https://wanqing-api.corp.kuaishou.com/api/llm/workflow/v1/chat/completions",
                    "tooltip": "API请求的目标地址"
                }),
                "token": ("STRING", {
                    "default": "",
                    "tooltip": "用于认证的Bearer Token"
                }),
                "model": ("STRING", {
                    "default": "app-lrn12c-1750994696171776386",
                    "tooltip": "要使用的模型ID"
                }),
                "inputs": ("STRING", {
                    "default": '''[
  {
    "variable": "img_url",
    "type": "file",
    "data": {
      "file_type": "image",
      "transfer_method": "remote_url",
      "url": "https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0e3647a314c75e16810a24704.jpg"
    }
  },
  {
    "variable": "target",
    "type": "text-input",
    "data": "text"
  }
]''',
                    "multiline": True,
                    "tooltip": "JSON格式的inputs参数，可以自由定义多个变量"
                }),
                "timeout": ("FLOAT", {
                    "default": 60.0,
                    "min": 10.0,
                    "max": 300.0,
                    "step": 5.0,
                    "tooltip": "API请求超时时间(秒)"
                }),
            },
            "optional": {
                "end_user_id": ("STRING", {
                    "default": "wangyihan",
                    "tooltip": "X-WQ-End-User-ID 请求头"
                }),
                "stream": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用流式输出"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "success", "message", "api_endpoint", "raw_response")
    FUNCTION = "call_wanqing_api"
    CATEGORY = "✨✨✨design-ai/api"

    def parse_inputs(self, inputs_str: str) -> list:
        """解析inputs JSON字符串"""
        try:
            inputs = json.loads(inputs_str)
            if not isinstance(inputs, list):
                raise ValueError("inputs必须是一个数组")
            
            # 验证每个input的基本结构
            for input_item in inputs:
                if not isinstance(input_item, dict):
                    raise ValueError("每个input必须是一个对象")
                if 'variable' not in input_item or 'type' not in input_item or 'data' not in input_item:
                    raise ValueError("每个input必须包含variable、type和data字段")
                    
            return inputs
        except json.JSONDecodeError as e:
            raise ValueError(f"inputs JSON格式错误: {e}")

    def build_request_payload(self, model: str, inputs: list, stream: bool) -> Dict[str, Any]:
        """构建API请求的payload"""
        payload = {
            "model": model,
            "inputs": inputs,
            "stream": stream
        }
        return payload

    def build_headers(self, token: str, end_user_id: str) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-WQ-End-User-ID': end_user_id,
            'X-WQ-Message-Channel': 'api'
        }
        return headers

    def clean_markdown_response(self, content: str) -> str:
        """清理响应中的markdown格式，提取纯内容"""
        if not content:
            return content
            
        # 移除markdown代码块格式
        # 匹配 ```json...``` 或 ```...``` 格式
        pattern = r'```(?:json|xml|html|javascript|python|yaml)?\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            # 提取代码块内容
            cleaned_content = match.group(1).strip()
            return cleaned_content
            
        # 如果没有找到代码块，返回原内容
        return content

    def process_response(self, response_data: Dict[str, Any]) -> tuple:
        """处理API响应"""
        try:
            # 原始响应
            raw_response = json.dumps(response_data, ensure_ascii=False, indent=2)
            
            # 提取响应内容，根据实际API响应结构调整
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                # 清理markdown格式
                cleaned_content = self.clean_markdown_response(content)
                return cleaned_content, "API调用成功", raw_response
            elif 'data' in response_data:
                # 如果响应格式不同，可以根据实际情况调整
                content = json.dumps(response_data['data'], ensure_ascii=False, indent=2)
                cleaned_content = self.clean_markdown_response(content)
                return cleaned_content, "API调用成功", raw_response
            elif 'result' in response_data:
                content = json.dumps(response_data['result'], ensure_ascii=False, indent=2)
                cleaned_content = self.clean_markdown_response(content)
                return cleaned_content, "API调用成功", raw_response
            else:
                # 如果结构未知，返回完整响应
                content = json.dumps(response_data, ensure_ascii=False, indent=2)
                cleaned_content = self.clean_markdown_response(content)
                return cleaned_content, "API调用成功，返回完整响应", raw_response
                
        except Exception as e:
            error_msg = f"响应处理错误: {str(e)}"
            return "", error_msg, ""

    def call_wanqing_api(self, api_url: str, token: str, model: str, inputs: str, 
                        timeout: float, end_user_id: Optional[str] = "wangyihan", 
                        stream: Optional[bool] = False):
        
        # 参数验证
        if not api_url.strip():
            return ("", False, "API URL是必需的", "", "")
        
        if not token.strip():
            return ("", False, "Token是必需的", "", "")
        
        if not model.strip():
            return ("", False, "Model是必需的", "", "")
            
        if not inputs.strip():
            return ("", False, "inputs是必需的", "", "")

        try:
            # 解析inputs
            parsed_inputs = self.parse_inputs(inputs)
            
            # 构建请求payload
            payload = self.build_request_payload(model, parsed_inputs, stream)
            
            # 构建请求头
            headers = self.build_headers(token, end_user_id or "wangyihan")
            
            print(f"发送万擎API请求...")
            print(f"API地址: {api_url}")
            print(f"模型: {model}")
            print(f"Inputs数量: {len(parsed_inputs)}")
            print(f"流式输出: {stream}")
            
            # 发送请求 - 使用UTF-8编码
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                timeout=timeout,
                stream=stream
            )

            if response.status_code != 200:
                error_msg = f"请求失败，状态码 {response.status_code}: {response.text}"
                print(error_msg)
                return ("", False, error_msg, api_url, "")

            # 处理响应
            if stream:
                # 处理流式响应
                try:
                    full_content = ""
                    raw_chunks = []
                    
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            raw_chunks.append(line_str)
                            
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                
                                if data_str.strip() == '[DONE]':
                                    break
                                    
                                try:
                                    data = json.loads(data_str)
                                    choices = data.get('choices', [])
                                    if choices and 'delta' in choices[0]:
                                        delta = choices[0]['delta']
                                        if 'content' in delta:
                                            content = delta['content']
                                            full_content += content
                                            print(content, end='', flush=True)
                                except json.JSONDecodeError:
                                    continue
                                    
                    print()  # New line after streaming
                    
                    cleaned_content = self.clean_markdown_response(full_content)
                    raw_response = '\n'.join(raw_chunks)
                    success_msg = f"万擎API流式调用完成! 模型: {model}"
                    print(success_msg)
                    return (cleaned_content, True, success_msg, api_url, raw_response)
                    
                except Exception as e:
                    error_msg = f"流式响应处理错误: {str(e)}"
                    print(error_msg)
                    return ("", False, error_msg, api_url, "")
            else:
                # 处理非流式响应
                try:
                    response_data = response.json()
                    content, message, raw_response = self.process_response(response_data)
                    success_msg = f"万擎API调用完成! 模型: {model}"
                    print(success_msg)
                    return (content, True, success_msg, api_url, raw_response)
                    
                except json.JSONDecodeError as e:
                    error_msg = f"响应JSON解析失败: {str(e)}"
                    print(error_msg)
                    return ("", False, error_msg, api_url, "")
            
        except ValueError as e:
            error_msg = f"参数验证错误: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, "", "")
        except requests.RequestException as e:
            error_msg = f"请求错误: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, api_url, "")
        except Exception as e:
            error_msg = f"意外错误: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, api_url, "") 