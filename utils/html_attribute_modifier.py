import re
from typing import List, Tuple, Optional

class HtmlAttributeModifierNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "html_content": ("STRING", {
                    "multiline": True,
                    "default": "<img src=\"image1.jpg\" alt=\"相关图像描述\" prompt=\"生成一个关于讲师培训的相关图片。\" img-number=\"1\">",
                    "tooltip": "输入HTML内容"
                }),
                "target_attribute": ("STRING", {
                    "default": "prompt",
                    "tooltip": "要修改的目标属性名（如：prompt、data-id、class等）"
                }),
                "new_value": ("STRING", {
                    "default": "新的属性值",
                    "tooltip": "属性的新值"
                }),
            },
            "optional": {
                "element_selector": ("STRING", {
                    "default": "",
                    "tooltip": "元素选择器（如：img、div[class='test']），留空则修改所有包含目标属性的元素"
                }),
                "inner_content": ("STRING", {
                    "default": "",
                    "tooltip": "要设置的内部内容（仅对非自闭合标签有效）"
                }),
                "element_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 999,
                    "step": 1,
                    "tooltip": "要修改的元素索引（-1修改所有匹配的元素）"
                }),
                "add_if_not_exists": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "如果属性不存在是否添加"
                }),
                "preserve_formatting": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否保持原有的格式化"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("modified_html", "operation_log", "modified_count")
    FUNCTION = "modify_attributes"
    CATEGORY = "✨✨✨design-ai/utils"

    def modify_attributes(self, html_content, target_attribute, new_value, element_selector="", inner_content="", element_index=-1, add_if_not_exists=True, preserve_formatting=True):
        try:
            modified_html = html_content
            operation_log = []
            modified_count = 0
            
            # 如果指定了元素选择器，使用选择器匹配
            if element_selector.strip():
                elements = self._find_elements_by_selector(html_content, element_selector)
            else:
                # 查找所有包含目标属性的元素，或者所有元素（如果要添加属性）
                if add_if_not_exists:
                    elements = self._find_all_elements(html_content)
                else:
                    elements = self._find_elements_with_attribute(html_content, target_attribute)
            
            # 如果指定了索引，只处理特定元素
            if element_index >= 0 and element_index < len(elements):
                elements = [elements[element_index]]
            
            # 按位置从后往前处理，避免位置偏移
            elements.sort(key=lambda x: x['start'], reverse=True)
            
            for element in elements:
                original_element = element['content']
                new_element = original_element
                
                # 修改属性
                if self._has_attribute(original_element, target_attribute):
                    # 属性已存在，修改值
                    new_element = self._modify_attribute_value(new_element, target_attribute, new_value)
                    operation_log.append(f"修改属性 {target_attribute}: '{self._get_attribute_value(original_element, target_attribute)}' -> '{new_value}'")
                elif add_if_not_exists:
                    # 属性不存在，添加属性
                    new_element = self._add_attribute(new_element, target_attribute, new_value)
                    operation_log.append(f"添加属性 {target_attribute}: '{new_value}'")
                
                # 修改内部内容
                if inner_content.strip() and not self._is_self_closing(original_element):
                    new_element = self._set_inner_content(new_element, inner_content)
                    operation_log.append(f"设置内部内容: '{inner_content}'")
                
                # 替换原始HTML中的元素
                if new_element != original_element:
                    start_pos = element['start']
                    end_pos = element['end']
                    modified_html = modified_html[:start_pos] + new_element + modified_html[end_pos:]
                    modified_count += 1
            
            # 生成操作日志
            log_text = f"操作完成，修改了 {modified_count} 个元素:\n" + "\n".join(operation_log) if operation_log else "未找到匹配的元素或无需修改"
            
            return (modified_html, log_text, modified_count)
            
        except Exception as e:
            error_msg = f"HTML属性修改错误: {str(e)}"
            return (html_content, error_msg, 0)

    def _find_elements_by_selector(self, html_content: str, selector: str) -> List[dict]:
        """根据选择器查找元素"""
        elements = []
        
        # 简单的选择器解析（支持标签名和属性选择器）
        if '[' in selector and ']' in selector:
            # 属性选择器，如：div[class='test']
            tag_match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)\[([^=]+)=[\'"]*([^\'\"]*?)[\'"]*\]$', selector.strip())
            if tag_match:
                tag_name = tag_match.group(1)
                attr_name = tag_match.group(2)
                attr_value = tag_match.group(3)
                pattern = rf'<{re.escape(tag_name)}\b[^>]*\b{re.escape(attr_name)}=(["\']?){re.escape(attr_value)}\1[^>]*/?>'
            else:
                return elements
        else:
            # 简单标签选择器
            tag_name = selector.strip()
            pattern = rf'<{re.escape(tag_name)}\b[^>]*/?>'
        
        for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag_name_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', match.group(0))
            if tag_name_match:
                tag_name = tag_name_match.group(1).lower()
                start_pos = match.start()
                
                if match.group(0).endswith('/>'):
                    # 自闭合标签
                    elements.append({
                        'content': match.group(0),
                        'start': start_pos,
                        'end': match.end()
                    })
                else:
                    # 查找结束标签
                    end_tag_pattern = rf'</{re.escape(tag_name)}>'
                    end_match = re.search(end_tag_pattern, html_content[match.end():], re.IGNORECASE)
                    
                    if end_match:
                        end_pos = match.end() + end_match.end()
                        full_element = html_content[start_pos:end_pos]
                        elements.append({
                            'content': full_element,
                            'start': start_pos,
                            'end': end_pos
                        })
                    else:
                        elements.append({
                            'content': match.group(0),
                            'start': start_pos,
                            'end': match.end()
                        })
        
        return elements

    def _find_all_elements(self, html_content: str) -> List[dict]:
        """查找所有HTML元素"""
        elements = []
        pattern = r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*/?>'
        
        for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag_name = match.group(1).lower()
            start_pos = match.start()
            
            if match.group(0).endswith('/>'):
                # 自闭合标签
                elements.append({
                    'content': match.group(0),
                    'start': start_pos,
                    'end': match.end()
                })
            else:
                # 查找结束标签
                end_tag_pattern = rf'</{re.escape(tag_name)}>'
                end_match = re.search(end_tag_pattern, html_content[match.end():], re.IGNORECASE)
                
                if end_match:
                    end_pos = match.end() + end_match.end()
                    full_element = html_content[start_pos:end_pos]
                    elements.append({
                        'content': full_element,
                        'start': start_pos,
                        'end': end_pos
                    })
                else:
                    elements.append({
                        'content': match.group(0),
                        'start': start_pos,
                        'end': match.end()
                    })
        
        return elements

    def _find_elements_with_attribute(self, html_content: str, target_attribute: str) -> List[dict]:
        """查找包含特定属性的元素"""
        elements = []
        pattern = rf'<([a-zA-Z][a-zA-Z0-9]*)[^>]*\b{re.escape(target_attribute)}=[^>]*/?>'
        
        for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
            tag_name = match.group(1).lower()
            start_pos = match.start()
            
            if match.group(0).endswith('/>'):
                # 自闭合标签
                elements.append({
                    'content': match.group(0),
                    'start': start_pos,
                    'end': match.end()
                })
            else:
                # 查找结束标签
                end_tag_pattern = rf'</{re.escape(tag_name)}>'
                end_match = re.search(end_tag_pattern, html_content[match.end():], re.IGNORECASE)
                
                if end_match:
                    end_pos = match.end() + end_match.end()
                    full_element = html_content[start_pos:end_pos]
                    elements.append({
                        'content': full_element,
                        'start': start_pos,
                        'end': end_pos
                    })
                else:
                    elements.append({
                        'content': match.group(0),
                        'start': start_pos,
                        'end': match.end()
                    })
        
        return elements

    def _has_attribute(self, element: str, attribute: str) -> bool:
        """检查元素是否包含指定属性"""
        pattern = rf'\b{re.escape(attribute)}='
        return bool(re.search(pattern, element, re.IGNORECASE))

    def _get_attribute_value(self, element: str, attribute: str) -> str:
        """获取属性值"""
        pattern = rf'\b{re.escape(attribute)}=(["\']?)([^"\'\s>]*)\1'
        match = re.search(pattern, element, re.IGNORECASE)
        return match.group(2) if match else ""

    def _modify_attribute_value(self, element: str, attribute: str, new_value: str) -> str:
        """修改属性值"""
        pattern = rf'(\b{re.escape(attribute)}=)(["\']?)([^"\'\s>]*)\2'
        
        def replace_func(match):
            quote = match.group(2) or '"'
            return f'{match.group(1)}{quote}{new_value}{quote}'
        
        return re.sub(pattern, replace_func, element, flags=re.IGNORECASE)

    def _add_attribute(self, element: str, attribute: str, value: str) -> str:
        """添加属性"""
        # 查找开始标签的结束位置
        if element.endswith('/>'):
            # 自闭合标签
            insert_pos = element.rfind('/>')
            return element[:insert_pos] + f' {attribute}="{value}"' + element[insert_pos:]
        else:
            # 普通标签
            tag_end = element.find('>')
            if tag_end != -1:
                return element[:tag_end] + f' {attribute}="{value}"' + element[tag_end:]
        
        return element

    def _is_self_closing(self, element: str) -> bool:
        """检查是否是自闭合标签"""
        return element.strip().endswith('/>')

    def _set_inner_content(self, element: str, content: str) -> str:
        """设置元素的内部内容"""
        # 查找开始标签和结束标签
        start_tag_end = element.find('>')
        if start_tag_end == -1:
            return element
        
        # 提取标签名
        tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', element)
        if not tag_match:
            return element
        
        tag_name = tag_match.group(1)
        end_tag_pattern = rf'</{re.escape(tag_name)}>'
        end_tag_match = re.search(end_tag_pattern, element, re.IGNORECASE)
        
        if end_tag_match:
            # 有结束标签，替换内容
            start_content = start_tag_end + 1
            end_content = end_tag_match.start()
            return element[:start_content] + content + element[end_content:]
        else:
            # 没有结束标签，添加内容和结束标签
            return element + content + f'</{tag_name}>' 