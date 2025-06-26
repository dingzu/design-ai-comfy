import torch
import numpy as np
import requests
import time
import json
from typing import List, Dict, Any, Optional

class GPTThirdPartyAPINode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_url": ("STRING", {
                    "default": "https://your-platform.com",
                    "tooltip": "第三方平台的Base URL，例如: https://your-platform.com"
                }),
                "api_key": ("STRING", {
                    "default": "sk-xxxxxxx",
                    "tooltip": "API密钥，将用于Bearer Token认证"
                }),
                "model": ("STRING", {
                    "default": "flux",
                    "tooltip": "要使用的模型ID"
                }),
                "messages": ("STRING", {
                    "default": '[{"role": "user", "content": "画个 AI 网站的 icon"}]',
                    "multiline": True,
                    "tooltip": "聊天消息列表，JSON格式，例如: [{'role': 'user', 'content': '你好'}]"
                }),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "采样温度，0-2之间，值越高输出越随机"
                }),
                "max_tokens": ("INT", {
                    "default": 4096,
                    "min": 1,
                    "max": 32768,
                    "step": 1,
                    "tooltip": "生成的最大token数量"
                }),
                "stream": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用流式输出"
                }),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "API请求超时时间(秒)"
                }),
            },
            "optional": {
                "top_p": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "核采样，0-1之间"
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "生成的回复数量"
                }),
                "stop": ("STRING", {
                    "default": "",
                    "tooltip": "停止序列，逗号分隔多个序列"
                }),
                "presence_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "存在惩罚，-2.0到2.0之间"
                }),
                "frequency_penalty": ("FLOAT", {
                    "default": 0.0,
                    "min": -2.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "频率惩罚，-2.0到2.0之间"
                }),
                "user": ("STRING", {
                    "default": "",
                    "tooltip": "用户标识符"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("response", "success", "message", "request_id", "api_endpoint", "prompt_tokens", "completion_tokens", "total_tokens")
    FUNCTION = "process_chat_request"
    CATEGORY = "✨✨✨design-ai/api"

    def parse_messages(self, messages_str: str) -> List[Dict[str, str]]:
        """Parse messages string to list of message dictionaries"""
        try:
            messages = json.loads(messages_str)
            if not isinstance(messages, list):
                raise ValueError("Messages must be a list")
            
            for msg in messages:
                if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                    raise ValueError("Each message must have 'role' and 'content' fields")
                    
            return messages
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def build_endpoint_url(self, base_url: str) -> str:
        """Build the Chat API endpoint URL"""
        base_url = base_url.rstrip('/')
        return f"{base_url}/v1/chat/completions"

    def build_request_payload(self, model: str, messages: List[Dict[str, str]], 
                            temperature: float, max_tokens: int, stream: bool,
                            top_p: Optional[float] = None, n: Optional[int] = None,
                            stop: Optional[str] = None, presence_penalty: Optional[float] = None,
                            frequency_penalty: Optional[float] = None, user: Optional[str] = None) -> Dict[str, Any]:
        """Build the request payload for Chat API"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # Add optional parameters if provided
        if top_p is not None and top_p != 1.0:
            payload["top_p"] = top_p
        
        if n is not None and n != 1:
            payload["n"] = n
            
        if stop and stop.strip():
            # Split by comma and clean up
            stop_sequences = [s.strip() for s in stop.split(',') if s.strip()]
            if len(stop_sequences) == 1:
                payload["stop"] = stop_sequences[0]
            elif len(stop_sequences) > 1:
                payload["stop"] = stop_sequences[:4]  # Max 4 sequences
                
        if presence_penalty is not None and presence_penalty != 0.0:
            payload["presence_penalty"] = presence_penalty
            
        if frequency_penalty is not None and frequency_penalty != 0.0:
            payload["frequency_penalty"] = frequency_penalty
            
        if user and user.strip():
            payload["user"] = user
            
        return payload

    def process_streaming_response(self, response) -> tuple:
        """Process streaming response from Chat API"""
        full_content = ""
        request_id = ""
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        if data_str.strip() == '[DONE]':
                            break
                            
                        try:
                            data = json.loads(data_str)
                            if not request_id:
                                request_id = data.get('id', '')
                                
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
            return full_content, request_id, 0, 0, 0  # Streaming doesn't provide token counts
            
        except Exception as e:
            raise Exception(f"Error processing streaming response: {e}")

    def process_non_streaming_response(self, response_data: Dict[str, Any]) -> tuple:
        """Process non-streaming response from Chat API"""
        request_id = response_data.get('id', '')
        choices = response_data.get('choices', [])
        usage = response_data.get('usage', {})
        
        if not choices:
            raise Exception("No choices in response")
            
        # Get the first choice's message content
        message = choices[0].get('message', {})
        content = message.get('content', '')
        
        # Extract token usage
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        return content, request_id, prompt_tokens, completion_tokens, total_tokens

    def process_chat_request(self, base_url: str, api_key: str, model: str, messages: str,
                           temperature: float, max_tokens: int, stream: bool, timeout: float,
                           top_p: Optional[float] = None, n: Optional[int] = None,
                           stop: Optional[str] = None, presence_penalty: Optional[float] = None,
                           frequency_penalty: Optional[float] = None, user: Optional[str] = None):
        
        # Validation
        if not base_url.strip():
            return ("", False, "Base URL is required", "", "", 0, 0, 0)
        
        if not api_key.strip():
            return ("", False, "API key is required", "", "", 0, 0, 0)
        
        if not model.strip():
            return ("", False, "Model is required", "", "", 0, 0, 0)
        
        if not messages.strip():
            return ("", False, "Messages are required", "", "", 0, 0, 0)

        try:
            # Parse messages
            parsed_messages = self.parse_messages(messages)
            
            # Build API endpoint
            endpoint = self.build_endpoint_url(base_url)
            
            # Build request payload
            payload = self.build_request_payload(
                model, parsed_messages, temperature, max_tokens, stream,
                top_p, n, stop, presence_penalty, frequency_penalty, user
            )
            
            # Setup headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }

            print(f"Sending chat request to third-party GPT API...")
            print(f"Endpoint: {endpoint}")
            print(f"Model: {model}")
            print(f"Messages: {len(parsed_messages)} message(s)")
            print(f"Stream: {stream}")
            
            # Make the request
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=timeout,
                stream=stream
            )

            if response.status_code != 200:
                error_msg = f"Request failed with status {response.status_code}: {response.text}"
                print(error_msg)
                return ("", False, error_msg, "", endpoint, 0, 0, 0)

            # Process response based on stream mode
            if stream:
                try:
                    content, request_id, prompt_tokens, completion_tokens, total_tokens = self.process_streaming_response(response)
                    success_msg = f"Chat completed successfully with streaming! Model: {model}"
                    print(success_msg)
                    return (content, True, success_msg, request_id, endpoint, prompt_tokens, completion_tokens, total_tokens)
                except Exception as e:
                    error_msg = f"Streaming error: {str(e)}"
                    print(error_msg)
                    return ("", False, error_msg, "", endpoint, 0, 0, 0)
            else:
                try:
                    response_data = response.json()
                    content, request_id, prompt_tokens, completion_tokens, total_tokens = self.process_non_streaming_response(response_data)
                    success_msg = f"Chat completed successfully! Model: {model}, Tokens: {total_tokens}"
                    print(success_msg)
                    return (content, True, success_msg, request_id, endpoint, prompt_tokens, completion_tokens, total_tokens)
                except Exception as e:
                    error_msg = f"Response processing error: {str(e)}"
                    print(error_msg)
                    return ("", False, error_msg, "", endpoint, 0, 0, 0)
            
        except ValueError as e:
            error_msg = f"Validation error: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, "", "", 0, 0, 0)
        except requests.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, "", "", 0, 0, 0)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, "", "", 0, 0, 0) 