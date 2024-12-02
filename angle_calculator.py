import math

class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class AngleCalculator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "point_1": ("STRING", {"default": "[0,0]"}),
                "point_2": ("STRING", {"default": "[1,1]"}),
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "calculate_angle"
    CATEGORY = "✨✨✨design-ai/logic"

    def calculate_angle(self, point_1, point_2):
        try:
            # Parse the input points
            x1, y1 = eval(point_1)
            x2, y2 = eval(point_2)

            # Ensure the parsed values are numbers
            if not (isinstance(x1, (int, float)) and isinstance(y1, (int, float)) and isinstance(x2, (int, float)) and isinstance(y2, (int, float))):
                raise ValueError("Coordinates must be numbers")

            # Calculate the differences
            dx = x2 - x1
            dy = y2 - y1

            # Calculate the angle in radians
            angle_radians = math.atan2(dy, dx)

            # Convert the angle to degrees
            angle_degrees = math.degrees(angle_radians)

        except (SyntaxError, ValueError, TypeError, NameError):
            # If there is any error in parsing or calculation, return 0 degrees
            angle_degrees = 0.0

        return (angle_degrees,)
