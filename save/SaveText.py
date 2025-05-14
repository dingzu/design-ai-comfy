import os
import json
import hashlib
import folder_paths

class SaveTextNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True,"dynamicPrompts": False}),
            }
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = "✨✨✨design-ai/io"

    def run(self, text,output_dir=[""]):
        texts=[]
        for t in text:
            if not isinstance(t, str):
                t = str(t)
            texts.append(t)

        text=texts
        return {"ui": {"text": text}, "result": (text,)}
