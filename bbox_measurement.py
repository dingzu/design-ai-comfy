import torch
import numpy as np

class BboxMeasurement:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bbox_list": ("STRING",),  # 输入的边界框字符串
                "return_format": (["single", "all"],), # 返回单个总结果还是所有bbox的结果
            },
        }

    RETURN_NAMES = ("width", "height", "area", "measurements", "statistics")
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "STRING",)
    FUNCTION = "measure_bbox"
    CATEGORY = "✨✨✨design-ai/bbox"

    def measure_bbox(self, bbox_list, return_format="single"):
        try:
            # 解析边界框字符串为列表
            bboxes = eval(bbox_list)
            
            # 如果没有bbox数据,返回零值结果
            if not bboxes:
                return (0, 0, 0, "[]", "{}")

            # 将嵌套列表展平成单层列表
            flat_bboxes = []
            for bbox_group in bboxes:
                for bbox in bbox_group:
                    flat_bboxes.append(bbox)

            # 将bbox转换为numpy数组便于计算
            bboxes_array = np.array(flat_bboxes)
            
            # 计算每个bbox的测量结果
            measurements = []
            widths = []
            heights = []
            areas = []

            for bbox in flat_bboxes:
                x1, y1, x2, y2 = bbox
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                area = width * height
                
                widths.append(width)
                heights.append(height)
                areas.append(area)
                
                measurements.append({
                    "bbox": bbox,
                    "width": width,
                    "height": height,
                    "area": area,
                    "aspect_ratio": width / height if height != 0 else 0
                })

            # 计算统计信息
            statistics = {
                "total_count": len(flat_bboxes),
                "width_stats": {
                    "min": int(np.min(widths)),
                    "max": int(np.max(widths)),
                    "mean": float(np.mean(widths)),
                    "median": float(np.median(widths))
                },
                "height_stats": {
                    "min": int(np.min(heights)),
                    "max": int(np.max(heights)),
                    "mean": float(np.mean(heights)),
                    "median": float(np.median(heights))
                },
                "area_stats": {
                    "min": int(np.min(areas)),
                    "max": int(np.max(areas)),
                    "mean": float(np.mean(areas)),
                    "median": float(np.median(areas)),
                    "total": int(np.sum(areas))
                }
            }

            if return_format == "single":
                # 返回所有bbox的总体尺寸
                total_width = int(np.max(bboxes_array[:, 2]) - np.min(bboxes_array[:, 0]))
                total_height = int(np.max(bboxes_array[:, 3]) - np.min(bboxes_array[:, 1]))
                total_area = total_width * total_height
                
                return (
                    total_width,
                    total_height,
                    total_area,
                    str(measurements),
                    str(statistics)
                )
            else:
                # 返回第一个bbox的尺寸（与返回类型保持一致）
                return (
                    measurements[0]["width"],
                    measurements[0]["height"],
                    measurements[0]["area"],
                    str(measurements),
                    str(statistics)
                )

        except Exception as e:
            print(f"Error measuring bboxes: {str(e)}")
            return (0, 0, 0, "[]", "{}")

    def format_number(self, num):
        """格式化数字，保留两位小数"""
        return round(float(num), 2)