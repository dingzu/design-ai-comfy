import torch
import numpy as np
import requests
import time
import base64
from PIL import Image
from io import BytesIO
import json

class FluxThirdPartyAPINode:
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
                "model": (["pro", "max"], {"default": "pro"}),
                "api_type": (["text2img", "img2img"], {
                    "default": "text2img",
                    "tooltip": "API类型：文本生成图像或图像编辑"
                }),
                "prompt": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "描述你想要生成或编辑的图像的文本"
                }),
                "aspect_ratio": ([
                    "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21",
                    "3:2", "2:3", "5:4", "4:5", "7:3", "3:7"
                ], {"default": "1:1"}),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "step": 1,
                    "tooltip": "随机种子，-1表示随机生成"
                }),
                "prompt_upsampling": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用提示增强"
                }),
                "safety_tolerance": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 6,
                    "step": 1,
                    "tooltip": "安全等级，0最严格，6最宽松"
                }),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "timeout": ("FLOAT", {
                    "default": 120.0,
                    "min": 30.0,
                    "max": 300.0,
                    "step": 10.0,
                    "tooltip": "API请求超时时间(秒)"
                }),
                "max_poll_attempts": ("INT", {
                    "default": 120,
                    "min": 30,
                    "max": 600,
                    "step": 10,
                    "tooltip": "最大轮询次数"
                }),
            },
            "optional": {
                "input_image": ("IMAGE", {
                    "tooltip": "输入图像（仅用于img2img模式）"
                }),
                "webhook_url": ("STRING", {
                    "default": "",
                    "tooltip": "可选的Webhook URL"
                }),
                "webhook_secret": ("STRING", {
                    "default": "",
                    "tooltip": "可选的Webhook密钥"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("image", "success", "message", "request_id", "api_endpoint")
    FUNCTION = "process_request"
    CATEGORY = "✨✨✨design-ai/api"

    def tensor_to_base64(self, tensor_image):
        """Convert tensor image to base64 string"""
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
        pil_image.save(buffer, format='PNG')
        image_data = buffer.getvalue()
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
        return base64_string

    def build_endpoint_url(self, base_url, model, api_type):
        """Build the API endpoint URL based on base_url, model and api_type"""
        # Remove trailing slash from base_url
        base_url = base_url.rstrip('/')
        
        # Build endpoint based on api_type and model
        if api_type == "img2img":
            if model == "max":
                endpoint_path = "/bfl/v1/flux-kontext-max"
            else:
                endpoint_path = "/bfl/v1/flux-kontext-pro"
        else:  # text2img
            if model == "max":
                endpoint_path = "/bfl/v1/flux-kontext-max"
            else:
                endpoint_path = "/bfl/v1/flux-kontext-pro"
        
        return f"{base_url}{endpoint_path}"

    def build_polling_url(self, base_url, polling_url):
        """Build the polling URL for third-party API"""
        if polling_url.startswith('http'):
            # If polling_url is absolute, replace the domain with our base_url
            # Extract the path from polling_url
            if 'api.bfl.ai' in polling_url:
                # Replace api.bfl.ai domain with our base_url/bfl
                path = polling_url.replace('https://api.bfl.ai', '')
                return f"{base_url.rstrip('/')}/bfl{path}"
            else:
                return polling_url
        else:
            # If polling_url is relative, append to base_url
            return f"{base_url.rstrip('/')}/bfl{polling_url}"

    def process_request(self, base_url, api_key, model, api_type, prompt, aspect_ratio, seed,
                       prompt_upsampling, safety_tolerance, output_format, timeout, max_poll_attempts,
                       input_image=None, webhook_url="", webhook_secret=""):
        
        # Validation
        if not base_url.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "Base URL is required", "", "")
        
        if not api_key.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "API key is required", "", "")
        
        if not prompt.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "Prompt is required", "", "")

        if api_type == "img2img" and input_image is None:
            return (torch.zeros((1, 512, 512, 3)), False, "Input image is required for img2img mode", "", "")

        try:
            # Build API endpoint
            endpoint = self.build_endpoint_url(base_url, model, api_type)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "prompt_upsampling": prompt_upsampling,
                "safety_tolerance": safety_tolerance,
                "output_format": output_format
            }
            
            # Add input image for img2img
            if api_type == "img2img" and input_image is not None:
                print("Converting input image to base64...")
                base64_image = self.tensor_to_base64(input_image)
                payload["input_image"] = base64_image
            
            # Add seed if not -1 (random)
            if seed != -1:
                payload["seed"] = seed
                
            # Add webhook info if provided
            if webhook_url.strip():
                payload["webhook_url"] = webhook_url
            if webhook_secret.strip():
                payload["webhook_secret"] = webhook_secret

            # Setup headers with Bearer token authentication
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Step 1: Create the request
            print(f"Sending {api_type} request to third-party FLUX API...")
            print(f"Endpoint: {endpoint}")
            print(f"Model: {model.upper()}")
            print(f"Prompt: {prompt[:50]}...")
            
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=timeout
            )

            if response.status_code != 200:
                error_msg = f"Request failed with status {response.status_code}: {response.text}"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg, "", endpoint)

            request_data = response.json()
            request_id = request_data.get('id')
            polling_url = request_data.get('polling_url')
            
            if not polling_url:
                error_msg = "No polling URL received from API"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg, str(request_id) if request_id else "", endpoint)

            # Build the full polling URL for third-party API
            full_polling_url = self.build_polling_url(base_url, polling_url)
            
            print(f"Request submitted with ID: {request_id}")
            print(f"Polling URL: {full_polling_url}")
            print("Polling for result...")

            # Step 2: Poll for the result
            attempt = 0
            
            while attempt < max_poll_attempts:
                time.sleep(1)
                attempt += 1
                
                try:
                    poll_response = requests.get(
                        full_polling_url,
                        headers={'accept': 'application/json', 'Authorization': f'Bearer {api_key}'},
                        timeout=30
                    )
                    
                    if poll_response.status_code != 200:
                        print(f"Polling failed with status {poll_response.status_code}, attempt {attempt}")
                        continue
                        
                    result_data = poll_response.json()
                    status = result_data.get('status', 'Unknown')
                    
                    print(f"Status: {status} (attempt {attempt})")
                    
                    if status == "Ready":
                        # Get the image URL
                        result = result_data.get('result', {})
                        image_url = result.get('sample')
                        
                        if not image_url:
                            error_msg = "No image URL in result"
                            print(error_msg)
                            return (torch.zeros((1, 512, 512, 3)), False, error_msg, str(request_id) if request_id else "", endpoint)
                        
                        # Download the image
                        print(f"Downloading {api_type} result image...")
                        image_response = requests.get(image_url, timeout=60)
                        
                        if image_response.status_code != 200:
                            error_msg = f"Failed to download image: {image_response.status_code}"
                            print(error_msg)
                            return (torch.zeros((1, 512, 512, 3)), False, error_msg, str(request_id) if request_id else "", endpoint)
                        
                        # Convert to PIL Image
                        image = Image.open(BytesIO(image_response.content))
                        
                        # Convert to RGB if necessary
                        if image.mode in ('RGBA', 'LA'):
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            background.paste(image, mask=image.split()[-1])
                            image = background
                        elif image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # Convert to torch tensor
                        np_image = np.array(image).astype(np.float32) / 255.0
                        tensor_image = torch.from_numpy(np_image).unsqueeze(0)
                        
                        success_msg = f"{api_type.title()} completed successfully with {model.upper()} model! Size: {image.size}"
                        print(success_msg)
                        return (tensor_image, True, success_msg, str(request_id) if request_id else "", endpoint)
                        
                    elif status in ["Error", "Failed"]:
                        error_msg = f"{api_type.title()} failed with status: {status}"
                        if 'error' in result_data:
                            error_msg += f" - {result_data['error']}"
                        print(error_msg)
                        return (torch.zeros((1, 512, 512, 3)), False, error_msg, str(request_id) if request_id else "", endpoint)
                        
                except requests.RequestException as e:
                    print(f"Polling error (attempt {attempt}): {e}")
                    continue
            
            # Timeout
            error_msg = f"{api_type.title()} timed out after {max_poll_attempts} attempts"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg, str(request_id) if request_id else "", endpoint)
            
        except requests.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg, "", "")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg, "", "") 