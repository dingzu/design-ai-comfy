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
from .coordinate_sorter import CoordinateSorter
from .angle_calculator import AngleCalculator
from .transform_bbox import TransformBbox
from .filter_bbox import FilterBbox
from .color_name_generator import ColorNameGenerator
from .analyze_image_colors import AnalyzeImageColors
from .calculate_weighted_average_color import CalculateWeightedAverageColor
from .recommend_background_color import RecommendBackgroundColor
from .resize_img_and_mask_pro import ResizeImgAndMaskPro
from .layer_transform import LayerTransform
from .layer_transform_no_mask import LayerTransformNoMask
from .bbox_sorter import BboxSorter
from .bbox_container import BboxContainer
from .bbox_measurement import BboxMeasurement
from .regex_processor import RegexProcessor
from .text_file_reader import TextFileReader, GPTConfigReader
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
    "CoordinateSorter":CoordinateSorter,
    "AngleCalculator":AngleCalculator,
    "TransformBbox":TransformBbox,
    "FilterBbox":FilterBbox,
    "ColorNameGenerator":ColorNameGenerator,
    "AnalyzeImageColors":AnalyzeImageColors,
    "CalculateWeightedAverageColor": CalculateWeightedAverageColor,
    "RecommendBackgroundColor": RecommendBackgroundColor,
    "ResizeImgAndMaskPro": ResizeImgAndMaskPro,
    "LayerTransform": LayerTransform,
    "LayerTransformNoMask": LayerTransformNoMask,
    "BboxSorter":BboxSorter,
    "BboxContainer":BboxContainer,
    "BboxMeasurement":BboxMeasurement,
    "RegexProcessor":RegexProcessor,
    "TextFileReader": TextFileReader,
    "GPTConfigReader": GPTConfigReader,
    "LoadImageFromURL":LoadImageFromURL,
    "GroupRandomSelector":GroupRandomSelector,
    "OpenAITextGenNode": OpenAITextGenNode,
    "OpenAIVisionNode": OpenAIVisionNode,
    "ImageBase64": ImageBase64Node,
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
    "GPTImageEditNode": GPTImageEditNode
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
    "CoordinateSorter": "CoordinateSorter",
    "AngleCalculator": "AngleCalculator",
    "TransformBbox": "TransformBbox",
    "FilterBbox":"FilterBbox",
    "ColorNameGenerator": "ColorNameGenerator",
    "AnalyzeImageColors":"AnalyzeImageColors",
    "CalculateWeightedAverageColor": "CalculateWeightedAverageColor",
    "RecommendBackgroundColor": "RecommendBackgroundColor",
    "ResizeImgAndMaskPro": "Resize_img_and_mask_pro",
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
    "GPTImageEditNode": "GPT Image Edit"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

