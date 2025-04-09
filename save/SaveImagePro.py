import os
import json
import numpy as np
from PIL import Image
import folder_paths

class SaveImageProNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "format": (["jpg", "png"], {"default": "jpg"}),
                "metadata": (["disable", "enable"], {"default": "disable"}),
                "quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display": "slider"
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "✨✨✨design-ai/io"

    def save_images(self, images, filename_prefix, format, metadata, quality, prompt=None, extra_pnginfo=None):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix,
            self.output_dir,
            images[0].shape[1],
            images[0].shape[0]
        )
        
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            extension = f".{format.lower()}"
            file = f"{filename}_{counter:05}_{extension}"
            full_path = os.path.join(full_output_folder, file)
            
            if format.lower() == "jpg":
                img.save(full_path, format="JPEG", quality=quality)
            else:
                # PNG 格式：如果需要保存元信息，使用基本的 metadata 字典
                if metadata == "enable" and (prompt is not None or extra_pnginfo is not None):
                    metadata_dict = {}
                    if prompt is not None:
                        metadata_dict["prompt"] = json.dumps(prompt)
                    if extra_pnginfo is not None:
                        metadata_dict.update({k: json.dumps(v) for k, v in extra_pnginfo.items()})
                    img.save(full_path, format="PNG", pnginfo=None)
                    # 如果需要，可以在这里用其他方式保存元数据
                else:
                    img.save(full_path, format="PNG")
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}} 