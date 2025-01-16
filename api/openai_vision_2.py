from openai import OpenAI

class OpenAIVision2Node:
    def __init__(self):
        self._clients = {}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "api_base": ("STRING", {"default": "https://openai.nengyongai.cn/v1"}),
                "model": ([
                    "gpt-4-vision-preview",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "claude-3-5-sonnet-20240620",
                    "o1-mini"
                ], {"default": "claude-3-5-sonnet-20240620"}),
                "base64_image1": ("STRING",),
                "base64_image2": ("STRING",),
                "prompt": ("STRING", {
                    "default": "Compare these two images. What are the differences?", 
                    "multiline": True
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
                "timeout": ([
                    "30s (默认)",
                    "60s (1分钟)",
                    "120s (2分钟)", 
                    "300s (5分钟)"
                ], {
                    "default": "30s (默认)"
                }),
            },
            "optional": {
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("output_text", "success")
    FUNCTION = "analyze_images"
    CATEGORY = "✨✨✨design-ai/llm"

    def _get_client(self, api_key: str, api_base: str, timeout: int) -> OpenAI:
        """简单的客户端缓存"""
        cache_key = f"{api_key}:{api_base}:{timeout}"
        if cache_key not in self._clients:
            self._clients[cache_key] = OpenAI(api_key=api_key, base_url=api_base, timeout=timeout)
        return self._clients[cache_key]

    def analyze_images(self, api_key, api_base, model, base64_image1, prompt, temperature, timeout, base64_image2=None):
        try:
            # 检查第一张图片
            if not base64_image1:
                return ("No first image provided", False)

            # 解析超时时间
            timeout_seconds = int(timeout.split('s')[0])

            # 准备消息内容
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image1}"
                    }
                }
            ]

            # 如果提供了第二张图片，添加到消息中
            if base64_image2:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image2}"
                    }
                })

            # 获取缓存的客户端实例
            client = self._get_client(api_key, api_base, timeout_seconds)

            # 发送请求
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=temperature,
                max_tokens=500,
                timeout=timeout_seconds
            )
            
            return (response.choices[0].message.content, True)

        except Exception as e:
            error_msg = f"Failed to analyze images: {str(e)}"
            print(error_msg)
            return (error_msg, False)