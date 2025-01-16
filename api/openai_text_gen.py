# nodes/openai_text_gen_node.py
from openai import OpenAI

class OpenAITextGenNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "api_base": ("STRING", {"default": "https://openai.nengyongai.cn/v1"}),
                "model": ([
                    "gpt-3.5-turbo",   
                    "gpt-4",           
                    "gpt-4o",          
                    "gpt-4o-mini",     
                    "claude-3-5-sonnet-20240620",  
                    "o1-mini"     
                ], {"default": "gpt-3.5-turbo"}),
                "system_prompt": ("STRING", {
                    "default": "You are a helpful assistant.", 
                    "multiline": True
                }),
                "input_text": ("STRING", {
                    "default": "", 
                    "multiline": True
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("output_text", "success")
    FUNCTION = "generate_text"
    CATEGORY = "✨✨✨design-ai/llm"

    def generate_text(self, api_key, api_base, model, system_prompt, input_text, temperature):
        try:
            client = OpenAI(api_key=api_key, base_url=api_base)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_text}
                ],
                temperature=temperature
            )
            return (response.choices[0].message.content, True)
        except:
            return ("Failed to generate text.", False)