import torch
import numpy as np
import requests
import base64
from PIL import Image
from io import BytesIO
import json

class GPTImageEditNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_url": ("STRING", {
                    "default": "https://api.openai.com",
                    "tooltip": "API Base URL，例如: https://api.openai.com"
                }),
                "api_key": ("STRING", {
                    "default": "sk-xxxxxxx",
                    "tooltip": "API密钥，用于Bearer Token认证"
                }),
                "model": ("STRING", {
                    "default": "gpt-image-1",
                    "tooltip": "模型名称，支持: gpt-image-1, flux-kontext-pro, flux-kontext-max"
                }),
                "image": ("IMAGE", {
                    "tooltip": "要编辑的图像，支持PNG、WEBP、JPG格式"
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "描述期望图像的文本，gpt-image-1最大32000字符，dall-e-2最大1000字符"
                }),
            },
            "optional": {
                "mask": ("IMAGE", {
                    "tooltip": "可选的PNG遮罩图像，透明区域(alpha=0)表示要编辑的区域"
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "要生成的图像数量，1-10之间"
                }),
                "quality": (["auto", "high", "medium", "low"], {
                    "default": "auto",
                    "tooltip": "仅适用于gpt-image-1的图像质量"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "b64_json",
                    "tooltip": "响应格式，url仅dall-e-2支持且有效期60分钟"
                }),
                "size": (["auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512"], {
                    "default": "auto",
                    "tooltip": "图像尺寸，gpt-image-1默认auto，dall-e-2支持256x256/512x512/1024x1024"
                }),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "API请求超时时间(秒)"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("image", "success", "message", "response_data")
    FUNCTION = "edit_image"
    CATEGORY = "✨✨✨design-ai/api"

    def tensor_to_base64(self, tensor_image, format='PNG'):
        """Convert tensor image to base64 string"""
        try:
            # Convert tensor to numpy array
            if len(tensor_image.shape) == 4:
                # Remove batch dimension if present
                np_image = tensor_image.squeeze(0).cpu().numpy()
            else:
                np_image = tensor_image.cpu().numpy()
            
            # Convert from [0,1] to [0,255]
            np_image = (np_image * 255).astype(np.uint8)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(np_image)
            
            # Convert to base64
            buffer = BytesIO()
            pil_image.save(buffer, format=format)
            image_data = buffer.getvalue()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            return base64_string
        except Exception as e:
            raise Exception(f"Error converting tensor to base64: {e}")

    def base64_to_tensor(self, base64_string):
        """Convert base64 string to tensor image"""
        try:
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array and then to tensor
            np_image = np.array(image).astype(np.float32) / 255.0
            tensor_image = torch.from_numpy(np_image).unsqueeze(0)
            
            return tensor_image
        except Exception as e:
            raise Exception(f"Error converting base64 to tensor: {e}")

    def download_image_to_tensor(self, image_url):
        """Download image from URL and convert to tensor"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array and then to tensor
            np_image = np.array(image).astype(np.float32) / 255.0
            tensor_image = torch.from_numpy(np_image).unsqueeze(0)
            
            return tensor_image
        except Exception as e:
            raise Exception(f"Error downloading image: {e}")

    def build_endpoint_url(self, base_url: str) -> str:
        """Build the image edit endpoint URL"""
        base_url = base_url.rstrip('/')
        return f"{base_url}/v1/images/edits"

    def edit_image(self, base_url, api_key, model, image, prompt, mask=None, n=1, 
                   quality="auto", response_format="b64_json", size="auto", timeout=120.0):
        
        # Validation
        if not api_key.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "API key is required", "")
        
        if not prompt.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "Prompt is required", "")

        try:
            # Build endpoint URL
            endpoint = self.build_endpoint_url(base_url)
            
            # Convert input image to base64
            print("Converting input image to base64...")
            image_base64 = self.tensor_to_base64(image, 'PNG')
            
            # Prepare form data for multipart/form-data request
            files = {
                'image': ('image.png', base64.b64decode(image_base64), 'image/png')
            }
            
            data = {
                'prompt': prompt,
                'model': model,
                'n': str(n),
                'response_format': response_format
            }
            
            # Add optional parameters
            if quality != "auto":
                data['quality'] = quality
                
            if size != "auto":
                data['size'] = size
            
            # Add mask if provided
            if mask is not None:
                print("Converting mask to base64...")
                mask_base64 = self.tensor_to_base64(mask, 'PNG')
                files['mask'] = ('mask.png', base64.b64decode(mask_base64), 'image/png')

            headers = {
                'Authorization': f'Bearer {api_key}'
            }

            # Make the API request
            print(f"Sending image edit request to {endpoint} with model: {model}")
            print(f"Prompt: {prompt[:100]}...")
            
            response = requests.post(
                endpoint,
                headers=headers,
                files=files,
                data=data,
                timeout=timeout
            )

            # Handle response
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg, "")

            response_data = response.json()
            print("Response received successfully")
            
            # Parse response data
            if 'data' not in response_data or not response_data['data']:
                error_msg = "No image data in response"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg, json.dumps(response_data, indent=2))

            # Get the first image from response
            image_data = response_data['data'][0]
            
            # Handle different response formats
            if response_format == "b64_json":
                if 'b64_json' not in image_data:
                    error_msg = "No b64_json data in response"
                    print(error_msg)
                    return (torch.zeros((1, 512, 512, 3)), False, error_msg, json.dumps(response_data, indent=2))
                
                # Convert base64 to tensor
                print("Converting response image to tensor...")
                tensor_image = self.base64_to_tensor(image_data['b64_json'])
                
            elif response_format == "url":
                if 'url' not in image_data:
                    error_msg = "No URL in response"
                    print(error_msg)
                    return (torch.zeros((1, 512, 512, 3)), False, error_msg, json.dumps(response_data, indent=2))
                
                # Download image from URL
                print(f"Downloading image from URL: {image_data['url']}")
                tensor_image = self.download_image_to_tensor(image_data['url'])
            
            else:
                error_msg = f"Unsupported response format: {response_format}"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg, json.dumps(response_data, indent=2))

            # Get usage information if available
            usage_info = ""
            if 'usage' in response_data:
                usage = response_data['usage']
                usage_info = f" | Tokens: {usage.get('total_tokens', 'N/A')}"

            success_msg = f"Image edited successfully with {model} model{usage_info}"
            print(success_msg)
            
            return (tensor_image, True, success_msg, json.dumps(response_data, indent=2))
            
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg, "")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg, "") 