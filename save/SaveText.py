import os
import json
import hashlib
import folder_paths

def get_unique_hash(text):
    """生成唯一的文件名哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]

class SaveTextNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True,"dynamicPrompts": False}),
            },
            "optional":{ 
                    "output_dir": ("STRING",{"forceInput": True,"default": "","multiline": True,"dynamicPrompts": False}), 
                }
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = "✨✨✨design-ai/io"

    def run(self, text, output_dir=[""]):
        # 类型纠正
        texts = []
        for t in text:
            if not isinstance(t, str):
                t = str(t)
            texts.append(t)

        if len(output_dir)==1 and (output_dir[0]=='' or os.path.dirname(output_dir[0])==''):
            t = '\n'.join(text)
            output_dir = [
                os.path.join(folder_paths.get_temp_directory(),
                             get_unique_hash(t)+'.txt'
                             )
            ]
        elif len(output_dir)==1:
            base = os.path.basename(output_dir[0])
            t = '\n'.join(text)
            if base=='' or os.path.splitext(base)[1]=='':
                base = get_unique_hash(t)+'.txt'
            output_dir = [
                os.path.join(output_dir[0],
                             base
                             )
            ]

        if len(output_dir)==1 and len(text)>1:
            output_dir = [output_dir[0] for _ in range(len(text))]
        
        for i in range(len(text)):
            o_fp = output_dir[i]
            dirp = os.path.dirname(o_fp)
            if dirp=='':
                dirp = folder_paths.get_temp_directory()
                o_fp = os.path.join(folder_paths.get_temp_directory(), o_fp)

            if not os.path.exists(dirp):
                os.makedirs(dirp, exist_ok=True)

            if not os.path.splitext(o_fp)[1].lower()=='.txt':
                o_fp = o_fp+'.txt'

            t = text[i]
            # 使用 utf-8 编码写入文件
            with open(o_fp, 'w', encoding='utf-8') as file:
                file.write(t)

        # 确保返回的文本也使用正确的编码
        result_text = text[0] if isinstance(text, list) and len(text) > 0 else text
        return {"ui": {"text": result_text}, "result": (text,)}