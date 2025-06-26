import requests
import json

class PPInfraGPTNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "model_preset": ([
                    "gpt-4.1",
                    "gpt-4.1-nano", 
                    "gpt-4.1-mini",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "claude-opus-4-20250514",
                    "claude-sonnet-4-20250514", 
                    "claude-3-7-sonnet-20250219",
                    "custom"
                ], {"default": "gpt-4o"}),
                "custom_model": ("STRING", {
                    "default": "",
                    "tooltip": "仅当选择 'custom' 时使用"
                }),
                "system_prompt": ("STRING", {
                    "default": "您是一个专业的 AI 文档助手。", 
                    "multiline": True
                }),
                "user_prompt": ("STRING", {
                    "default": "", 
                    "multiline": True
                }),
                "max_tokens": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 4096,
                    "step": 1
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("output_text", "success", "model_used")
    FUNCTION = "generate_text"
    CATEGORY = "✨✨✨design-ai/llm"

    def get_model_mapping(self, model_preset):
        """获取预设模型对应的API参数"""
        model_map = {
            "gpt-4.1": "pa/gt-4.1",
            "gpt-4.1-nano": "pa/gt-4.1-n", 
            "gpt-4.1-mini": "pa/gt-4.1-m",
            "gpt-4o": "pa/gt-4p",
            "gpt-4o-mini": "pa/gt-4p-m",
            "claude-opus-4-20250514": "pa/cd-op-4-20250514",
            "claude-sonnet-4-20250514": "pa/cd-st-4-20250514",
            "claude-3-7-sonnet-20250219": "pa/cd-3-7-st-20250219"
        }
        return model_map.get(model_preset, model_preset)

    def generate_text(self, api_key, model_preset, custom_model, system_prompt, user_prompt, max_tokens, temperature):
        try:
            # 确定使用的模型
            if model_preset == "custom" and custom_model.strip():
                model_to_use = custom_model.strip()
            elif model_preset == "custom" and not custom_model.strip():
                # 如果选择custom但没有输入，使用默认模型
                model_to_use = self.get_model_mapping("gpt-4o")
            else:
                model_to_use = self.get_model_mapping(model_preset)

            # 构建请求数据
            payload = {
                "model": model_to_use,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # 发送API请求
            response = requests.post(
                "https://api.ppinfra.com/v3/openai/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                output_text = result["choices"][0]["message"]["content"]
                return (output_text, True, model_to_use)
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                return (error_msg, False, model_to_use)
                
        except requests.exceptions.Timeout:
            return ("请求超时，请稍后重试", False, "timeout")
        except requests.exceptions.RequestException as e:
            return (f"网络请求错误: {str(e)}", False, "error")
        except KeyError as e:
            return (f"API响应格式错误: {str(e)}", False, "error")
        except Exception as e:
            return (f"未知错误: {str(e)}", False, "error") 