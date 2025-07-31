import math
import random
import torch
import zlib
import base64

class watermark_Mark:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
            Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
            Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
            The type can be a list for selection.

            Returns: `dict`:
                - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
                - Value input_fields (`dict`): Contains input fields config:
                    * Key field_name (`string`): Name of a entry-point method's argument
                    * Value field_config (`tuple`):
                        + First value is a string indicate the type of field or a list for selection.
                        + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "encode": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "use_compression": ("BOOLEAN", {"default": True}),
                "bit_depth": (["1", "2", "3"], {"default": "2"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "mark"
    CATEGORY = "✨✨✨design-ai/img"

    @staticmethod
    def _text_to_bits(text, use_compression=True):
        """将文本转换为比特序列，支持压缩"""
        if not text:
            return []
        
        # 编码为UTF-8字节
        text_bytes = text.encode('utf-8')
        
        # 如果启用压缩
        if use_compression:
            try:
                compressed_bytes = zlib.compress(text_bytes, level=9)
                # 如果压缩后更小，则使用压缩版本，并添加压缩标记
                if len(compressed_bytes) < len(text_bytes):
                    text_bytes = b'\x01' + compressed_bytes  # 0x01表示压缩
                else:
                    text_bytes = b'\x00' + text_bytes  # 0x00表示未压缩
            except:
                text_bytes = b'\x00' + text_bytes
        else:
            text_bytes = b'\x00' + text_bytes
        
        # 转换为比特序列
        bits = []
        for byte in text_bytes:
            for i in range(8):
                bits.append((byte >> (7-i)) & 1)
        
        return bits

    @staticmethod
    def _bits_to_text(bits, use_compression=True):
        """将比特序列转换为文本，支持解压缩"""
        if not bits or len(bits) < 8:
            return ""
        
        # 将比特转换为字节
        text_bytes = bytearray()
        for i in range(0, len(bits) - len(bits) % 8, 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            text_bytes.append(byte)
        
        try:
            # 检查是否压缩
            if text_bytes[0] == 1:  # 压缩标记
                compressed_data = bytes(text_bytes[1:])
                decompressed_data = zlib.decompress(compressed_data)
                return decompressed_data.decode('utf-8')
            else:  # 未压缩
                return bytes(text_bytes[1:]).decode('utf-8')
        except:
            return ""

    @staticmethod
    def _calculate_capacity(image_shape, bit_depth):
        """计算图像可容纳的比特数"""
        batch_size, height, width, channels = image_shape
        # 每个像素每个通道可以存储 bit_depth 个比特
        total_pixels = height * width * channels
        # 预留一些像素用于存储元数据（长度、校验等）
        reserved_pixels = min(100, total_pixels // 10)
        available_pixels = total_pixels - reserved_pixels
        return available_pixels * bit_depth

    @staticmethod
    def _embed_metadata(image, data_length, bit_depth):
        """在图像开始位置嵌入元数据"""
        # 将数据长度转换为32位二进制
        length_bits = []
        for i in range(32):
            length_bits.append((data_length >> (31-i)) & 1)
        
        # 嵌入长度信息到前32个像素位置
        bit_idx = 0
        for h in range(image.shape[1]):
            for w in range(image.shape[2]):
                for c in range(image.shape[3]):
                    if bit_idx >= 32:
                        return
                    
                    pixel_val = image[0][h][w][c].item()
                    pixel_int = int(pixel_val * 255)
                    
                    # 根据bit_depth修改最低位
                    for depth in range(int(bit_depth)):
                        if bit_idx + depth < 32:
                            bit_to_embed = length_bits[bit_idx + depth]
                            # 修改对应的位
                            if depth == 0:
                                pixel_int = (pixel_int & 0xFE) | bit_to_embed
                            elif depth == 1:
                                pixel_int = (pixel_int & 0xFD) | (bit_to_embed << 1)
                            elif depth == 2:
                                pixel_int = (pixel_int & 0xFB) | (bit_to_embed << 2)
                    
                    image[0][h][w][c] = pixel_int / 255.0
                    bit_idx += int(bit_depth)

    @staticmethod
    def _extract_metadata(image, bit_depth):
        """从图像开始位置提取元数据"""
        length_bits = []
        bit_idx = 0
        
        for h in range(image.shape[1]):
            for w in range(image.shape[2]):
                for c in range(image.shape[3]):
                    if bit_idx >= 32:
                        break
                    
                    pixel_val = image[0][h][w][c].item()
                    pixel_int = int(pixel_val * 255)
                    
                    # 根据bit_depth提取最低位
                    for depth in range(int(bit_depth)):
                        if bit_idx < 32:
                            if depth == 0:
                                bit = pixel_int & 1
                            elif depth == 1:
                                bit = (pixel_int >> 1) & 1
                            elif depth == 2:
                                bit = (pixel_int >> 2) & 1
                            length_bits.append(bit)
                            bit_idx += 1
                
                if bit_idx >= 32:
                    break
            if bit_idx >= 32:
                break
        
        # 将比特转换为长度
        data_length = 0
        for i, bit in enumerate(length_bits[:32]):
            data_length |= bit << (31 - i)
        
        return data_length

    @staticmethod
    def mark(image, encode, use_compression=True, bit_depth="2"):
        if len(encode) > 1024:
            raise Exception("Text too long! Maximum 1024 characters supported.")
        
        # 检查图像容量
        capacity = watermark_Mark._calculate_capacity(image.shape, int(bit_depth))
        
        # 转换文本为比特
        bits = watermark_Mark._text_to_bits(encode, use_compression)
        
        if len(bits) > capacity:
            raise Exception(f"Text too long for this image! Available capacity: {capacity} bits, required: {len(bits)} bits.")
        
        # 克隆图像以避免修改原始数据
        watermarked_image = image.clone()
        
        # 嵌入元数据
        watermark_Mark._embed_metadata(watermarked_image, len(bits), bit_depth)
        
        # 嵌入数据比特
        bit_idx = 0
        metadata_pixels = 32 // int(bit_depth) + (1 if 32 % int(bit_depth) > 0 else 0)
        pixel_count = 0
        
        for h in range(watermarked_image.shape[1]):
            for w in range(watermarked_image.shape[2]):
                for c in range(watermarked_image.shape[3]):
                    if pixel_count < metadata_pixels:
                        pixel_count += 1
                        continue
                    
                    if bit_idx >= len(bits):
                        return (watermarked_image,)
                    
                    pixel_val = watermarked_image[0][h][w][c].item()
                    pixel_int = int(pixel_val * 255)
                    
                    # 根据bit_depth嵌入比特
                    for depth in range(int(bit_depth)):
                        if bit_idx < len(bits):
                            bit_to_embed = bits[bit_idx]
                            # 修改对应的位
                            if depth == 0:
                                pixel_int = (pixel_int & 0xFE) | bit_to_embed
                            elif depth == 1:
                                pixel_int = (pixel_int & 0xFD) | (bit_to_embed << 1)
                            elif depth == 2:
                                pixel_int = (pixel_int & 0xFB) | (bit_to_embed << 2)
                            bit_idx += 1
                    
                    watermarked_image[0][h][w][c] = pixel_int / 255.0
        
        return (watermarked_image,)


class watermark_Extract:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
            Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
            Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
            The type can be a list for selection.

            Returns: `dict`:
                - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
                - Value input_fields (`dict`): Contains input fields config:
                    * Key field_name (`string`): Name of a entry-point method's argument
                    * Value field_config (`tuple`):
                        + First value is a string indicate the type of field or a list for selection.
                        + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "bit_depth": (["1", "2", "3"], {"default": "2"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract"
    CATEGORY = "✨✨✨design-ai/img"

    @staticmethod
    def extract(image, bit_depth="2"):
        try:
            # 提取元数据
            data_length = watermark_Mark._extract_metadata(image, bit_depth)
            
            if data_length <= 0 or data_length > 1024 * 8 * 4:  # 合理性检查
                return ("",)
            
            # 提取数据比特
            bits = []
            bit_idx = 0
            metadata_pixels = 32 // int(bit_depth) + (1 if 32 % int(bit_depth) > 0 else 0)
            pixel_count = 0
            
            for h in range(image.shape[1]):
                for w in range(image.shape[2]):
                    for c in range(image.shape[3]):
                        if pixel_count < metadata_pixels:
                            pixel_count += 1
                            continue
                        
                        if bit_idx >= data_length:
                            break
                        
                        pixel_val = image[0][h][w][c].item()
                        pixel_int = int(pixel_val * 255)
                        
                        # 根据bit_depth提取比特
                        for depth in range(int(bit_depth)):
                            if bit_idx < data_length:
                                if depth == 0:
                                    bit = pixel_int & 1
                                elif depth == 1:
                                    bit = (pixel_int >> 1) & 1
                                elif depth == 2:
                                    bit = (pixel_int >> 2) & 1
                                bits.append(bit)
                                bit_idx += 1
                    
                    if bit_idx >= data_length:
                        break
                if bit_idx >= data_length:
                    break
            
            # 将比特转换为文本
            extracted_text = watermark_Mark._bits_to_text(bits, use_compression=True)
            return (extracted_text,)
            
        except Exception as e:
            return ("",)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "Apply Invisible Watermark": watermark_Mark,
    "Extract Watermark": watermark_Extract,
}