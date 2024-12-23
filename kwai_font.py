import cv2
import numpy as np
import torch
import pytorch_lightning as ptl
from PIL import Image
from pathlib import Path
import folder_paths
import os
from .kwai_font_models.model import ResNet50Regressor, FontDetector, ResNet101Regressor
from torchvision.transforms import Resize
import torch.nn.functional as F
import torchvision.transforms.functional as F1
from .kwai_font_models import config
import json
import pickle
 

class Resnet50_Runner:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",), # ([B, H, W, C])
                "resnet50_model": ("RESNET50MODEL",),
                "font_list": ("FONTLIST",),
                "output_top_num": ("INT", {"default": 9, "min": 1, "max": 20}),
            },
        }

    # 节点目录映射
    CATEGORY = "✨✨✨design-ai/kwaifont"
 
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES =("font_type", )
    FUNCTION = "run_resnet50_model"
 
    def run_resnet50_model(self, image, resnet50_model, font_list, output_top_num):
        # print(font_list)
        if torch.__version__ >= "2.0" and os.name == "posix":
            model = torch.compile(resnet50_model)

        lambda_font = 2.0
        lambda_direction = 0.5
        lambda_regression = 1.0

        # 推理模式
        detector = FontDetector(
            model=model,
            lambda_font=1,
            lambda_direction=1,
            lambda_regression=1,
            font_classification_only=False,
            lr=1,
            betas=(1, 1),
            num_warmup_iters=1,
            num_iters=1e9,
            num_epochs=1e9,
        )

        device = torch.device("cuda:0")
        detector = detector.to(device)
        detector.eval()

        # 尺寸转换
        img = image.permute(0, 3, 2, 1)
        img_resize = F.interpolate(img, size=(512, 512), mode='bilinear', align_corners=False).squeeze(0)

        result = []

        with torch.no_grad():
            # 转换为cuda并推理
            img_resize = img_resize.to(device)
            output = detector(img_resize.unsqueeze(0))
            prob = output[0][: config.FONT_COUNT].softmax(dim=0)
        
            indicies = list(torch.topk(prob, output_top_num))
            for i in range(output_top_num):
                # 输出用户指定的排名前几的字体识别结果和分数
                # res = [font_list[str(indicies[1][i].to('cpu').item())], f"{float(indicies[0][i].to('cpu').item()):.8f}"]
                # index = indicies[1][i].to('cpu').item()
                font_family = font_list[str(indicies[1][i].to('cpu').item())]
                score = f"{float(indicies[0][i].to('cpu').item()):.8f}"
                result.append({"font_family":font_family, "'score":score})
 
        res_str = str(result)

        return (res_str, )

# Yuzumarker 模型加载节点
class Resnet50_Loader:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "model": ([item.name for item in Path(folder_paths.models_dir, "kwaifont").iterdir()], {"tooltip": 
            "models are expected to be in like Comfyui/models/kwaifont/resnet50_alldata dir"}),
            # "font_data": ([item.name for item in Path(folder_paths.models_dir, "kwaifont/resnet50/font_data").iterdir()], {"tooltip": 
            # "models are expected to be in Comfyui/models/kwaifont/resnet50/font_data folder"}),
            }
        }
    RETURN_TYPES = ("RESNET50MODEL", "FONTLIST",)
    RETURN_NAMES = ("resnet50_model", "font_list",)
    FUNCTION = "loadmodel"
    CATEGORY = "✨✨✨design-ai/kwaifont"

    def loadmodel(self, model):
        font_path = Path(folder_paths.models_dir, "kwaifont", model)

        font_data_path = str(font_path) + '/' + [i for i in os.listdir(font_path) if i.endswith('.bin')][0]
        model_path = str(font_path) + '/'  + [i for i in os.listdir(font_path) if not i.endswith('.bin')][0]

        # 读取字体分类映射表
        with open(font_data_path, 'rb') as file:
            json_str = pickle.load(file)
        font_list_data = json.loads(json_str)

        # 加载模型
        print(f"Loading model from {model_path}")

        load_model = ResNet50Regressor(
        pretrained=False, regression_use_tanh=False
    )
        # 加载checkpoint文件
        checkpoint = torch.load(model_path)['state_dict']
        new_checkpoint = {}
        # 去除state_dict冗余前缀
        for key,value in checkpoint.items():
            new_key = key[len("model._orig_mod."):]
            new_checkpoint[new_key] = value
        # print(checkpoint.keys())
        load_model.load_state_dict(new_checkpoint)
        del checkpoint

        # 需要以元组形式返回参数
        return (load_model, font_list_data) 

