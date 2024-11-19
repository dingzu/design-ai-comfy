class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class StringBuilder:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_template": ("STRING", {"default": ""}),
                "input_1": (any,{"default": ""}),
                "input_2": (any,{"default": ""}),
                "input_3": (any,{"default": ""}),
                "input_4": (any,{"default": ""}),
                "input_5": (any,{"default": ""}),
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "build_string"
    CATEGORY = "✨✨✨design-ai/logic"

    def build_string(self, string_template, input_1, input_2, input_3, input_4, input_5):
        # Create a dictionary to map input placeholders to actual inputs
        input_dict = {
            "input_1": input_1,
            "input_2": input_2,
            "input_3": input_3,
            "input_4": input_4,
            "input_5": input_5,
        }

        # Replace placeholders in the template with actual inputs
        for key, value in input_dict.items():
            placeholder = f"${{{key}}}"
            string_template = string_template.replace(placeholder, str(value))

        return (string_template,)

# Example usage
builder = StringBuilder()
result = builder.build_string("Hello, ${input_1}! Today is ${input_2}.", "Alice", "Monday", "", "", "")
print(result)  # Output: ('Hello, Alice! Today is Monday.',)