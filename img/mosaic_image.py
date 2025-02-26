import torch

class MosaicImage:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "block_size": ("INT", {
                    "default": 10, 
                    "min": 2,
                    "max": 100,
                    "step": 1,
                    "display": "number"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_mosaic"
    CATEGORY = "✨✨✨design-ai/img"

    def apply_mosaic(self, image, block_size):
        # 获取输入图像
        img = image[0]
        
        # 获取原始尺寸
        height, width, channels = img.shape
        
        # 计算新的尺寸
        new_h = height // block_size
        new_w = width // block_size
        
        # 重塑图像以便进行块操作
        reshaped = img.view(new_h, block_size, new_w, block_size, channels)
        
        # 计算每个块的平均值
        mosaic = torch.mean(torch.mean(reshaped, dim=3), dim=1)
        
        # 上采样回原始尺寸
        mosaic = mosaic.unsqueeze(1).unsqueeze(3)
        mosaic = mosaic.expand(-1, block_size, -1, block_size, -1)
        mosaic = mosaic.reshape(height, width, channels)
        
        # 确保输出格式正确
        return (mosaic.unsqueeze(0),) 