import numpy as np

class CropImageByPercentage:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "top_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "bottom_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "left_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "right_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "multiple": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "width", "height")

    FUNCTION = "crop_image"

    CATEGORY = "✨✨✨design-ai"

    def crop_image(self, image, top_percent, bottom_percent, left_percent, right_percent, multiple):
        img = image[0]
        height, width, channels = img.shape

        # Calculate pixel values from percentages
        top = int(height * (top_percent / 100.0))
        bottom = int(height * (bottom_percent / 100.0))
        left = int(width * (left_percent / 100.0))
        right = int(width * (right_percent / 100.0))

        # Ensure the crop values are within the image boundaries
        top = max(0, min(top, height))
        bottom = max(0, min(bottom, height))
        left = max(0, min(left, width))
        right = max(0, min(right, width))

        # Crop the image
        cropped_img = img[top:height-bottom, left:width-right]

        # Get new dimensions
        new_height, new_width, _ = cropped_img.shape

        # Adjust dimensions to be multiples of the given parameter
        new_height = (new_height // multiple) * multiple
        new_width = (new_width // multiple) * multiple

        # Ensure the cropped image is resized to the new dimensions
        cropped_img = cropped_img[:new_height, :new_width]

        return (cropped_img[np.newaxis, ...], new_width, new_height)