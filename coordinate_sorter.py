class AnyType(str):
    def __eq__(self, __value: object) -> bool:
        return True
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class CoordinateSorter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "coordinates": ("STRING", {"default": ""}),
                "primary_sort": (["x", "y"],),
                "primary_order": (["asc", "desc"],),
                "secondary_sort": (["x", "y"],),
                "secondary_order": (["asc", "desc"],),
                "range_coordinates": ("STRING", {"default": "-1"})
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "sort_coordinates"
    CATEGORY = "✨✨✨design-ai/logic"

    def sort_coordinates(self, coordinates, primary_sort, primary_order, secondary_sort, secondary_order, range_coordinates):
        import ast

        # Parse the coordinates string into a list of tuples
        coordinates_list = ast.literal_eval(coordinates)

        # Parse the range_coordinates string into a list of tuples
        if range_coordinates != "-1":
            range_coordinates_list = ast.literal_eval(range_coordinates)
            (x1, y1), (x2, y2) = range_coordinates_list

            # Filter coordinates within the specified range
            coordinates_list = [
                (x, y) for (x, y) in coordinates_list
                if x1 <= x <= x2 and y1 <= y <= y2
            ]

        # Define the sorting key function
        def sort_key(coord):
            primary_index = 0 if primary_sort == "x" else 1
            secondary_index = 0 if secondary_sort == "x" else 1
            return (coord[primary_index], coord[secondary_index])

        # Sort the coordinates list
        reverse_primary = primary_order == "desc"
        reverse_secondary = secondary_order == "desc"
        sorted_coordinates = sorted(coordinates_list, key=sort_key, reverse=reverse_primary)

        # If primary and secondary orders are different, we need to sort again for secondary order
        if primary_order != secondary_order:
            sorted_coordinates = sorted(sorted_coordinates, key=lambda coord: coord[1] if secondary_sort == "y" else coord[0], reverse=reverse_secondary)

        return (str(sorted_coordinates),)