class Cropborder:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "top": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "bottom": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "left": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "right": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("cropped_image", "width", "height")

    FUNCTION = "crop_image"

    CATEGORY = "✨✨✨design-ai"

    def crop_image(self, image, top, bottom, left, right):
        img = image[0]
        height, width, channels = img.shape

        # Ensure the crop values are within the image boundaries
        top = max(0, min(top, height))
        bottom = max(0, min(bottom, height))
        left = max(0, min(left, width))
        right = max(0, min(right, width))

        # Crop the image
        cropped_img = img[top:height-bottom, left:width-right]

        # Get new dimensions
        new_height, new_width, _ = cropped_img.shape

        return (cropped_img.unsqueeze(0), new_width, new_height)