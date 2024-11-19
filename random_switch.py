import random

class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class RandomSwitch:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0}),
                "input_1": (any,),
                "input_2": (any,),
                "input_3": (any,),
                "input_4": (any,),
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "random_switch"
    CATEGORY = "✨✨✨design-ai/logic"

    def random_switch(self, seed, input_1, input_2, input_3, input_4):
        random.seed(seed)
        inputs = [input_1, input_2, input_3, input_4]
        selected_input = random.choice(inputs)
        return (selected_input,)

# 示例使用
if __name__ == "__main__":
    switch = RandomSwitch()
    result = switch.random_switch(seed=42, input_1="Input A", input_2="Input B", input_3="Input C", input_4="Input D")
    print(result)
