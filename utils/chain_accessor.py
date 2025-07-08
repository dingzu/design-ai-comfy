import re
import json
from typing import Any, Union

class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class ChainAccessor:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_data": (any, {"default": ""}),
                "access_path": ("STRING", {"default": "input[0]", "multiline": False}),
            }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("result",)
    FUNCTION = "chain_access"
    CATEGORY = "✨✨✨design-ai/logic"

    def chain_access(self, input_data, access_path):
        """
        支持链式访问数据结构的节点
        
        功能:
        - 支持链式访问: input[1]["a"][1]["c"]
        - 支持 .length() 获取数组长度
        - 支持 a|b 默认值操作（如果a不存在则返回b）
        
        示例:
        - input[1]["a"][1]["c"] 
        - input.length()
        - input[1]["missing"]|"default_value"
        - input[0].length()|0
        """
        try:
            # 如果input_data是字符串，尝试解析为JSON
            if isinstance(input_data, str):
                try:
                    data = json.loads(input_data)
                except json.JSONDecodeError:
                    # 如果不是有效JSON，尝试eval（谨慎使用）
                    try:
                        data = eval(input_data)
                    except:
                        data = input_data
            else:
                data = input_data

            # 处理默认值语法 a|b
            if '|' in access_path:
                parts = access_path.split('|', 1)
                primary_path = parts[0].strip()
                default_value = parts[1].strip()
                
                try:
                    result = self._evaluate_path(data, primary_path)
                    return (result,)
                except:
                    # 主路径失败，使用默认值
                    try:
                        # 尝试解析默认值
                        if default_value.startswith('"') and default_value.endswith('"'):
                            return (default_value[1:-1],)  # 字符串字面量
                        elif default_value.startswith("'") and default_value.endswith("'"):
                            return (default_value[1:-1],)  # 字符串字面量
                        elif default_value.isdigit() or (default_value.startswith('-') and default_value[1:].isdigit()):
                            return (int(default_value),)  # 整数
                        elif self._is_float(default_value):
                            return (float(default_value),)  # 浮点数
                        elif default_value.lower() in ['true', 'false']:
                            return (default_value.lower() == 'true',)  # 布尔值
                        elif default_value.lower() == 'null':
                            return (None,)  # null值
                        else:
                            # 尝试作为路径解析
                            return (self._evaluate_path(data, default_value),)
                    except:
                        return (default_value,)  # 返回原始字符串
            else:
                # 普通路径解析
                result = self._evaluate_path(data, access_path)
                return (result,)

        except Exception as e:
            return (f"Error: {str(e)}",)

    def _is_float(self, value):
        """检查字符串是否为浮点数"""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _evaluate_path(self, data, path):
        """评估访问路径"""
        # 替换 'input' 为实际数据的引用
        if path.startswith('input'):
            # 处理 .length() 方法
            if '.length()' in path:
                # 提取 .length() 之前的路径
                base_path = path.replace('.length()', '')
                target_data = self._navigate_path(data, base_path)
                if hasattr(target_data, '__len__'):
                    return len(target_data)
                else:
                    raise ValueError(f"Object at path '{base_path}' does not have length")
            else:
                # 普通路径导航
                return self._navigate_path(data, path)
        else:
            raise ValueError(f"Path must start with 'input': {path}")

    def _navigate_path(self, data, path):
        """导航到指定路径"""
        current = data
        
        # 移除开头的 'input'
        if path.startswith('input'):
            path = path[5:]  # 移除 'input'
        
        # 解析路径段
        segments = self._parse_path_segments(path)
        
        for segment in segments:
            if segment['type'] == 'index':
                # 数组索引访问
                try:
                    current = current[segment['value']]
                except (IndexError, KeyError, TypeError):
                    raise ValueError(f"Cannot access index {segment['value']} in {type(current)}")
            elif segment['type'] == 'key':
                # 字典键访问
                try:
                    current = current[segment['value']]
                except (KeyError, TypeError):
                    raise ValueError(f"Cannot access key '{segment['value']}' in {type(current)}")
        
        return current

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
def test_chain_accessor():
    """测试函数"""
    accessor = ChainAccessor()
    
    # 测试数据
    test_data = [1, {"a": ["b", {"c": "xxx"}]}]
    
    # 测试用例
    test_cases = [
        'input[1]["a"][1]["c"]',  # 应该返回 "xxx"
        'input[1]["a"].length()',  # 应该返回 2
        'input.length()',          # 应该返回 2
        'input[1]["missing"]|"default"',  # 应该返回 "default"
        'input[10]|"not_found"',   # 应该返回 "not_found"
        'input[0]',                # 应该返回 1
    ]
    
    for case in test_cases:
        try:
            result = accessor.chain_access(test_data, case)
            print(f"'{case}' => {result[0]}")
        except Exception as e:
            print(f"'{case}' => Error: {e}")

if __name__ == "__main__":
    test_chain_accessor() 