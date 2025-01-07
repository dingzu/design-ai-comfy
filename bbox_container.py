import torch
import numpy as np

class BboxContainer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bbox_list": ("STRING",),  # 输入的边界框字符串
                "canvas_width": ("INT", {"default": 512, "min": 1, "max": 4096}),  # 画布宽度
                "canvas_height": ("INT", {"default": 512, "min": 1, "max": 4096}),  # 画布高度
                "padding": ("INT", {"default": 0, "min": 0, "max": 1000}),  # padding值
            },
        }

    RETURN_NAMES = ("container_bbox", "adjusted_bboxes", "is_valid")
    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN",)
    FUNCTION = "create_container"
    CATEGORY = "✨✨✨design-ai/bbox"

    def create_container(self, bbox_list, canvas_width=512, canvas_height=512, padding=0):
        try:
            # 解析边界框字符串为列表
            bboxes = eval(bbox_list)
            
            # 如果没有bbox数据,返回空结果和画布大小的容器
            if not bboxes:
                container = [0, 0, canvas_width, canvas_height]
                return (str([container]), "[]", True)

            # 将嵌套列表展平成单层列表
            flat_bboxes = []
            for bbox_group in bboxes:
                for bbox in bbox_group:
                    flat_bboxes.append(bbox)

            # 将bbox转换为numpy数组便于计算
            bboxes_array = np.array(flat_bboxes)
            
            # 计算所有bbox的最小和最大坐标
            min_x = np.min(bboxes_array[:, 0])
            min_y = np.min(bboxes_array[:, 1])
            max_x = np.max(bboxes_array[:, 2])
            max_y = np.max(bboxes_array[:, 3])

            # 添加padding
            container_x1 = max(0, min_x - padding)
            container_y1 = max(0, min_y - padding)
            container_x2 = min(canvas_width, max_x + padding)
            container_y2 = min(canvas_height, max_y + padding)

            # 创建容器bbox
            container_bbox = [container_x1, container_y1, container_x2, container_y2]

            # 调整所有bbox确保在画布范围内
            adjusted_bboxes = []
            for bbox in flat_bboxes:
                adj_bbox = [
                    max(0, min(bbox[0], canvas_width)),
                    max(0, min(bbox[1], canvas_height)),
                    max(0, min(bbox[2], canvas_width)),
                    max(0, min(bbox[3], canvas_height))
                ]
                # 确保bbox有效(宽高都大于0)
                if adj_bbox[2] > adj_bbox[0] and adj_bbox[3] > adj_bbox[1]:
                    adjusted_bboxes.append(adj_bbox)

            # 检查调整后的bbox是否都在容器内
            is_valid = True
            for bbox in adjusted_bboxes:
                if not (container_bbox[0] <= bbox[0] and
                       container_bbox[1] <= bbox[1] and
                       container_bbox[2] >= bbox[2] and
                       container_bbox[3] >= bbox[3]):
                    is_valid = False
                    break

            return (
                str([container_bbox]),  # 包装成与输入格式一致的嵌套列表
                str([adjusted_bboxes]),
                is_valid
            )

        except Exception as e:
            print(f"Error processing bboxes: {str(e)}")
            # 发生错误时返回画布大小的容器
            container = [0, 0, canvas_width, canvas_height]
            return (str([container]), "[]", False)

    def validate_bbox(self, bbox, canvas_width, canvas_height):
        """验证bbox是否有效"""
        x1, y1, x2, y2 = bbox
        # 检查坐标是否在画布范围内
        if x1 < 0 or y1 < 0 or x2 > canvas_width or y2 > canvas_height:
            return False
        # 检查bbox大小是否有效
        if x2 <= x1 or y2 <= y1:
            return False
        return True