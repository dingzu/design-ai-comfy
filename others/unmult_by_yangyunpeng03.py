from PIL import Image
import numpy as np
import torch
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter
# matplotlib导入和后端设置（可选，如果环境中没有matplotlib会跳过）
try:
    import matplotlib.pyplot as plt
    # 确保matplotlib使用非交互后端
    plt.switch_backend('Agg')
except ImportError:
    # matplotlib不是必需的，跳过
    pass

# 节点注册映射（统一管理）
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 第一个节点：透明通道曲线调整
class AlphaCurveAdjustNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "point1_x": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "point1_y": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "point2_x": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01}),
                "point2_y": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "point3_x": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "point3_y": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "curve_smoothness": ("INT", {"default": 3, "min": 1, "max": 5, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("调整后图像",)
    FUNCTION = "adjust_alpha_curve"
    CATEGORY = "✨✨✨design-ai/yangyunpeng"

    def adjust_alpha_curve(self, image, point1_x, point1_y, point2_x, point2_y, point3_x, point3_y, curve_smoothness):
        if isinstance(image, torch.Tensor):
            img_np = image.cpu().numpy()
            if len(img_np.shape) == 4:
                img_np = img_np[0]
        
        # 处理无 alpha 通道的情况
        if img_np.shape[-1] == 3:
            alpha_channel = np.ones((img_np.shape[0], img_np.shape[1], 1), dtype=np.float32)
            img_np = np.concatenate([img_np, alpha_channel], axis=-1)
        
        rgb_channels = img_np[..., :3]
        alpha_channel = img_np[..., 3:4]
        
        # 构建控制点并预处理
        points = np.array([
            [point1_x, point1_y],
            [point2_x, point2_y],
            [point3_x, point3_y]
        ])
        points = np.unique(points, axis=0)
        points = points[points[:, 0].argsort()]
        
        if len(points) < 2:
            return (torch.from_numpy(img_np).unsqueeze(0),)
        
        # 补充边界点
        if points[0, 0] > 1e-6:
            points = np.insert(points, 0, [0.0, 0.0], axis=0)
        if points[-1, 0] < 1.0 - 1e-6:
            points = np.append(points, [[1.0, 1.0]], axis=0)
        
        # 创建插值函数，增加异常兜底
        try:
            kind = 'cubic' if curve_smoothness >= 3 else 'linear'
            f = interp1d(
                points[:, 0], 
                points[:, 1], 
                kind=kind, 
                bounds_error=False, 
                fill_value=(points[0, 1], points[-1, 1])
            )
        except ValueError:
            f = interp1d(
                points[:, 0], 
                points[:, 1], 
                kind='linear', 
                bounds_error=False, 
                fill_value=(points[0, 1], points[-1, 1])
            )
        
        # 应用曲线调整
        adjusted_alpha = f(alpha_channel)
        adjusted_alpha = np.clip(adjusted_alpha, 0.0, 1.0)
        
        result_np = np.concatenate([rgb_channels, adjusted_alpha], axis=-1)
        result_tensor = torch.from_numpy(result_np).unsqueeze(0)
        
        return (result_tensor,)


# 第二个节点：图像正常混合（保留透明）
class ImageNormalBlendNode:
    """
    图像正常混合节点（保留透明通道）
    实现类似Photoshop正常混合模式，同时保留透明通道信息
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image": ("IMAGE",),  # 底层图像（支持透明通道）
                "top_image": ("IMAGE",),   # 顶层图像（支持透明通道）
                "opacity": ("FLOAT", {     # 顶层透明度（0.0-1.0）
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("混合图像",)
    FUNCTION = "blend_images"
    CATEGORY = "✨✨✨design-ai/yangyunpeng"

    def blend_images(self, base_image, top_image, opacity):
        # 处理输入图像格式：将Tensor转换为numpy数组并移除批次维度
        if isinstance(base_image, torch.Tensor):
            base_np = base_image.cpu().numpy()
            if len(base_np.shape) == 4:
                base_np = base_np[0]
        
        if isinstance(top_image, torch.Tensor):
            top_np = top_image.cpu().numpy()
            if len(top_np.shape) == 4:
                top_np = top_np[0]
        
        # 转换为PIL图像并确保为RGBA模式
        base_pil = Image.fromarray((base_np * 255).astype(np.uint8)).convert("RGBA")
        top_pil = Image.fromarray((top_np * 255).astype(np.uint8)).convert("RGBA")
        
        # 调整顶层图像尺寸以匹配底层图像
        if base_pil.size != top_pil.size:
            top_pil = top_pil.resize(base_pil.size, Image.Resampling.LANCZOS)
        
        # 转换为numpy数组并归一化到0-1范围
        base_rgba = np.array(base_pil, dtype=np.float32) / 255.0
        top_rgba = np.array(top_pil, dtype=np.float32) / 255.0
        
        # 应用顶层透明度到alpha通道
        top_rgba[..., 3] *= opacity
        
        # 提取顶层alpha通道
        top_alpha = top_rgba[..., 3:4]
        
        # 计算混合后的RGB通道
        result_rgb = (top_rgba[..., :3] * top_alpha) + (base_rgba[..., :3] * (1 - top_alpha))
        
        # 计算混合后的alpha通道
        result_alpha = top_alpha + (base_rgba[..., 3:4] * (1 - top_alpha))
        
        # 合并通道并转换回ComfyUI格式
        result_rgba = np.concatenate([result_rgb, result_alpha], axis=-1)
        result_np = (result_rgba * 255).astype(np.uint8).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result_np).unsqueeze(0)
        
        return (result_tensor,)


# 第三个节点：Unmult Black Background
class UnmultBlackBackground:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tolerance": ("INT", {"default": 255, "min": 0, "max": 255}),
                "anti_alias": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "✨✨✨design-ai/yangyunpeng"

    def process(self, image, tolerance, anti_alias):
        image_np = image[0].cpu().numpy()  # 取第一张图，转numpy
        image_np = np.clip(image_np * 255, 0, 255).astype(np.uint8)
        h, w, c = image_np.shape

        if c == 3:
            img_rgba = np.dstack((image_np, np.full((h, w), 255, dtype=np.uint8)))
        elif c == 4:
            img_rgba = image_np
        else:
            raise ValueError("不支持的通道数")

        r, g, b, a = [img_rgba[:, :, i].astype(np.float32) for i in range(4)]
        original_alpha = a / 255.0
        color_diff = np.sqrt(r**2 + g**2 + b**2)
        base_alpha = np.clip(color_diff / (tolerance + 1e-6), 0, 1)

        if anti_alias and tolerance > 0:
            base_alpha = gaussian_filter(base_alpha, sigma=1.0)

        final_alpha = base_alpha * original_alpha
        img_rgba[:, :, 3] = (final_alpha * 255).astype(np.uint8)

        # 转为 torch tensor，适配 ComfyUI
        out = torch.from_numpy(img_rgba.astype(np.float32) / 255.0).unsqueeze(0)
        return (out,)


# 统一注册所有节点
NODE_CLASS_MAPPINGS.update({
    "AlphaCurveAdjust": AlphaCurveAdjustNode,
    "ImageNormalBlendWithAlpha": ImageNormalBlendNode,
    "UnmultBlackBackground": UnmultBlackBackground
})

NODE_DISPLAY_NAME_MAPPINGS.update({
    "AlphaCurveAdjust": "透明通道曲线调整",
    "ImageNormalBlendWithAlpha": "图像正常混合（保留透明）",
    "UnmultBlackBackground": "扣黑"
})


# 确保符合ComfyUI插件格式要求
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
