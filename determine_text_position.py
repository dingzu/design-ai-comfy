import torch

class DetermineTextPosition:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ocr_json": ("JSON",),
                "center_threshold": ("FLOAT", {"default": 10.0, "min": 1.0, "max": 100.0}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("largest_text_position", "centroid_position")
    FUNCTION = "determine_text_position"
    CATEGORY = "✨✨✨design-ai/logic"

    def determine_text_position(self, ocr_json, center_threshold):
        # Convert center_threshold to a ratio (0.01 to 1.0)
        center_threshold = center_threshold / 100.0

        # Check if the input is a list and has at least one element
        if not isinstance(ocr_json, list) or len(ocr_json) == 0:
            return ("Failed", "Failed")

        # Use the first element in the list
        data = ocr_json[0]

        # Check if the required keys are in the JSON
        if not data or "shapes" not in data or "imageWidth" not in data:
            return ("Failed", "Failed")

        shapes = data["shapes"]
        image_width = data["imageWidth"]

        # Check if shapes list is not empty and image width is valid
        if not shapes or image_width <= 0:
            return ("Failed", "Failed")

        # Find the largest text box
        largest_area = 0
        largest_box = None
        centroids = []
        for shape in shapes:
            if shape["shape_type"] == "rectangle":
                points = shape["points"]
                width = abs(points[1][0] - points[0][0])
                height = abs(points[1][1] - points[0][1])
                area = width * height
                centroid_x = (points[0][0] + points[1][0]) / 2
                centroids.append(centroid_x)
                if area > largest_area:
                    largest_area = area
                    largest_box = shape

        # Check if a largest box was found
        if not largest_box:
            return ("Failed", "Failed")

        # Determine the position of the largest text box
        points = largest_box["points"]
        box_center_x = (points[0][0] + points[1][0]) / 2
        image_center_x = image_width / 2

        # Calculate the distance ratio for the largest text box
        distance_ratio = abs(box_center_x - image_center_x) / image_width

        # Determine the position based on the distance ratio and center threshold
        if distance_ratio <= center_threshold:
            largest_text_position = "center"
        elif box_center_x < image_center_x:
            largest_text_position = "left"
        else:
            largest_text_position = "right"

        # Determine the position based on the centroids of all shapes
        if not centroids:
            return (largest_text_position, "Failed")

        average_centroid_x = sum(centroids) / len(centroids)
        distance_ratio_centroid = abs(average_centroid_x - image_center_x) / image_width

        if distance_ratio_centroid <= center_threshold:
            centroid_position = "center"
        elif average_centroid_x < image_center_x:
            centroid_position = "left"
        else:
            centroid_position = "right"

        return (largest_text_position, centroid_position)

