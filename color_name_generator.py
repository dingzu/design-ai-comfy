import json
import colorsys

class ColorNameGenerator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#000000"}),
                "config_json": ("STRING", {
                    "default": """[
                        {
                            "name": "红色",
                            "conditions": {
                                "h": [350, 10],
                                "s": [50, 100],
                                "l": [20, 60]
                            }
                        },
                        {
                            "name": "红色",
                            "conditions": {
                                "h": [350, 10],
                                "s": [30, 50],
                                "l": [40, 80]
                            }
                        }
                    ]""",
                    "multiline": True
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("color_description",)

    FUNCTION = "describe_color"

    CATEGORY = "✨✨✨design-ai/color"

    def describe_color(self, hex_color, config_json):
        # Convert hex to RGB
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert RGB to HSL
        h, l, s = colorsys.rgb_to_hls(*[x/255 for x in rgb])
        h *= 360
        s *= 100
        l *= 100

        # Parse the configuration JSON
        try:
            rules = json.loads(config_json)
            if not isinstance(rules, list):
                return ("配置格式错误：需要是规则列表",)
        except json.JSONDecodeError:
            return ("JSON 格式错误",)

        # Find the first matching rule
        for rule in rules:
            if not isinstance(rule, dict) or 'name' not in rule or 'conditions' not in rule:
                continue
            
            if self.match_rule(h, s, l, rule['conditions']):
                return (rule['name'],)

        return ("未知颜色",)

    def match_rule(self, h, s, l, conditions):
        for key, value_range in conditions.items():
            if key == 'h':
                if not self.is_in_hue_range(h, value_range[0], value_range[1]):
                    return False
            elif key == 's':
                if not (value_range[0] <= s <= value_range[1]):
                    return False
            elif key == 'l':
                if not (value_range[0] <= l <= value_range[1]):
                    return False
        return True

    def is_in_hue_range(self, h, start, end):
        if start <= end:
            return start <= h <= end
        else:  # 处理跨越0度的情况
            return h >= start or h <= end