import requests
import json
import re
from typing import Dict, Any, Optional, List

class WanqingBboxDetectorNode:
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
                "img_url": ("STRING", {
                    "default": "https://cdnfile.corp.kuaishou.com/kc/files/a/design-ai/poify/0e3647a314c75e16810a24704.jpg",
                    "tooltip": "图片的URL地址"
                }),
                "target": ("STRING", {
                    "default": "text",
                    "tooltip": "检测目标类型"
                }),
                "timeout": ("FLOAT", {
                    "default": 60.0,
                    "min": 10.0,
                    "max": 300.0,
                    "step": 5.0,
                    "tooltip": "API请求超时时间(秒)"
                }),
                "use_proxy": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否使用代理服务器"
                }),
            },
            "optional": {
                "end_user_id": ("STRING", {
                    "default": "wangyihan",
                    "tooltip": "X-WQ-End-User-ID 请求头"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING", "BBOXES", "STRING")
    RETURN_NAMES = ("response", "success", "message", "api_endpoint", "bboxes", "bboxes_string")
    FUNCTION = "detect_bbox"
    CATEGORY = "✨✨✨design-ai/api"

    def build_request_payload(self, model: str, img_url: str, target: str) -> Dict[str, Any]:
        """构建API请求的payload"""
        payload = {
            "model": model,
            "inputs": [
                {
                    "variable": "img_url",
                    "type": "file",
                    "data": {
                        "file_type": "image",
                        "transfer_method": "remote_url",
                        "url": img_url
                    }
                },
                {
                    "variable": "target",
                    "type": "text-input",
                    "data": target
                }
            ],
            "stream": False
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

    def clean_json_response(self, content: str) -> str:
        """清理响应中的markdown格式，提取纯JSON数据"""
        if not content:
            return content
            
        # 移除markdown代码块格式
        # 匹配 ```json...``` 或 ```...``` 格式
        pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            # 提取代码块内容
            json_content = match.group(1).strip()
            return json_content
        
        # 如果没有找到代码块，尝试查找JSON对象
        # 查找以 { 开始，以 } 结束的内容
        json_pattern = r'\{.*?\}'
        json_match = re.search(json_pattern, content, re.DOTALL)
        
        if json_match:
            return json_match.group(0)
            
        # 如果都没找到，返回原内容
        return content

    def extract_bboxes(self, content: str) -> List[List[List[int]]]:
        """从响应内容中提取bbox数据，转换为三层方括号格式"""
        try:
            # 尝试解析JSON
            data = json.loads(content)
            
            # 查找bbox_2d字段
            if isinstance(data, dict) and 'bbox_2d' in data:
                bbox = data['bbox_2d']
                # 确保bbox是4个数字的列表
                if isinstance(bbox, list) and len(bbox) == 4:
                    # 转换为三层方括号格式: [[[x1, y1, x2, y2]]]
                    return [[[int(x) for x in bbox]]]
                    
            # 如果没有找到有效的bbox，返回空的三层结构
            return [[[]]]
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"提取bbox时出错: {e}")
            # 返回空的三层结构
            return [[[]]]

    def process_response(self, response_data: Dict[str, Any]) -> tuple:
        """处理API响应"""
        try:
            # 提取响应内容，根据实际API响应结构调整
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                # 清理markdown格式
                cleaned_content = self.clean_json_response(content)
                # 提取bbox数据
                bboxes = self.extract_bboxes(cleaned_content)
                return cleaned_content, "API调用成功", bboxes
            elif 'data' in response_data:
                # 如果响应格式不同，可以根据实际情况调整
                content = json.dumps(response_data['data'], ensure_ascii=False, indent=2)
                cleaned_content = self.clean_json_response(content)
                bboxes = self.extract_bboxes(cleaned_content)
                return cleaned_content, "API调用成功", bboxes
            elif 'result' in response_data:
                content = json.dumps(response_data['result'], ensure_ascii=False, indent=2)
                cleaned_content = self.clean_json_response(content)
                bboxes = self.extract_bboxes(cleaned_content)
                return cleaned_content, "API调用成功", bboxes
            else:
                # 如果结构未知，返回完整响应
                content = json.dumps(response_data, ensure_ascii=False, indent=2)
                cleaned_content = self.clean_json_response(content)
                bboxes = self.extract_bboxes(cleaned_content)
                return cleaned_content, "API调用成功，返回完整响应", bboxes
                
        except Exception as e:
            error_msg = f"响应处理错误: {str(e)}"
            return "", error_msg, [[[]]]

    def detect_bbox(self, api_url: str, token: str, model: str, img_url: str, target: str, 
                   timeout: float, use_proxy: bool, end_user_id: Optional[str] = "wangyihan"):
        
        # 参数验证
        if not api_url.strip():
            return ("", False, "API URL是必需的", "", [[[]]], "")
        
        if not token.strip():
            return ("", False, "Token是必需的", "", [[[]]], "")
        
        if not model.strip():
            return ("", False, "Model是必需的", "", [[[]]], "")
            
        if not img_url.strip():
            return ("", False, "图片URL是必需的", "", [[[]]], "")
            
        if not target.strip():
            return ("", False, "Target是必需的", "", [[[]]], "")

        try:
            # 构建请求payload
            payload = self.build_request_payload(model, img_url, target)
            
            # 构建请求头
            headers = self.build_headers(token, end_user_id or "wangyihan")
            
            # 配置代理
            request_kwargs = {
                "headers": headers,
                "data": json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                "timeout": timeout
            }
            if use_proxy:
                request_kwargs["proxies"] = {"http": None, "https": None}
            
            print(f"发送bbox检测请求...")
            print(f"API地址: {api_url}")
            print(f"模型: {model}")
            print(f"图片URL: {img_url}")
            print(f"检测目标: {target}")
            
            # 发送请求 - 修复UTF-8编码问题
            response = requests.post(api_url, **request_kwargs)

            if response.status_code != 200:
                error_msg = f"请求失败，状态码 {response.status_code}: {response.text}"
                print(error_msg)
                return ("", False, error_msg, api_url, [[[]]], "")

            # 处理响应
            try:
                response_data = response.json()
                content, message, bboxes = self.process_response(response_data)
                success_msg = f"bbox检测完成! 模型: {model}, 目标: {target}"
                print(success_msg)
                print(f"提取到的bbox: {bboxes}")
                bboxes_string = str(bboxes)
                return (content, True, success_msg, api_url, bboxes, bboxes_string)
                
            except json.JSONDecodeError as e:
                error_msg = f"响应JSON解析失败: {str(e)}"
                print(error_msg)
                return ("", False, error_msg, api_url, [[[]]], "")
            
        except requests.RequestException as e:
            error_msg = f"请求错误: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, api_url, [[[]]], "")
        except Exception as e:
            error_msg = f"意外错误: {str(e)}"
            print(error_msg)
            return ("", False, error_msg, api_url, [[[]]], "") 