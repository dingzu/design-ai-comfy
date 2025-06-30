import re
import json
import copy
from typing import Any, Union

class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class ChainReplacer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_data": (any, {"default": ""}),
                "access_path": ("STRING", {"default": "input[0]['a']", "multiline": False}),
                "new_value": (any, {"default": ""}),
            }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("result",)
    FUNCTION = "chain_replace"
    CATEGORY = "✨✨✨design-ai/logic"

    def chain_replace(self, input_data, access_path, new_value):
        """
        支持链式替换数据结构中某个属性的节点
        
        功能:
        - 支持链式访问和替换: input[1]["a"][1]["c"] = new_value
        - 支持深度复制，不修改原始数据
        - 支持字符串JSON的解析和重新序列化
        - 自动处理各种数据类型的转换
        
        示例:
        - input[1]["a"][1]["c"] = "new_value"
        - input[0] = {"new": "object"}
        - input["key"] = [1, 2, 3]
        """
        try:
            # 深度复制原始数据，避免修改输入
            if isinstance(input_data, str):
                try:
                    data = json.loads(input_data)
                    is_json_string = True
                except json.JSONDecodeError:
                    # 如果不是有效JSON，尝试eval（谨慎使用）
                    try:
                        data = eval(input_data)
                        is_json_string = False
                    except:
                        data = input_data
                        is_json_string = False
            else:
                data = copy.deepcopy(input_data)
                is_json_string = False

            # 处理new_value的类型转换
            processed_new_value = self._process_new_value(new_value)
            
            # 替换指定路径的值
            self._replace_at_path(data, access_path, processed_new_value)
            
            # 如果原始输入是JSON字符串，返回JSON字符串
            if is_json_string and not isinstance(input_data, (list, dict)):
                return (json.dumps(data, ensure_ascii=False),)
            else:
                return (data,)

        except Exception as e:
            return (f"Error: {str(e)}",)

    def _process_new_value(self, new_value):
        """处理新值的类型转换"""
        # 如果new_value是字符串且看起来像JSON，尝试解析
        if isinstance(new_value, str):
            new_value = new_value.strip()
            # 检查是否是JSON对象或数组
            if (new_value.startswith('{') and new_value.endswith('}')) or \
               (new_value.startswith('[') and new_value.endswith(']')):
                try:
                    return json.loads(new_value)
                except json.JSONDecodeError:
                    pass
            # 检查是否是特殊值
            elif new_value.lower() == 'null':
                return None
            elif new_value.lower() == 'true':
                return True
            elif new_value.lower() == 'false':
                return False
            # 检查是否是数字
            elif new_value.isdigit() or (new_value.startswith('-') and new_value[1:].isdigit()):
                return int(new_value)
            elif self._is_float(new_value):
                return float(new_value)
        
        return new_value

    def _is_float(self, value):
        """检查字符串是否为浮点数"""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False

    def _replace_at_path(self, data, path, new_value):
        """在指定路径替换值"""
        # 替换 'input' 为实际数据的引用
        if not path.startswith('input'):
            raise ValueError(f"Path must start with 'input': {path}")
        
        # 解析路径并找到目标位置
        path_segments = self._parse_path_segments(path[5:])  # 移除 'input'
        
        if not path_segments:
            # 如果没有路径段，说明要替换整个input
            raise ValueError("Cannot replace entire input data")
        
        # 导航到父级元素
        current = data
        for segment in path_segments[:-1]:
            if segment['type'] == 'index':
                current = current[segment['value']]
            elif segment['type'] == 'key':
                current = current[segment['value']]
        
        # 替换最后一个元素
        last_segment = path_segments[-1]
        if last_segment['type'] == 'index':
            current[last_segment['value']] = new_value
        elif last_segment['type'] == 'key':
            current[last_segment['value']] = new_value

    def _parse_path_segments(self, path):
        """解析路径段"""
        segments = []
        
        # 匹配所有的 [数字] 和 ["字符串"] 或 ['字符串'] 模式
        pattern = r'\[(\d+)\]|\["([^"]+)"\]|\[\'([^\']+)\'\]'
        matches = re.findall(pattern, path)
        
        for match in matches:
            if match[0]:  # 数字索引
                segments.append({
                    'type': 'index',
                    'value': int(match[0])
                })
            elif match[1]:  # 双引号字符串键
                segments.append({
                    'type': 'key',
                    'value': match[1]
                })
            elif match[2]:  # 单引号字符串键
                segments.append({
                    'type': 'key',
                    'value': match[2]
                })
        
        return segments

# 用于测试的示例函数
def test_chain_replacer():
    """测试函数"""
    replacer = ChainReplacer()
    
    # 测试数据
    test_data = [1, {"a": ["b", {"c": "xxx"}]}]
    
    # 测试用例
    test_cases = [
        ('input[1]["a"][1]["c"]', '{"a":"b"}'),  # 替换为JSON对象
        ('input[0]', '42'),                      # 替换数字
        ('input[1]["a"][0]', '"new_string"'),    # 替换字符串
    ]
    
    for path, new_val in test_cases:
        try:
            result = replacer.chain_replace(test_data.copy(), path, new_val)
            print(f"Replace '{path}' with '{new_val}' => {result[0]}")
        except Exception as e:
            print(f"Replace '{path}' with '{new_val}' => Error: {e}")

if __name__ == "__main__":
    test_chain_replacer() 