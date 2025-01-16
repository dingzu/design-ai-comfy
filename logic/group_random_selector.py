import torch
import numpy as np
import json
import random

class GroupRandomSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_config": ("STRING", {
                    "default": '[{"groupName":"group1","list":["1","2","3"]},{"groupName":"group2","list":["4","5","6"]}]',
                    "multiline": True  # 允许多行输入
                }),
                "target_groups": ("STRING", {
                    "default": "",  # 为空时在所有组中随机
                    "multiline": False
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2**32 - 1  # 调整为符合要求的范围
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("selected_value", "selected_group", "all_groups")
    FUNCTION = "random_select"
    CATEGORY = "✨✨✨design-ai/logic"

    def random_select(self, json_config, target_groups="", seed=0):
        try:
            # 设置随机种子
            random.seed(seed)
            np.random.seed(seed)

            # 解析JSON配置
            config = json.loads(json_config)
            
            # 验证配置格式
            if not isinstance(config, list):
                raise ValueError("Config must be a list of groups")
            
            # 解析目标组名
            target_group_list = [g.strip() for g in target_groups.split(",")] if target_groups else []
            target_group_list = [g for g in target_group_list if g]  # 移除空字符串
            
            # 收集所有可用的组名
            all_groups = [group["groupName"] for group in config]
            all_groups_str = ",".join(all_groups)
            
            # 筛选符合条件的组
            valid_groups = []
            if target_group_list:
                # 只选择指定的组
                valid_groups = [
                    group for group in config 
                    if group["groupName"] in target_group_list
                ]
            else:
                # 使用所有组
                valid_groups = config
                
            if not valid_groups:
                return ("", "", all_groups_str)
            
            # 收集所有符合条件的选项
            all_items = []
            group_mapping = {}  # 用于记录每个项属于哪个组
            
            for group in valid_groups:
                group_name = group["groupName"]
                items = group.get("list", [])
                for item in items:
                    all_items.append(item)
                    group_mapping[len(all_items)-1] = group_name
            
            if not all_items:
                return ("", "", all_groups_str)
            
            # 随机选择一个项
            selected_index = random.randint(0, len(all_items)-1)
            selected_value = str(all_items[selected_index])
            selected_group = group_mapping[selected_index]
            
            return (selected_value, selected_group, all_groups_str)
            
        except json.JSONDecodeError as e:
            return (f"JSON解析错误: {str(e)}", "", "")
        except Exception as e:
            return (f"错误: {str(e)}", "", "")