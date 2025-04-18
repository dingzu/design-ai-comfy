import requests
import json

class TranslateServiceNode:
    def __init__(self):
        self._base_url = "https://design-ai.staging.kuaishou.com"
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "from_lang": ("STRING", {"default": "en"}),
                "to_lang": ("STRING", {"default": "zh"}),
                "translate_type": ([
                    "mmu",
                    "yandex", 
                    "google"
                ], {"default": "yandex"}),
            },
            "optional": {
                "base_url": ("STRING", {
                    "default": "https://design-ai.staging.kuaishou.com",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("translated_text", "success", "raw_json")
    FUNCTION = "translate_text"
    CATEGORY = "✨✨✨design-ai/translate"

    def translate_text(self, text, from_lang, to_lang, translate_type, base_url=None):
        try:
            if not text:
                return ("No text provided", False, "{}")

            # 使用自定义 base_url 或默认值
            actual_base_url = base_url if base_url else self._base_url

            # 准备请求数据
            payload = {
                "word": text,
                "from": from_lang,
                "to": to_lang,
                "type": translate_type
            }

            # 发送翻译请求
            response = requests.post(
                f"{actual_base_url}/api/comfy/translate",
                json=payload,
                headers={"Content-Type": "application/json"},
                proxies={"http": None, "https": None}
            )
            
            # 检查响应
            data = response.json()
            # 将响应数据转换为格式化的 JSON 字符串
            raw_json = json.dumps(data, ensure_ascii=False, indent=2)
            
            if data["code"] == 1:
                return (data["word"], True, raw_json)
            else:
                error_msg = f"Translation failed: {data.get('errorMsg', 'Unknown error')}"
                print(error_msg)
                return (error_msg, False, raw_json)

        except Exception as e:
            error_msg = f"Translation request failed: {str(e)}"
            print(error_msg)
            return (error_msg, False, "{}") 