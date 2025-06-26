import re
from typing import List, Tuple, Optional

class HtmlElementExtractorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "html_content": ("STRING", {
                    "multiline": True,
                    "default": "<div>\n  <img src=\"image1.jpg\" alt=\"相关图像描述\" prompt=\"生成一个关于讲师培训的相关图片。\" img-number=\"1\">\n  <img src=\"image2.jpg\" alt=\"相关图像描述\" prompt=\"生成一个关于潜力学员的相关图片。\" img-number=\"2\">\n  <div prompt=\"测试内容\">这是一个包含内容的div</div>\n</div>",
                    "tooltip": "输入HTML内容"
                }),
                "target_attribute": ("STRING", {
                    "default": "prompt",
                    "tooltip": "要识别的目标属性名（如：prompt、data-id等）"
                }),
            },
            "optional": {
                "index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 999,
                    "step": 1,
                    "tooltip": "返回特定索引的元素（-1返回所有元素）"
                }),
                "include_attributes": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否在结果中包含所有属性"
                }),
                "extract_attribute_value": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否只提取目标属性的值"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("elements_array", "selected_element", "total_count", "attribute_values")
    FUNCTION = "extract_elements"
    CATEGORY = "✨✨✨design-ai/utils"

    def extract_elements(self, html_content, target_attribute, index=-1, include_attributes=True, extract_attribute_value=False):
        try:
            # 提取所有包含目标属性的元素
            elements = self._find_elements_with_attribute(html_content, target_attribute)
            
            # 处理元素内容
            processed_elements = []
            attribute_values = []
            
            for element in elements:
                if extract_attribute_value:
                    # 只提取属性值
                    attr_value = self._extract_attribute_value(element, target_attribute)
                    attribute_values.append(attr_value)
                else:
                    # 提取完整元素
                    if include_attributes:
                        processed_elements.append(element)
                    else:
                        # 移除所有属性，只保留标签和内容
                        clean_element = self._remove_attributes(element)
                        processed_elements.append(clean_element)
                    
                    # 同时提取属性值
                    attr_value = self._extract_attribute_value(element, target_attribute)
                    attribute_values.append(attr_value)
            
            # 生成数组字符串
            if extract_attribute_value:
                elements_array = str(attribute_values)
            else:
                elements_array = str(processed_elements)
            
            # 获取总数
            total_count = len(elements if extract_attribute_value else processed_elements)
            
            # 获取特定索引的元素
            selected_element = ""
            if index >= 0 and index < total_count:
                if extract_attribute_value:
                    selected_element = attribute_values[index]
                else:
                    selected_element = processed_elements[index]
            elif index == -1 and total_count > 0:
                if extract_attribute_value:
                    selected_element = str(attribute_values)
                else:
                    selected_element = str(processed_elements)
            
            # 属性值数组
            attribute_values_str = str(attribute_values)
            
            return (elements_array, selected_element, total_count, attribute_values_str)
            
        except Exception as e:
            error_msg = f"HTML元素提取错误: {str(e)}"
            return ("[]", error_msg, 0, "[]")

    def _find_elements_with_attribute(self, html_content: str, target_attribute: str) -> List[str]:
        """查找所有包含目标属性的HTML元素"""
        elements = []
        
        # 匹配包含目标属性的开始标签
        # 支持自闭合标签和有结束标签的元素
        pattern = rf'<([a-zA-Z][a-zA-Z0-9]*)[^>]*\b{re.escape(target_attribute)}=[^>]*/?>'
        
        for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag_name = match.group(1).lower()
            start_pos = match.start()
            
            # 检查是否是自闭合标签
            if match.group(0).endswith('/>'):
                # 自闭合标签
                elements.append(match.group(0))
            else:
                # 查找对应的结束标签
                end_tag_pattern = rf'</{re.escape(tag_name)}>'
                end_match = re.search(end_tag_pattern, html_content[match.end():], re.IGNORECASE)
                
                if end_match:
                    # 找到结束标签，提取完整元素
                    end_pos = match.end() + end_match.end()
                    full_element = html_content[start_pos:end_pos]
                    elements.append(full_element)
                else:
                    # 没有找到结束标签，可能是自闭合标签或HTML片段
                    elements.append(match.group(0))
        
        return elements

    def _extract_attribute_value(self, element: str, attribute: str) -> str:
        """从元素中提取指定属性的值"""
        # 匹配属性值（支持单引号、双引号或无引号）
        pattern = rf'\b{re.escape(attribute)}=(["\']?)([^"\'\s>]*)\1'
        match = re.search(pattern, element, re.IGNORECASE)
        
        if match:
            return match.group(2)
        return ""

    def _remove_attributes(self, element: str) -> str:
        """移除元素的所有属性，只保留标签名和内容"""
        # 匹配开始标签
        start_tag_pattern = r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>'
        start_match = re.search(start_tag_pattern, element)
        
        if not start_match:
            return element
        
        tag_name = start_match.group(1)
        
        # 检查是否是自闭合标签
        if element.strip().endswith('/>'):
            return f'<{tag_name}/>'
        
        # 查找结束标签
        end_tag_pattern = rf'</{re.escape(tag_name)}>'
        end_match = re.search(end_tag_pattern, element, re.IGNORECASE)
        
        if end_match:
            # 提取内容
            content_start = start_match.end()
            content_end = end_match.start()
            content = element[content_start:content_end]
            return f'<{tag_name}>{content}</{tag_name}>'
        else:
            # 没有结束标签
            return f'<{tag_name}>'

    def _format_elements_as_array(self, elements: List[str]) -> str:
        """将元素列表格式化为数组字符串"""
        if not elements:
            return "[]"
        
        # 转义引号并格式化
        formatted_elements = []
        for element in elements:
            # 转义双引号
            escaped = element.replace('"', '\\"')
            formatted_elements.append(f'"{escaped}"')
        
        return f"[{', '.join(formatted_elements)}]" 