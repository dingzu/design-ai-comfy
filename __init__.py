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
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

