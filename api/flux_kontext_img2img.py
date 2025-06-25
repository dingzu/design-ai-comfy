import torch
import numpy as np
import requests
import time
import base64
from PIL import Image
from io import BytesIO
import json

class FluxKontextImg2ImgNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""}),
                "model": (["pro", "max"], {"default": "pro"}),
                "input_image": ("IMAGE",),
                "prompt": ("STRING", {
                    "default": "", 
                    "multiline": True
                }),
                "aspect_ratio": ([
                    "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21",
                    "3:2", "2:3", "5:4", "4:5", "7:3", "3:7"
                ], {"default": "1:1"}),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "step": 1
                }),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 6,
                    "step": 1
                }),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
            },
            "optional": {
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING")
    RETURN_NAMES = ("image", "success", "message")
    FUNCTION = "edit_image"
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

    def edit_image(self, api_key, model, input_image, prompt, aspect_ratio, seed, 
                   prompt_upsampling, safety_tolerance, output_format, 
                   webhook_url="", webhook_secret=""):
        
        if not api_key.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "API key is required")
        
        if not prompt.strip():
            return (torch.zeros((1, 512, 512, 3)), False, "Prompt is required")

        # Determine API endpoint based on model
        if model == "max":
            endpoint = "https://api.bfl.ai/v1/flux-kontext-max"
        else:
            endpoint = "https://api.bfl.ai/v1/flux-kontext-pro"

        try:
            # Convert input image to base64
            print("Converting input image to base64...")
            base64_image = self.tensor_to_base64(input_image)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "input_image": base64_image,
                "aspect_ratio": aspect_ratio,
                "prompt_upsampling": prompt_upsampling,
                "safety_tolerance": safety_tolerance,
                "output_format": output_format
            }
            
            # Add seed if not -1 (random)
            if seed != -1:
                payload["seed"] = seed
                
            # Add webhook info if provided
            if webhook_url.strip():
                payload["webhook_url"] = webhook_url
            if webhook_secret.strip():
                payload["webhook_secret"] = webhook_secret

            headers = {
                'accept': 'application/json',
                'x-key': api_key,
                'Content-Type': 'application/json'
            }

            # Step 1: Create the request
            print(f"Sending image editing request to FLUX Kontext {model.upper()} with prompt: {prompt[:50]}...")
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"Request failed with status {response.status_code}: {response.text}"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg)

            request_data = response.json()
            request_id = request_data.get('id')
            polling_url = request_data.get('polling_url')
            
            if not polling_url:
                error_msg = "No polling URL received from API"
                print(error_msg)
                return (torch.zeros((1, 512, 512, 3)), False, error_msg)

            print(f"Request submitted with ID: {request_id}")
            print("Polling for result...")

            # Step 2: Poll for the result
            max_attempts = 120  # 2 minutes with 1-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(1)
                attempt += 1
                
                try:
                    poll_response = requests.get(
                        polling_url,
                        headers={'accept': 'application/json', 'x-key': api_key},
                        timeout=10
                    )
                    
                    if poll_response.status_code != 200:
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
                            return (torch.zeros((1, 512, 512, 3)), False, error_msg)
                        
                        # Download the image
                        print("Downloading edited image...")
                        image_response = requests.get(image_url, timeout=30)
                        
                        if image_response.status_code != 200:
                            error_msg = f"Failed to download image: {image_response.status_code}"
                            print(error_msg)
                            return (torch.zeros((1, 512, 512, 3)), False, error_msg)
                        
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
                        
                        success_msg = f"Image edited successfully with {model.upper()} model! Size: {image.size}"
                        print(success_msg)
                        return (tensor_image, True, success_msg)
                        
                    elif status in ["Error", "Failed"]:
                        error_msg = f"Image editing failed with status: {status}"
                        if 'error' in result_data:
                            error_msg += f" - {result_data['error']}"
                        print(error_msg)
                        return (torch.zeros((1, 512, 512, 3)), False, error_msg)
                        
                except requests.RequestException as e:
                    print(f"Polling error (attempt {attempt}): {e}")
                    continue
            
            # Timeout
            error_msg = f"Image editing timed out after {max_attempts} seconds"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return (torch.zeros((1, 512, 512, 3)), False, error_msg) 