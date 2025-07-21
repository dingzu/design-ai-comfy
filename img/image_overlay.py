import torch
import numpy as np
from PIL import Image

class ImageOverlay:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_a": ("IMAGE",),  # 底图
                "image_b": ("IMAGE",),  # 叠加图
                "enable_overlay": ("BOOLEAN", {"default": True}),  # 是否启用叠加
                "offset_x": ("INT", {"default": 0, "min": -4096, "max": 4096}),  # X轴偏移
                "offset_y": ("INT", {"default": 0, "min": -4096, "max": 4096}),  # Y轴偏移
                "coordinate_origin": ([
                    "top_left", 
                    "top_right", 
                    "bottom_left", 
                    "bottom_right"
                ], {"default": "top_left"}),  # 坐标系原点
            },
            "optional": {
                "mask_b": ("MASK",),  # 图片B的掩码
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output_image",)
    FUNCTION = "overlay_images"
    CATEGORY = "✨✨✨design-ai/img"

    def overlay_images(self, image_a, image_b, enable_overlay, offset_x, offset_y, coordinate_origin, mask_b=None):
        # 如果没有启用叠加，直接返回图片A
        if not enable_overlay:
            return (image_a,)
        
        # 转换torch tensor为PIL Image
        # 图片A（底图）
        img_a_array = 255. * image_a.cpu().numpy().squeeze()
        img_a = Image.fromarray(np.clip(img_a_array, 0, 255).astype(np.uint8))
        
        # 图片B（叠加图）
        img_b_array = 255. * image_b.cpu().numpy().squeeze()
        img_b = Image.fromarray(np.clip(img_b_array, 0, 255).astype(np.uint8))
        
        # 处理掩码
        if mask_b is not None:
            # 转换掩码为PIL图像
            # ComfyUI的MASK: 1.0表示白色（选中区域），0.0表示黑色（未选中区域）
            # PIL的paste mask: 255表示不透明（显示源图像），0表示透明（不显示）
            # 需要反转：ComfyUI中1.0的区域应该显示图片，所以直接转换
            # 但根据实际测试，需要反转掩码
            mask_array = (1.0 - mask_b.cpu().numpy().squeeze()) * 255
            mask_img = Image.fromarray(np.clip(mask_array, 0, 255).astype(np.uint8)).convert('L')
            # 确保掩码尺寸与图片B一致
            if mask_img.size != img_b.size:
                mask_img = mask_img.resize(img_b.size, Image.LANCZOS)
        else:
            # 如果没有提供掩码，创建一个全白掩码（完全不透明）
            mask_img = Image.new('L', img_b.size, 255)
        
        # 获取图片尺寸
        width_a, height_a = img_a.size
        width_b, height_b = img_b.size
        
        # 根据坐标系原点计算实际的粘贴位置
        paste_x, paste_y = self._calculate_paste_position(
            width_a, height_a, width_b, height_b, 
            offset_x, offset_y, coordinate_origin
        )
        
        # 处理图片B和掩码的裁剪（如果超出边界）
        crop_left = max(0, -paste_x)
        crop_top = max(0, -paste_y)
        crop_right = min(width_b, width_a - paste_x)
        crop_bottom = min(height_b, height_a - paste_y)
        
        # 如果完全超出边界，直接返回图片A
        if crop_right <= crop_left or crop_bottom <= crop_top:
            return (image_a,)
        
        # 裁剪图片B和掩码
        if crop_left > 0 or crop_top > 0 or crop_right < width_b or crop_bottom < height_b:
            img_b = img_b.crop((crop_left, crop_top, crop_right, crop_bottom))
            mask_img = mask_img.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        # 更新粘贴位置（考虑裁剪）
        actual_paste_x = max(0, paste_x)
        actual_paste_y = max(0, paste_y)
        
        # 创建结果图像（复制图片A）
        result_img = img_a.copy()
        
        # 使用掩码叠加图片B到图片A上
        result_img.paste(img_b, (actual_paste_x, actual_paste_y), mask_img)
        
        # 转换回torch tensor
        result_array = np.array(result_img).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result_array).unsqueeze(0)
        
        return (result_tensor,)
    
    def _calculate_paste_position(self, width_a, height_a, width_b, height_b, offset_x, offset_y, coordinate_origin):
        """根据坐标系原点计算实际的粘贴位置"""
        if coordinate_origin == "top_left":
            # 左上角原点：直接使用偏移量
            paste_x = offset_x
            paste_y = offset_y
        elif coordinate_origin == "top_right":
            # 右上角原点：X轴需要从右边开始计算
            paste_x = width_a - width_b - offset_x
            paste_y = offset_y
        elif coordinate_origin == "bottom_left":
            # 左下角原点：Y轴需要从底部开始计算
            paste_x = offset_x
            paste_y = height_a - height_b - offset_y
        elif coordinate_origin == "bottom_right":
            # 右下角原点：X和Y轴都需要从右下角开始计算
            paste_x = width_a - width_b - offset_x
            paste_y = height_a - height_b - offset_y
        else:
            # 默认为左上角
            paste_x = offset_x
            paste_y = offset_y
        
        return paste_x, paste_y 