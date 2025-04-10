import torch
import numpy as np
from PIL import Image

class CropByRatioAndBBox:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "bbox_values": ("STRING", {"default": "0,0,100,100", "multiline": False}),
                "target_ratio_w": ("INT", {"default": 1, "min": 1, "max": 100}),
                "target_ratio_h": ("INT", {"default": 1, "min": 1, "max": 100}),
                "crop_mode": ([
                    "fill_max_keep_partial",    # 模式1：最大化填充，允许部分裁剪
                    "fill_max_keep_complete",   # 模式2：最大化填充，保持完整
                    "fill_min_keep_complete",   # 模式3：最小化填充，保持完整
                    "fill_min_keep_partial",    # 模式4：最小化填充，允许部分裁剪
                ],),
                "pad_color": ("INT", {"default": 0, "min": 0, "max": 255}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "crop_by_ratio"
    CATEGORY = "✨✨✨design-ai/img"

    def parse_bbox(self, bbox_values):
        try:
            # 移除所有空格和方括号
            bbox_values = bbox_values.replace(" ", "")
            values_str = bbox_values.replace("[", "").replace("]", "")
            # 分割并转换为浮点数
            values = [float(x) for x in values_str.split(",")]
            
            # 确保有足够的值
            if len(values) >= 4:
                return (
                    round(values[0]),  # X1
                    round(values[1]),  # Y1
                    round(values[2]),  # X2
                    round(values[3])   # Y2
                )
            else:
                print("Not enough values in bbox_values, using default")
                return (0, 0, 100, 100)
        except Exception as e:
            print(f"Error parsing bbox: {e}")
            return (0, 0, 100, 100)

    def crop_by_ratio(self, image, bbox_values, 
                     target_ratio_w, target_ratio_h, crop_mode, pad_color):
        # Parse bbox coordinates
        bbox_x1, bbox_y1, bbox_x2, bbox_y2 = self.parse_bbox(bbox_values)
        
        # Convert torch tensor to PIL Image
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        # Get original dimensions and bbox info
        orig_width, orig_height = img.size
        bbox_width = bbox_x2 - bbox_x1
        bbox_height = bbox_y2 - bbox_y1
        target_ratio = target_ratio_w / target_ratio_h

        if crop_mode == "fill_max_keep_partial" or crop_mode == "fill_min_keep_partial":
            # 允许部分裁剪的模式
            if crop_mode == "fill_max_keep_partial":
                # 最大化填充，允许部分裁剪
                if orig_width / orig_height > target_ratio:
                    new_height = orig_height
                    new_width = int(new_height * target_ratio)
                else:
                    new_width = orig_width
                    new_height = int(new_width / target_ratio)
            else:  # fill_min_keep_partial
                # 最小化填充，允许部分裁剪
                if bbox_width / bbox_height > target_ratio:
                    new_height = bbox_height
                    new_width = int(new_height * target_ratio)
                else:
                    new_width = bbox_width
                    new_height = int(new_width / target_ratio)
            
            center_x = (bbox_x1 + bbox_x2) // 2
            center_y = (bbox_y1 + bbox_y2) // 2
            
            crop_x1 = center_x - new_width // 2
            crop_y1 = center_y - new_height // 2
            crop_x2 = crop_x1 + new_width
            crop_y2 = crop_y1 + new_height
            
            # 确保裁剪区域不超出图像边界
            if crop_x1 < 0:
                crop_x1 = 0
                crop_x2 = new_width
            if crop_y1 < 0:
                crop_y1 = 0
                crop_y2 = new_height
            if crop_x2 > orig_width:
                crop_x2 = orig_width
                crop_x1 = crop_x2 - new_width
            if crop_y2 > orig_height:
                crop_y2 = orig_height
                crop_y1 = crop_y2 - new_height
            
            result_img = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            # 创建全白mask（值为1.0）
            mask = torch.ones((result_img.height, result_img.width), dtype=torch.float32)

        else:  # keep_complete modes
            if crop_mode == "fill_max_keep_complete":
                if bbox_width / bbox_height > target_ratio:
                    new_width = bbox_width
                    new_height = int(new_width / target_ratio)
                else:
                    new_height = bbox_height
                    new_width = int(new_height * target_ratio)
            else:  # fill_min_keep_complete
                if bbox_width / bbox_height > target_ratio:
                    new_height = bbox_height
                    new_width = int(new_height * target_ratio)
                else:
                    new_width = bbox_width
                    new_height = int(new_width / target_ratio)

            # 创建新图像和mask
            result_img = Image.new('RGB', (new_width, new_height), (pad_color, pad_color, pad_color))
            # 初始化为全黑mask（值为0.0）
            mask = np.zeros((new_height, new_width), dtype=np.float32)

            paste_x = (new_width - orig_width) // 2
            paste_y = (new_height - orig_height) // 2

            if paste_x >= 0 and paste_y >= 0:
                # 如果原图比目标小，需要填充
                result_img.paste(img, (paste_x, paste_y))
                
                # 只在原图区域设置mask为1.0
                mask[paste_y:paste_y+orig_height, paste_x:paste_x+orig_width] = 1.0
            else:
                # 如果原图比目标大，需要裁剪
                crop_x = max(0, -paste_x)
                crop_y = max(0, -paste_y)
                crop_right = min(orig_width, crop_x + new_width)
                crop_bottom = min(orig_height, crop_y + new_height)
                
                cropped = img.crop((crop_x, crop_y, crop_right, crop_bottom))
                
                # 计算粘贴位置
                paste_x = max(0, paste_x)
                paste_y = max(0, paste_y)
                
                result_img.paste(cropped, (paste_x, paste_y))
                
                # 设置mask
                crop_width = crop_right - crop_x
                crop_height = crop_bottom - crop_y
                mask[paste_y:paste_y+crop_height, paste_x:paste_x+crop_width] = 1.0

        # 转换为torch tensor
        mask = torch.from_numpy(mask)

        # Convert back to torch tensors
        result_tensor = torch.from_numpy(np.array(result_img).astype(np.float32) / 255.0).unsqueeze(0)
        # 确保mask是正确的形状
        mask_tensor = mask.unsqueeze(0) if mask.dim() == 2 else mask

        return (result_tensor, mask_tensor) 