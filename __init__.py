from .blackborderdetector import BlackBorderDetector
from .cropborder import Cropborder
from .resize_and_center import ResizeAndCenter
from .switch_case_more import SwitchCaseMore
from .resize_by_side_pro import ResizeBySidePro
from .colorgenerator import GetPrimaryColor
from .text_color_on_bg import TextColorOnBg
from .draw_text_on_image import DrawTextOnImage
from .determine_text_position import DetermineTextPosition
from .crop_image_by_percentage import CropImageByPercentage
from .convert_json_format import ConvertJsonFormat
from .text_position_estimator import TextPositionEstimator
from .generate_mask_from_bbox import GenerateMaskFromBbox
from .random_color_generator import RandomColorGenerator
from .random_switch import RandomSwitch
from .string_builder import StringBuilder
from .generate_mask_from_points import GenerateMaskFromPoints
from .json_extractor import JsonExtractor
from .utils.chain_accessor import ChainAccessor
from .utils.chain_replacer import ChainReplacer
from .coordinate_sorter import CoordinateSorter
from .angle_calculator import AngleCalculator
from .transform_bbox import TransformBbox
from .filter_bbox import FilterBbox
from .color_name_generator import ColorNameGenerator
from .analyze_image_colors import AnalyzeImageColors
from .calculate_weighted_average_color import CalculateWeightedAverageColor
from .recommend_background_color import RecommendBackgroundColor
from .img.resize_img_and_mask_pro import ResizeImgAndMaskPro
from .img.resize_by_ratio_pro import ResizeByRatioPro
from .layer_transform import LayerTransform
from .layer_transform_no_mask import LayerTransformNoMask
from .bbox_sorter import BboxSorter
from .bbox_container import BboxContainer
from .bbox_measurement import BboxMeasurement
from .regex_processor import RegexProcessor
from .text_file_reader import TextFileReader, GPTConfigReader, WanqingConfigReader
from .api.load_image_from_url import LoadImageFromURL
from .logic.group_random_selector import GroupRandomSelector
from .api.openai_text_gen import OpenAITextGenNode
from .api.openai_vision import OpenAIVisionNode
from .img.image_base64 import ImageBase64Node
from .api.openai_vision_2 import OpenAIVision2Node
from .save.SaveText import SaveTextNode
from .img.mosaic_image import MosaicImage
from .img.water_mark import watermark_Mark, watermark_Extract
from .api.translate_service import TranslateServiceNode
from .save.SaveImagePro import SaveImageProNode
from .img.CropByRatioAndBBox import CropByRatioAndBBox
from .img.watermark_detection import WatermarkDetector, WatermarkCheck
from .api.flux_kontext_text2img import FluxKontextProNode
from .api.flux_kontext_img2img import FluxKontextImg2ImgNode
from .api.flux_third_party_api import FluxThirdPartyAPINode
from .api.gpt_third_party_api import GPTThirdPartyAPINode
from .api.upload_image import UploadImageNode
from .api.html_screenshot import HtmlScreenshotNode
from .api.html_screenshot_viewer import ApiResponseViewerNode
from .api.js_editor import JsEditorNode
from .utils.html_formatter import HtmlFormatterNode
from .utils.html_element_extractor import HtmlElementExtractorNode
from .utils.html_attribute_modifier import HtmlAttributeModifierNode
from .html_extractor import HtmlExtractorNode
from .api.ppinfra_gpt_node import PPInfraGPTNode
from .api.gpt_image_edit import GPTImageEditNode
from .api.wanqing_bbox_detector import WanqingBboxDetectorNode
from .api.wanqing_flexible_api import WanqingFlexibleAPINode
from .api.wanqing_gpt_image_generation import WanQingGPTImageGenerationNode
from .api.wanqing_gpt_image_edit import WanQingGPTImageEditNode
from .api.qwen_image_text2img import QwenImageText2ImgNode
from .api.qwen_image_edit import QwenImageEditNode
from .api.jimeng_text_to_image import JiMengTextToImageNode
from .api.jimeng_image_to_image import JiMengImageToImageNode
from .api.wanqing_jimeng_4_0_text2img import WanQingJiMeng40TextToImageNode
from .api.wanqing_jimeng_4_0_img2img import WanQingJiMeng40ImageToImageNode
from .api.kolors_text_to_image import KolorsTextToImageNode
from .api.kolors_image_to_image import KolorsImageToImageNode
from .api.kolors_expand_image import KolorsExpandImageNode
from .api.azure_openai_image_edit import AzureOpenAIImageEditNode
from .api.azure_openai_text2img import AzureOpenAIText2ImgNode
from .api.ketu_text_to_image import KetuTextToImageNode
from .img.image_overlay import ImageOverlay
from .img.XingYueSize import XingYueSize
from .api.gemini_2_5_flash_image_preview import Gemini25FlashImagePreviewNode
from .apiv2.jimeng_multi_image_to_image_v2 import JiMengMultiImageToImageNodeV2
from .apiv2.qwen_image_edit import QwenImageEditNode as QwenImageEditNodeV2
from .apiv2.wanqing_jimeng_4_0_img2img_v2 import WanQingJiMeng40ImageToImageNodeV2
from .apiv2.wanqing_jimeng_4_0_text2img_v2 import WanQingJiMeng40TextToImageNodeV2
from .apiv2.kolors_text_to_image_v2 import KolorsTextToImageNodeV2
from .apiv2.kolors_image_to_image_v2 import KolorsImageToImageNodeV2
from .apiv2.kolors_expand_image_v2 import KolorsExpandImageNodeV2
from .apiv2.qwen_image_text2img_v2 import QwenImageText2ImgNodeV2
from .apiv2.jimeng_image_to_image_v2 import JiMengImageToImageNodeV2
from .apiv2.ketu_text_to_image_v2 import KetuTextToImageNodeV2
from .apiv2.gemini_2_5_flash_image_preview_v2 import GeminiImageNodeV2
from .apiv2.gemini_multi_image_advanced_v3 import GeminiMultiImageAdvancedV2
from .others.unmult_by_yangyunpeng03 import AlphaCurveAdjustNode, ImageNormalBlendNode, UnmultBlackBackground

