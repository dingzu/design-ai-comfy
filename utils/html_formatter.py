import re

class HtmlFormatterNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "escaped_html": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "输入转义的HTML文本（包含\\n等转义字符）"
                }),
            },
            "optional": {
                "auto_format": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否自动格式化HTML（添加缩进）"
                }),
                "indent_size": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 8,
                    "step": 1,
                    "tooltip": "缩进空格数量"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("formatted_html", "preview", "line_count")
    FUNCTION = "format_html"
    CATEGORY = "✨✨✨design-ai/utils"

    def format_html(self, escaped_html, auto_format=True, indent_size=2):
        try:
            # 处理转义字符
            formatted_html = self._unescape_html(escaped_html)
            
            # 如果启用自动格式化
            if auto_format:
                formatted_html = self._auto_format_html(formatted_html, indent_size)
            
            # 计算行数
            line_count = len(formatted_html.split('\n'))
            
            # 生成预览（限制长度）
            preview = self._generate_preview(formatted_html)
            
            return (formatted_html, preview, line_count)
            
        except Exception as e:
            error_msg = f"HTML格式化错误: {str(e)}"
            return (escaped_html, error_msg, 1)

    def _unescape_html(self, escaped_text):
        """处理转义字符"""
        # 替换常见的转义字符
        replacements = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\"': '"',
            "\\'": "'",
            '\\\\': '\\',
        }
        
        result = escaped_text
        for escaped, unescaped in replacements.items():
            result = result.replace(escaped, unescaped)
        
        return result

    def _auto_format_html(self, html_text, indent_size):
        """自动格式化HTML"""
        try:
            lines = html_text.split('\n')
            formatted_lines = []
            indent_level = 0
            
            # HTML标签配对
            opening_tags = ['html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                           'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'script', 'style', 'section', 
                           'article', 'nav', 'header', 'footer', 'main', 'aside']
            
            self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 
                               'source', 'track', 'wbr']
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append('')
                    continue
                
                # 检查是否是结束标签
                if stripped.startswith('</'):
                    indent_level = max(0, indent_level - 1)
                
                # 添加当前行（带缩进）
                indent = ' ' * (indent_level * indent_size)
                formatted_lines.append(indent + stripped)
                
                # 检查是否是开始标签（不是自闭合标签）
                if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                    # 提取标签名
                    tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', stripped)
                    if tag_match:
                        tag_name = tag_match.group(1).lower()
                        if tag_name in opening_tags and tag_name not in self_closing_tags:
                            # 检查是否在同一行就有结束标签
                            if f'</{tag_name}>' not in stripped:
                                indent_level += 1
            
            return '\n'.join(formatted_lines)
            
        except Exception:
            # 如果自动格式化失败，返回原始文本
            return html_text

    def _generate_preview(self, html_text, max_lines=10, max_chars_per_line=80):
        """生成HTML预览"""
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