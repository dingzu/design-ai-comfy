import re
import numpy as np

class RegexProcessor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING",),  # 输入的字符串
                "regex_pattern": ("STRING",),  # 正则表达式模式
            },
        }

    RETURN_NAMES = ("matches", "match_indices")
    RETURN_TYPES = ("STRING", "STRING",)
    FUNCTION = "process_regex"
    CATEGORY = "✨✨✨design-ai/logic"

    def process_regex(self, input_string, regex_pattern):
        # 编译正则表达式
        pattern = re.compile(regex_pattern)
        
        # 查找所有匹配项
        matches = pattern.findall(input_string)
        
        # 获取匹配项的起始和结束位置
        match_indices = [m.span() for m in pattern.finditer(input_string)]
        
        # 转换为字符串格式
        matches_str = str(matches)
        match_indices_str = str(match_indices)

        return (matches_str, match_indices_str)