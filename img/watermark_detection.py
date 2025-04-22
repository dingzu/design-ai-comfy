import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms.functional as TVF
from transformers import Owlv2VisionModel
from torch import nn
import folder_paths
import os

# Register design_models directory
if "design_models" not in folder_paths.folder_names_and_paths:
    current_paths = [os.path.join(folder_paths.models_dir, "design_models")]
else:
    current_paths, _ = folder_paths.folder_names_and_paths["design_models"]
folder_paths.folder_names_and_paths["design_models"] = (current_paths, folder_paths.supported_pt_extensions)

class DetectorModelOwl(nn.Module):
    owl: Owlv2VisionModel

    def __init__(self, model_path: str, dropout: float, n_hidden: int = 768):
        super().__init__()

        # Load model from local path
        owl = Owlv2VisionModel.from_pretrained(model_path, local_files_only=True)
        assert isinstance(owl, Owlv2VisionModel)
        self.owl = owl
        self.owl.requires_grad_(False)
        self.transforms = None

        self.dropout1 = nn.Dropout(dropout)
        self.ln1 = nn.LayerNorm(n_hidden, eps=1e-5)
        self.linear1 = nn.Linear(n_hidden, n_hidden * 2)
        self.act1 = nn.GELU()
        self.dropout2 = nn.Dropout(dropout)
        self.ln2 = nn.LayerNorm(n_hidden * 2, eps=1e-5)
        self.linear2 = nn.Linear(n_hidden * 2, 2)
    
    def forward(self, pixel_values: torch.Tensor, labels: torch.Tensor | None = None):
        with torch.autocast("cpu", dtype=torch.bfloat16):
            outputs = self.owl(pixel_values=pixel_values, output_hidden_states=True)
            x = outputs.last_hidden_state
        
            x = self.dropout1(x)
            x = self.ln1(x)
            x = self.linear1(x)
            x = self.act1(x)

            x = self.dropout2(x)
            x, _ = x.max(dim=1)
            x = self.ln2(x)

            x = self.linear2(x)
        
        if labels is not None:
            loss = F.cross_entropy(x, labels)
            return (x, loss)

        return (x,)

class WatermarkDetector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "owl_model_dir": ("STRING", {"default": "owlv2-base-patch16-ensemble"}),
                "owl_weights_name": (folder_paths.get_filename_list("design_models"), ),
                "confidence_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    FUNCTION = "detect_watermark"
    CATEGORY = "✨✨✨design-ai/img"

    def detect_watermark(self, image, owl_model_dir, owl_weights_name, confidence_threshold):
        # Get full paths
        owl_model_path = os.path.join(folder_paths.get_folder_paths("design_models")[0], owl_model_dir)
        owl_weights_path = folder_paths.get_full_path("design_models", owl_weights_name)

        # Load OWLv2 model
        owl_model = DetectorModelOwl(owl_model_path, dropout=0.0)
        owl_model.load_state_dict(torch.load(owl_weights_path, map_location="cuda"))
        owl_model = owl_model.to('cuda')
        owl_model.eval()

        # Process image for OWLv2
        pil_image = Image.fromarray((image[0].cpu().numpy() * 255).astype('uint8'))
        
        # Pad to square
        big_side = max(pil_image.size)
        new_image = Image.new("RGB", (big_side, big_side), (128, 128, 128))
        new_image.paste(pil_image, (0, 0))

        # Resize to 960x960
        preped = new_image.resize((960, 960), Image.BICUBIC)

        # Convert to tensor and normalize
        preped = TVF.pil_to_tensor(preped)
        preped = preped / 255.0
        input_image = TVF.normalize(preped, [0.48145466, 0.4578275, 0.40821073], [0.26862954, 0.26130258, 0.27577711])

        # Run OWLv2 prediction
        with torch.no_grad():
            logits, = owl_model(input_image.to('cuda').unsqueeze(0), None)
            probs = F.softmax(logits, dim=1)
            owl_prediction = torch.argmax(probs.cpu(), dim=1)
            owl_label = "Watermarked" if owl_prediction.item() == 1 else "Not Watermarked"

        # Return original image and prediction
        return (image, f"OWLv2 Prediction: {owl_label}")

class WatermarkCheck:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "owl_model_dir": ("STRING", {"default": "owlv2-base-patch16-ensemble"}),
                "owl_weights_name": (folder_paths.get_filename_list("design_models"), ),
                "confidence_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "check_watermark"
    CATEGORY = "✨✨✨design-ai/img"

    def check_watermark(self, image, owl_model_dir, owl_weights_name, confidence_threshold):
        # Get full paths
        owl_model_path = os.path.join(folder_paths.get_folder_paths("design_models")[0], owl_model_dir)
        owl_weights_path = folder_paths.get_full_path("design_models", owl_weights_name)

        # Load OWLv2 model
        owl_model = DetectorModelOwl(owl_model_path, dropout=0.0)
        owl_model.load_state_dict(torch.load(owl_weights_path, map_location="cuda"))
        owl_model = owl_model.to('cuda')
        owl_model.eval()

        # Process image for OWLv2
        pil_image = Image.fromarray((image[0].cpu().numpy() * 255).astype('uint8'))
        
        # Pad to square
        big_side = max(pil_image.size)
        new_image = Image.new("RGB", (big_side, big_side), (128, 128, 128))
        new_image.paste(pil_image, (0, 0))

        # Resize to 960x960
        preped = new_image.resize((960, 960), Image.BICUBIC)

        # Convert to tensor and normalize
        preped = TVF.pil_to_tensor(preped)
        preped = preped / 255.0
        input_image = TVF.normalize(preped, [0.48145466, 0.4578275, 0.40821073], [0.26862954, 0.26130258, 0.27577711])

        # Run OWLv2 prediction
        with torch.no_grad():
            logits, = owl_model(input_image.to('cuda').unsqueeze(0), None)
            probs = F.softmax(logits, dim=1)
            owl_prediction = torch.argmax(probs.cpu(), dim=1)
        
        # Return boolean result
        return (owl_prediction.item() == 1,)

NODE_CLASS_MAPPINGS = {
    "WatermarkDetector": WatermarkDetector,
    "WatermarkCheck": WatermarkCheck
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WatermarkDetector": "Watermark Detection",
    "WatermarkCheck": "Watermark Check"
}
