import os

class TextFileReader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING",),  # 本地文件路径
                "key": ("STRING",),  # 要查找的键
            },
        }

    RETURN_NAMES = ("value",)
    RETURN_TYPES = ("STRING",)
    FUNCTION = "read_text_file"
    CATEGORY = "✨✨✨design-ai/io"

    def read_text_file(self, file_path, key):
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return (f"Error: File not found at {file_path}",)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
            
            # 查找指定键的值
            for line in content:
                line = line.strip()
                if ':' in line:
                    current_key, value = line.split(':', 1)
                    current_key = current_key.strip()
                    value = value.strip()
                    if current_key == key:
                        return (value,)
            
            return (f"Key '{key}' not found in file",)
            
        except Exception as e:
            return (f"Error reading file: {str(e)}",)

class GPTConfigReader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"default": "/home/work/ComfyUI/models/design_resource/GPTConfig.txt"}),
                "token_key": ("STRING", {"default": "TOKEN"}),
                "api_key": ("STRING", {"default": "APIURL"}),
            },
        }

    RETURN_NAMES = ("token", "api_url")
    RETURN_TYPES = ("STRING", "STRING")
    FUNCTION = "read_gpt_config"
    CATEGORY = "✨✨✨design-ai/io"

    def read_gpt_config(self, file_path, token_key, api_key):
        try:
            if not os.path.exists(file_path):
                return ("Error: Config file not found", "Error: Config file not found")
            
            token = ""
            api_url = ""
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
            
            for line in content:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == token_key:
                        token = value
                    elif key == api_key:
                        api_url = value
            
            if not token:
                token = f"Token not found with key '{token_key}'"
            if not api_url:
                api_url = f"API URL not found with key '{api_key}'"
                
            return (token, api_url)
            
        except Exception as e:
            return (f"Error reading config: {str(e)}", f"Error reading config: {str(e)}")

class WanqingConfigReader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"default": "/home/work/ComfyUI/models/design_resource/WANQINGConfig.txt"}),
                "token_key": ("STRING", {"default": "TOKEN"}),
            },
        }

    RETURN_NAMES = ("token",)
    RETURN_TYPES = ("STRING",)
    FUNCTION = "read_wanqing_config"
    CATEGORY = "✨✨✨design-ai/io"

    def read_wanqing_config(self, file_path, token_key):
        try:
            if not os.path.exists(file_path):
                return (f"Error: Config file not found at {file_path}",)
            
            token = ""
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
            
            for line in content:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == token_key:
                        token = value
                        break
            
            if not token:
                token = f"Token not found with key '{token_key}'"
                
            return (token,)
            
        except Exception as e:
            return (f"Error reading config: {str(e)}",) 