class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False
  
any = AnyType("*")

class SwitchCaseMore:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "switch_condition": ("STRING", {"default": "", "multiline": False}),
                **{f"case_{i}": ("STRING", {"default": "", "multiline": False}) for i in range(1, 17)},
                "input_default": (any,),
            },
            "optional": {
                **{f"input_{i}": (any,) for i in range(1, 17)},
            }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = "?"
    FUNCTION = "switch_case"
    CATEGORY = "✨✨✨design-ai/switch-case"

    def switch_case(self, switch_condition, input_default, **kwargs):
        case_input_dict = {kwargs[f'case_{i}']: kwargs.get(f'input_{i}') for i in range(1, 17)}
        
        return (case_input_dict.get(switch_condition, input_default),)