NODE_CLASS_MAPPINGS = {
    "BlackBorderDetector": BlackBorderDetector,
    "Cropborder": Cropborder,
    "ResizeAndCenter": ResizeAndCenter,
    "SwitchCaseMore": SwitchCaseMore,
    "ResizeBySidePro": ResizeBySidePro,
    "GetPrimaryColor": GetPrimaryColor,
    "TextColorOnBg": TextColorOnBg,
    "DrawTextOnImage": DrawTextOnImage,
    "DetermineTextPosition": DetermineTextPosition,
    "CropImageByPercentage": CropImageByPercentage,
    "ConvertJsonFormat":ConvertJsonFormat,
    "TextPositionEstimator":TextPositionEstimator,
    "GenerateMaskFromBbox": GenerateMaskFromBbox,
    "RandomColorGenerator": RandomColorGenerator,
    "RandomSwitch": RandomSwitch,
    "StringBuilder": StringBuilder,
    "GenerateMaskFromPoints": GenerateMaskFromPoints,
    "JsonExtractor": JsonExtractor,
    "ChainAccessor": ChainAccessor,
    "ChainReplacer": ChainReplacer,
    "CoordinateSorter":CoordinateSorter,
    "AngleCalculator":AngleCalculator,
    "TransformBbox":TransformBbox,
    "FilterBbox":FilterBbox,
    "ColorNameGenerator":ColorNameGenerator,
    "AnalyzeImageColors":AnalyzeImageColors,
    "CalculateWeightedAverageColor": CalculateWeightedAverageColor,
    "RecommendBackgroundColor": RecommendBackgroundColor,
    "ResizeImgAndMaskPro": ResizeImgAndMaskPro,
    "ResizeByRatioPro": ResizeByRatioPro,
    "LayerTransform": LayerTransform,
    "LayerTransformNoMask": LayerTransformNoMask,
    "BboxSorter":BboxSorter,
    "BboxContainer":BboxContainer,
    "BboxMeasurement":BboxMeasurement,
    "RegexProcessor":RegexProcessor,
    "TextFileReader": TextFileReader,
    "GPTConfigReader": GPTConfigReader,
    "WanqingConfigReader": WanqingConfigReader,
    "LoadImageFromURL":LoadImageFromURL,
    "GroupRandomSelector":GroupRandomSelector,
    "OpenAITextGenNode": OpenAITextGenNode,
    "OpenAIVisionNode": OpenAIVisionNode,
    "ImageBase64Node": ImageBase64Node,
    "OpenAIVision2Node": OpenAIVision2Node,
    "SaveTextNode": SaveTextNode,
    "MosaicImage": MosaicImage,
    "watermark_Mark": watermark_Mark,
    "watermark_Extract": watermark_Extract,
    "TranslateService": TranslateServiceNode,
    "SaveImagePro": SaveImageProNode,
    "CropByRatioAndBBox": CropByRatioAndBBox,
    "WatermarkDetector": WatermarkDetector,
    "WatermarkCheck": WatermarkCheck,
    "FluxKontextPro": FluxKontextProNode,
    "FluxKontextImg2Img": FluxKontextImg2ImgNode,
    "FluxThirdPartyAPI": FluxThirdPartyAPINode,
    "GPTThirdPartyAPI": GPTThirdPartyAPINode,
    "UploadImageNode": UploadImageNode,
    "HtmlScreenshotNode": HtmlScreenshotNode,
    "ApiResponseViewerNode": ApiResponseViewerNode,
    "JsEditorNode": JsEditorNode,
    "HtmlFormatterNode": HtmlFormatterNode,
    "HtmlElementExtractorNode": HtmlElementExtractorNode,
    "HtmlAttributeModifierNode": HtmlAttributeModifierNode,
    "HtmlExtractorNode": HtmlExtractorNode,
    "PPInfraGPTNode": PPInfraGPTNode,
    "GPTImageEditNode": GPTImageEditNode,
    "WanqingBboxDetectorNode": WanqingBboxDetectorNode,
    "WanqingFlexibleAPINode": WanqingFlexibleAPINode,
    "WanQingGPTImageGeneration": WanQingGPTImageGenerationNode,
    "WanQingGPTImageEdit": WanQingGPTImageEditNode,
    "QwenImageText2Img": QwenImageText2ImgNode,
    "QwenImageEdit": QwenImageEditNode,
    "JiMengTextToImage": JiMengTextToImageNode,
    "JiMengImageToImage": JiMengImageToImageNode,
    "WanQingJiMeng40TextToImage": WanQingJiMeng40TextToImageNode,
    "WanQingJiMeng40ImageToImage": WanQingJiMeng40ImageToImageNode,
    "KolorsTextToImage": KolorsTextToImageNode,
    "KolorsImageToImage": KolorsImageToImageNode,
    "KolorsExpandImage": KolorsExpandImageNode,
    "AzureOpenAIImageEdit": AzureOpenAIImageEditNode,
    "AzureOpenAIText2Img": AzureOpenAIText2ImgNode,
    "KetuTextToImage": KetuTextToImageNode,
    "ImageOverlay": ImageOverlay,
    "XingYueSize": XingYueSize,
    "Gemini25FlashImagePreview": Gemini25FlashImagePreviewNode,
    "JiMengMultiImageToImageV2": JiMengMultiImageToImageNodeV2,
    "QwenImageEditV2": QwenImageEditNodeV2,
    "WanQingJiMeng40ImageToImageV2": WanQingJiMeng40ImageToImageNodeV2,
    "WanQingJiMeng40TextToImageV2": WanQingJiMeng40TextToImageNodeV2,
    "KolorsTextToImageV2": KolorsTextToImageNodeV2,
    "KolorsImageToImageV2": KolorsImageToImageNodeV2,
    "KolorsExpandImageV2": KolorsExpandImageNodeV2,
    "QwenImageText2ImgV2": QwenImageText2ImgNodeV2,
    "JiMengImageToImageV2": JiMengImageToImageNodeV2,
    "KetuTextToImageV2": KetuTextToImageNodeV2,
    "GeminiImageNodeV2": GeminiImageNodeV2,
    "GeminiMultiImageAdvancedV2": GeminiMultiImageAdvancedV2,
    "AlphaCurveAdjust": AlphaCurveAdjustNode,
    "ImageNormalBlendWithAlpha": ImageNormalBlendNode,
    "UnmultBlackBackground": UnmultBlackBackground
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BlackBorderDetector": "img_black_border_detector",
    "Cropborder": "img_crop_border",
    "ResizeAndCenter": "resize_and_center",
    "SwitchCaseMore": "Switch_case_more",
    "ResizeBySidePro": "Resize_by_side_pro",
    "GetPrimaryColor": "GetPrimaryColor",
    "TextColorOnBg": "TextColorOnBg",
    "DrawTextOnImage": "DrawTextOnImage",
    "DetermineTextPosition": "DetermineTextPosition",
    "CropImageByPercentage": "CropImageByPercentage",
    "ConvertJsonFormat": "ConvertJsonFormat",
    "TextPositionEstimator": "TextPositionEstimator",
    "GenerateMaskFromBbox": "GenerateMaskFromBbox",
    "RandomColorGenerator": "RandomColorGenerator",
    "RandomSwitch": "RandomSwitch",
    "StringBuilder": "StringBuilder",
    "GenerateMaskFromPoints": "GenerateMaskFromPoints",
    "JsonExtractor": "JsonExtractor",
    "ChainAccessor": "ChainAccessor",
    "ChainReplacer": "ChainReplacer",
    "CoordinateSorter": "CoordinateSorter",
    "AngleCalculator": "AngleCalculator",
    "TransformBbox": "TransformBbox",
    "FilterBbox":"FilterBbox",
    "ColorNameGenerator": "ColorNameGenerator",
    "AnalyzeImageColors":"AnalyzeImageColors",
    "CalculateWeightedAverageColor": "CalculateWeightedAverageColor",
    "RecommendBackgroundColor": "RecommendBackgroundColor",
    "ResizeImgAndMaskPro": "Resize_img_and_mask_pro",
    "ResizeByRatioPro": "Resize_by_ratio_pro",
    "LayerTransform": "LayerTransform",
    "LayerTransformNoMask": "LayerTransformNoMask",
    "BboxSorter": "BboxSorter",
    "BboxContainer": "BboxContainer",
    "BboxMeasurement": "BboxMeasurement",
    "RegexProcessor": "RegexProcessor",
    "TextFileReader": "TextFileReader",
    "GPTConfigReader": "GPTConfigReader",
    "LoadImageFromURL": "LoadImageFromURL",
    "GroupRandomSelector": "GroupRandomSelector",
    "OpenAITextGenNode": "OpenAITextGenNode",
    "OpenAIVisionNode": "OpenAIVisionNode",
    "ImageBase64Node": "ImageBase64Node",
    "OpenAIVision2Node": "OpenAIVision2Node",
    "SaveTextNode": "SaveTextNode",
    "MosaicImage": "img_mosaic",
    "watermark_Mark": "Apply Invisible Watermark",
    "watermark_Extract": "Extract Watermark",
    "TranslateService": "TranslateService",
    "SaveImagePro": "SaveImagePro",
    "CropByRatioAndBBox": "Crop By Ratio And BBox",
    "WatermarkDetector": "Watermark Detection",
    "WatermarkCheck": "Watermark Check",
    "FluxKontextPro": "FLUX.1 Kontext Pro",
    "FluxKontextImg2Img": "FLUX.1 Kontext Img2Img",
    "FluxThirdPartyAPI": "FLUX Third Party API",
    "GPTThirdPartyAPI": "GPT Third Party API",
    "UploadImageNode": "Upload Image to CDN",
    "HtmlScreenshotNode": "HTML Screenshot Generator",
    "ApiResponseViewerNode": "API Response Viewer",
    "JsEditorNode": "JS Editor Runner",
    "HtmlFormatterNode": "HTML Formatter",
    "HtmlElementExtractorNode": "HTML Element Extractor",
    "HtmlAttributeModifierNode": "HTML Attribute Modifier",
    "HtmlExtractorNode": "HTML Extractor",
    "PPInfraGPTNode": "PPInfra GPT Chat",
    "GPTImageEditNode": "GPT Image Edit",
    "WanqingBboxDetectorNode": "wanqing_bbox_detector",
    "WanqingFlexibleAPINode": "wanqing_flexible_api",
    "WanQingGPTImageGeneration": "万擎 GPT 图像生成",
    "WanQingGPTImageEdit": "万擎 GPT 图像编辑",
    "QwenImageText2Img": "Qwen-Image 文本生成图像",
    "QwenImageEdit": "Qwen-Image 图像编辑",
    "JiMengTextToImage": "即梦文生图",
    "JiMengImageToImage": "即梦图生图",
    "WanQingJiMeng40TextToImage": "万擎即梦4.0文生图",
    "WanQingJiMeng40ImageToImage": "万擎即梦4.0图生图",
    "KolorsTextToImage": "可图文生图",
    "KolorsImageToImage": "可图图生图",
    "KolorsExpandImage": "可图扩图",
    "AzureOpenAIImageEdit": "Azure OpenAI 图像编辑",
    "AzureOpenAIText2Img": "Azure OpenAI 文生图",
    "KetuTextToImage": "可图文生图 (Ketu T2I)",
    "ImageOverlay": "Image Overlay",
    "XingYueSize": "星月尺寸",
    "Gemini25FlashImagePreview": "Gemini-2.5-Flash 图像预览",
    "JiMengMultiImageToImageV2": "即梦多图生图 V2",
    "QwenImageEditV2": "Qwen-Image 图像编辑 V2",
    "WanQingJiMeng40ImageToImageV2": "万擎即梦4.0图生图 V2",
    "WanQingJiMeng40TextToImageV2": "万擎即梦4.0文生图 V2",
    "KolorsTextToImageV2": "可图文生图 V2",
    "KolorsImageToImageV2": "可图图生图 V2",
    "KolorsExpandImageV2": "可图扩图 V2",
    "QwenImageText2ImgV2": "Qwen-Image 文本生成图像 V2",
    "JiMengImageToImageV2": "即梦图生图 V2",
    "KetuTextToImageV2": "可图文生图 V2 (Ketu T2I)",
    "GeminiImageNodeV2": "gemini-image-v2",
    "GeminiMultiImageAdvancedV2": "gemini-multi-image-advanced-v2",
    "AlphaCurveAdjust": "透明通道曲线调整",
    "ImageNormalBlendWithAlpha": "图像正常混合（保留透明）",
    "UnmultBlackBackground": "扣黑"
}

# 添加前端扩展目录
WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

