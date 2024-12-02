import re
import json

class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class JsonExtractor:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_json": ("STRING", {"default": ""}),
                "extract_syntax": ("STRING", {"default": ""}),
                "output_syntax": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "extract_and_format"
    CATEGORY = "✨✨✨design-ai/logic"

    def extract_and_format(self, input_json, extract_syntax, output_syntax):
        try:
            # Parse the input JSON-like string
            input_data = json.loads(input_json)
        except json.JSONDecodeError:
            # If not valid JSON, treat it as a nested list
            input_data = eval(input_json)

        # Extract values based on the syntax
        extracted_values = {}
        for syntax in extract_syntax.split(','):
            var, path = syntax.split('=')
            var = var.strip().strip('${}')
            path = path.strip()

            try:
                value = self.extract_value(input_data, path)
            except:
                value = None

            extracted_values[var] = value

        # Format the output with support for mathematical functions
        output_syntax = self.process_output_syntax(output_syntax, extracted_values)

        return (output_syntax,)

    def extract_value(self, data, path):
        match = re.match(r'INPUT(\[[\d]+\])+', path)
        if match:
            for index in re.findall(r'\[(\d+)\]', path):
                data = data[int(index)]
            return data
        else:
            raise ValueError("Invalid extraction path")

    def process_output_syntax(self, output_syntax, extracted_values):
        # Replace variables with their values
        for var, value in extracted_values.items():
            if value is None:
                output_syntax = output_syntax.replace(f"${{{var}}}", "null")
            else:
                output_syntax = output_syntax.replace(f"${{{var}}}", str(value))

        # Process mathematical functions
        output_syntax = self.process_math_functions(output_syntax)

        return output_syntax

    def process_math_functions(self, output_syntax):
        # Define supported functions
        functions = {
            'MIN': min,
            'MAX': max,
            'SUM': sum,
            'AVG': lambda x: sum(x) / len(x) if x else None,
            'INT': int,
            'A_OR_B': lambda a, b: a if a is not None else b
        }

        # Find and process function calls
        pattern = re.compile(r'(\w+)\(([^)]+)\)')
        matches = pattern.findall(output_syntax)
        for func, args in matches:
            if func in functions:
                arg_values = [self.safe_eval(arg.strip()) for arg in args.split(',')]
                result = functions[func](arg_values) if func in ['MIN', 'MAX', 'SUM', 'AVG'] else functions[func](*arg_values)
                output_syntax = output_syntax.replace(f"{func}({args})", str(result))

        return output_syntax

    def safe_eval(self, expr):
        try:
            return eval(expr)
        except:
            return None