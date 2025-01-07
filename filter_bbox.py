import torch
import numpy as np

class FilterBbox:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_bbox": ("STRING",),  # 输入的A边界框字符串
                "filter_bbox": ("STRING",),  # 输入的B边界框字符串
            },
        }

    RETURN_NAMES = ("bbox","point_list")
    RETURN_TYPES = ("STRING", "STRING",)
    FUNCTION = "filter_bbox"
    CATEGORY = "✨✨✨design-ai/bbox"

    def filter_bbox(self, base_bbox, filter_bbox):
        # 解析边界框字符串为列表
        base_bbox = eval(base_bbox)
        filter_bbox = eval(filter_bbox)

        # 如果没有任何 bbox 数据，返回空字符串
        if not base_bbox or not filter_bbox:
            return ("[]", "[]",)

        # Initialize lists to store filtered bboxes and their vertices
        filtered_bboxes = []
        filtered_vertices = []

        # Iterate over each bbox in A and check if it is within any bbox in B
        for a_bbox_list in base_bbox:
            for a_bbox in a_bbox_list:
                a_x1, a_y1, a_x2, a_y2 = a_bbox

                # Define the four vertices of the A bbox
                a_vertices = [
                    [a_x1, a_y1],
                    [a_x2, a_y1],
                    [a_x2, a_y2],
                    [a_x1, a_y2]
                ]

                for b_bbox_list in filter_bbox:
                    for b_bbox in b_bbox_list:
                        b_x1, b_y1, b_x2, b_y2 = b_bbox

                        # Check if all vertices of A bbox are within B bbox
                        if all(b_x1 <= x <= b_x2 and b_y1 <= y <= b_y2 for x, y in a_vertices):
                            filtered_bboxes.append(a_bbox)
                            filtered_vertices.append(a_vertices)
                            break

        # Convert the lists to strings
        filtered_bboxes_str = str(filtered_bboxes)
        filtered_vertices_str = str(filtered_vertices)

        return (filtered_bboxes_str, filtered_vertices_str,)