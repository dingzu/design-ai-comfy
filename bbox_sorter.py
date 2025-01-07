import torch
import numpy as np

class BboxSorter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bbox_list": ("STRING",),  # 输入的边界框字符串
                "sort_mode": (["top_to_bottom", "left_to_right", "area"],), # 排序模式
                "primary_direction": (["vertical", "horizontal"],), # 主要排序方向
            },
        }

    RETURN_NAMES = ("sorted_bbox", "sorted_indices")
    RETURN_TYPES = ("STRING", "STRING",)
    FUNCTION = "sort_bbox"
    CATEGORY = "✨✨✨design-ai/bbox"

    def sort_bbox(self, bbox_list, sort_mode="top_to_bottom", primary_direction="vertical"):
        # 解析边界框字符串为列表
        bboxes = eval(bbox_list)
        
        # 如果没有bbox数据,返回空结果
        if not bboxes:
            return ("[]", "[]")

        # 将嵌套列表展平成单层列表
        flat_bboxes = []
        for bbox_group in bboxes:
            for bbox in bbox_group:
                flat_bboxes.append(bbox)

        # 将bbox转换为numpy数组便于计算
        bboxes_array = np.array(flat_bboxes)
        
        if sort_mode == "area":
            # 计算每个bbox的面积
            areas = (bboxes_array[:,2] - bboxes_array[:,0]) * (bboxes_array[:,3] - bboxes_array[:,1])
            # 按面积排序
            indices = np.argsort(areas)[::-1]  # 降序排列
            
        else:
            # 计算每个bbox的中心点
            centers = np.zeros((len(flat_bboxes), 2))
            centers[:,0] = (bboxes_array[:,0] + bboxes_array[:,2]) / 2  # x center
            centers[:,1] = (bboxes_array[:,1] + bboxes_array[:,3]) / 2  # y center

            if primary_direction == "vertical":
                if sort_mode == "top_to_bottom":
                    # 首先按y坐标排序,y相同时按x坐标排序
                    indices = np.lexsort((centers[:,0], centers[:,1]))
                else:  # left_to_right
                    # 首先按x坐标排序,x相同时按y坐标排序
                    indices = np.lexsort((centers[:,1], centers[:,0]))
            else:  # horizontal
                if sort_mode == "left_to_right":
                    # 首先按x坐标排序,x相同时按y坐标排序
                    indices = np.lexsort((centers[:,1], centers[:,0]))
                else:  # top_to_bottom
                    # 首先按y坐标排序,y相同时按x坐标排序
                    indices = np.lexsort((centers[:,0], centers[:,1]))

        # 根据排序索引重排bbox
        sorted_bboxes = [flat_bboxes[i] for i in indices]
        
        # 转换回字符串格式
        sorted_bboxes_str = str([sorted_bboxes])  # 包装成与输入格式一致的嵌套列表
        indices_str = str(indices.tolist())

        return (sorted_bboxes_str, indices_str)