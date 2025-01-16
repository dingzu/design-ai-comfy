from openai import OpenAI

class OpenAIVisionNode:
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
                "base64_image": ("STRING",),
                "prompt": ("STRING", {
                    "default": "What is in this image?", 
                    "multiline": True
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 1,
                    "max": 300,
                    "step": 1
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("output_text", "success")
    FUNCTION = "analyze_image"
    CATEGORY = "✨✨✨design-ai/llm"

    def _get_client(self, api_key: str, api_base: str, timeout: int) -> OpenAI:
        """简单的客户端缓存"""
        cache_key = f"{api_key}:{api_base}:{timeout}"
        if cache_key not in self._clients:
            self._clients[cache_key] = OpenAI(api_key=api_key, base_url=api_base, timeout=timeout)
        return self._clients[cache_key]

    def analyze_image(self, api_key, api_base, model, base64_image, prompt, temperature, timeout):
        try:
            # 检查base64输入
            if not base64_image:
                return ("No base64 image provided", False)

            # 获取缓存的客户端实例
            client = self._get_client(api_key, api_base, timeout)

            # 发送请求
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=temperature,
                max_tokens=500,
                timeout=timeout
            )
            
            return (response.choices[0].message.content, True)

        except Exception as e:
            error_msg = f"Failed to analyze image: {str(e)}"
            print(error_msg)
            return (error_msg, False)