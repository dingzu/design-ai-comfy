import re

class HtmlExtractorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_response": ("STRING", {
                    "multiline": True,
                    "default": "好的,这里是一段简单的HTML代码:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>示例</title>\n</head>\n<body>\n    <h1>Hello World</h1>\n</body>\n</html>\n```\n\n这是一个HTML示例。",
                    "tooltip": "包含HTML代码块的文本响应"
                }),
            },
            "optional": {
                "extract_method": (["auto", "html_blocks", "all_code_blocks"], {
                    "default": "auto",
                    "tooltip": "提取方法：auto-自动检测HTML，html_blocks-仅HTML代码块，all_code_blocks-所有代码块"
                }),
                "merge_blocks": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否合并多个HTML代码块"
                }),
                "clean_output": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否清理输出（移除多余空行等）"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("extracted_html", "preview", "block_count", "extraction_info")
    FUNCTION = "extract_html"
    CATEGORY = "✨✨✨design-ai/utils"

    def extract_html(self, text_response, extract_method="auto", merge_blocks=True, clean_output=True):
        try:
            # 提取HTML代码块
            html_blocks = self._extract_html_blocks(text_response, extract_method)
            
            if not html_blocks:
                return ("", "未找到HTML代码块", 0, "提取失败：未找到任何HTML内容")
            
            # 处理多个代码块
            if merge_blocks and len(html_blocks) > 1:
                extracted_html = "\n\n<!-- === 合并的HTML代码块 === -->\n\n".join(html_blocks)
            else:
                extracted_html = html_blocks[0]  # 取第一个
            
            # 清理输出
            if clean_output:
                extracted_html = self._clean_html(extracted_html)
            
            # 生成预览
            preview = self._generate_preview(extracted_html)
            
            # 生成提取信息
            extraction_info = self._generate_extraction_info(html_blocks, extract_method)
            
            return (extracted_html, preview, len(html_blocks), extraction_info)
            
        except Exception as e:
            error_msg = f"HTML提取错误: {str(e)}"
            return ("", error_msg, 0, error_msg)

    def _extract_html_blocks(self, text, extract_method):
        """提取HTML代码块"""
        html_blocks = []
        
        if extract_method == "auto":
            # 自动检测，优先匹配HTML代码块，其次匹配包含HTML标签的代码块
            html_blocks = self._extract_by_auto(text)
        elif extract_method == "html_blocks":
            # 仅提取明确标记为HTML的代码块
            html_blocks = self._extract_html_code_blocks(text)
        elif extract_method == "all_code_blocks":
            # 提取所有代码块并检查是否包含HTML
            html_blocks = self._extract_all_code_blocks_with_html(text)
        
        return html_blocks

    def _extract_by_auto(self, text):
        """自动提取HTML代码块"""
        html_blocks = []
        
        # 1. 首先尝试提取明确标记为HTML的代码块
        html_code_blocks = self._extract_html_code_blocks(text)
        if html_code_blocks:
            html_blocks.extend(html_code_blocks)
        
        # 2. 如果没找到，尝试提取所有包含HTML标签的代码块
        if not html_blocks:
            all_blocks = self._extract_all_code_blocks_with_html(text)
            html_blocks.extend(all_blocks)
        
        # 3. 如果还是没找到，尝试直接从文本中提取HTML片段
        if not html_blocks:
            direct_html = self._extract_direct_html(text)
            if direct_html:
                html_blocks.append(direct_html)
        
        return html_blocks

    def _extract_html_code_blocks(self, text):
        """提取明确标记为HTML的代码块"""
        # 匹配 ```html ... ``` 格式的代码块
        pattern = r'```html\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return [match.strip() for match in matches if match.strip()]

    def _extract_all_code_blocks_with_html(self, text):
        """提取所有包含HTML标签的代码块"""
        html_blocks = []
        
        # 匹配所有代码块 ```... ```
        pattern = r'```(?:[a-zA-Z]*\s*)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in matches:
            content = match.strip()
            if self._contains_html_tags(content):
                html_blocks.append(content)
        
        return html_blocks

    def _extract_direct_html(self, text):
        """直接从文本中提取HTML片段"""
        # 查找可能的HTML文档结构
        patterns = [
            r'<!DOCTYPE html.*?</html>',  # 完整的HTML文档
            r'<html.*?</html>',           # HTML标签包围的内容
            r'<(?:div|section|article|main).*?</(?:div|section|article|main)>',  # 常见的HTML片段
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None

    def _contains_html_tags(self, text):
        """检查文本是否包含HTML标签"""
        # 检查常见的HTML标签
        html_tag_pattern = r'<(?:html|head|body|div|span|p|h[1-6]|a|img|ul|ol|li|table|tr|td|th|form|input|button|script|style|meta|title|link|section|article|nav|header|footer|main|aside)(?:\s[^>]*)?/?>'
        return bool(re.search(html_tag_pattern, text, re.IGNORECASE))

    def _clean_html(self, html_text):
        """清理HTML文本"""
        # 移除多余的空行
        lines = html_text.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_empty:
                    cleaned_lines.append('')
                    prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False
        
        # 移除开头和结尾的空行
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)

    def _generate_preview(self, html_text, max_lines=8, max_chars_per_line=60):
        """生成HTML预览"""
        if not html_text:
            return "无内容"
        
        lines = html_text.split('\n')
        preview_lines = []
        
        for i, line in enumerate(lines[:max_lines]):
            if len(line) > max_chars_per_line:
                truncated_line = line[:max_chars_per_line] + "..."
            else:
                truncated_line = line
            preview_lines.append(f"{i+1:2d}: {truncated_line}")
        
        if len(lines) > max_lines:
            preview_lines.append(f"... (还有 {len(lines) - max_lines} 行)")
        
        return '\n'.join(preview_lines)

    def _generate_extraction_info(self, html_blocks, extract_method):
        """生成提取信息"""
        info_lines = [
            f"提取方法: {extract_method}",
            f"找到代码块数量: {len(html_blocks)}",
        ]
        
        if html_blocks:
            total_chars = sum(len(block) for block in html_blocks)
            total_lines = sum(len(block.split('\n')) for block in html_blocks)
            info_lines.extend([
                f"总字符数: {total_chars}",
                f"总行数: {total_lines}",
            ])
            
            # 检测HTML文档类型
            first_block = html_blocks[0]
            if '<!DOCTYPE html' in first_block:
                info_lines.append("类型: 完整HTML文档")
            elif '<html' in first_block:
                info_lines.append("类型: HTML片段")
            else:
                info_lines.append("类型: HTML代码片段")
        
        return '\n'.join(info_lines) 