# Yuzumarker 模型推理节点 
class Resnet101_Runner:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",), # ([B, H, W, C])
                "resnet101_model": ("RESNET101MODEL",),
                "font_list": ("FONTLIST",),
                "output_top_num": ("INT", {"default": 9, "min": 1, "max": 20}),
            },
        }

    # 节点目录映射
    CATEGORY = "✨✨✨design-ai/kwaifont"
 
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES =("font_type", "demo_images")
    FUNCTION = "run_resnet101_model"
 
    def run_resnet101_model(self, image, resnet101_model, font_list, output_top_num):
        # print(font_list)
        if torch.__version__ >= "2.0" and os.name == "posix":
            model = torch.compile(resnet101_model)

        lambda_font = 2.0
        lambda_direction = 0.5
        lambda_regression = 1.0

        # 推理模式
        detector = FontDetector(
            model=model,
            lambda_font=1,
            lambda_direction=1,
            lambda_regression=1,
            font_classification_only=False,
            lr=1,
            betas=(1, 1),
            num_warmup_iters=1,
            num_iters=1e9,
            num_epochs=1e9,
        )

        device = torch.device("cuda:0")
        detector = detector.to(device)
        detector.eval()

        # 尺寸转换
        img = image.permute(0, 3, 2, 1)

        img_resize = F.interpolate(img, size=(512, 512), mode='bilinear', align_corners=False).squeeze(0)

        base_demo_dir = folder_paths.models_dir + "/kwaifont/resnet101/demo_fonts/"
        demo_font_images = os.listdir(base_demo_dir)
        demo_font_images = sorted(demo_font_images, key=lambda x: int(x.split('.')[0]))
        result = []
        out = []

        with torch.no_grad():
            # 转换为cuda并推理
            img_resize = img_resize.to(device)
            output = detector(img_resize.unsqueeze(0))
            # prob = output[0][: config.FONT_COUNT].softmax(dim=0)
            prob = output[0][: 6150].softmax(dim=0)
        
            indicies = list(torch.topk(prob, output_top_num))
            for i in range(output_top_num):
                # 输出用户指定的排名前几的字体识别结果和分数
                # res = [font_list[str(indicies[1][i].to('cpu').item())], f"{float(indicies[0][i].to('cpu').item()):.8f}"]
                res = str(indicies[1][i].to('cpu').item()).ljust(5) + str(font_list[str(indicies[1][i].to('cpu').item())]).ljust(40) + ": " + f"{float(indicies[0][i].to('cpu').item()):.8f}"
                result.append(res)
            # 输出demo字体样式图
            demo_image = Image.open(base_demo_dir + demo_font_images[int(indicies[1][0].to('cpu').item())])
            annotated_image_tensor = F1.to_tensor(demo_image)
            out_tensor = annotated_image_tensor[:3, :, :].unsqueeze(0).permute(0, 2, 3, 1).cpu().float()
            out.append(out_tensor)
        
        res_str = "\n".join(result)
        out_demo = torch.cat(out, dim=0)

        return (res_str, out_demo,)

# Yuzumarker 模型加载节点
class Resnet101_Loader:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "model": ([item.name for item in Path(folder_paths.models_dir, "kwaifont/resnet101/checkpoint").iterdir()], {"tooltip": 
            "models are expected to be in Comfyui/models/kwaifont/resnet101/checkpoint folder"}),
            "font_data": ([item.name for item in Path(folder_paths.models_dir, "kwaifont/resnet101/font_data").iterdir()], {"tooltip": 
            "models are expected to be in Comfyui/models/kwaifont/resnet101/font_data folder"}),
            }
        }
    RETURN_TYPES = ("RESNET101MODEL", "FONTLIST",)
    RETURN_NAMES = ("resnet101_model", "font_list",)
    FUNCTION = "loadmodel"
    CATEGORY = "✨✨✨design-ai/kwaifont"

    def loadmodel(self, model, font_data):

        font_data_path = Path(folder_paths.models_dir, "kwaifont/resnet101/font_data", font_data)
        # 读取字体分类映射表
        with open(font_data_path, 'rb') as file:
            json_str = pickle.load(file)
        font_list_data = json.loads(json_str)

        # 加载模型
        model_path = Path(folder_paths.models_dir, "kwaifont/resnet101/checkpoint", model)
        print(f"Loading model from {model_path}")

        load_model = ResNet101Regressor(
        pretrained=False, regression_use_tanh=False
    )
        # 加载checkpoint文件
        checkpoint = torch.load(model_path)['state_dict']
        new_checkpoint = {}
        # 去除state_dict冗余前缀
        for key,value in checkpoint.items():
            new_key = key[len("model._orig_mod."):]
            new_checkpoint[new_key] = value
        # print(checkpoint.keys())
        load_model.load_state_dict(new_checkpoint)
        del checkpoint

        # 需要以元组形式返回参数
        return (load_model, font_list_data) 

# 根据矩形坐标裁剪文本区域并返回图片
class Image_Cropper:
    def __init__(self):
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image": ("IMAGE",), 
            "out_data": ("JSON",),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "crop_image"
    CATEGORY = "✨✨✨design-ai/kwaifont"
    
    def crop_image(self, image, out_data):
        # preview 图像维度顺序：premute(0,3,1,2)后permute(0,3,2,1)，即(B,H,W,C)
        # print(image.shape)
        rectangle = []
        for i in out_data[0]:
            x1, x2, y1, y2 = int(i[0]), int(i[2]), int(i[1]), int(i[3])
            crop_image = image[:, y1:y2, x1:x2, :].permute(0,3,1,2)
            # print(crop_image.shape)
            crop_image = F.interpolate(crop_image, size=(512, 1024), mode='bilinear', align_corners=False) # size(H,W)
            crop_image = crop_image.permute(0,2,3,1)
            rectangle.append(crop_image)
            # print(crop_image.shape)

        result = torch.cat(rectangle, dim=0)
        
        # 返回ui属性以显示图片
        return (result, )
