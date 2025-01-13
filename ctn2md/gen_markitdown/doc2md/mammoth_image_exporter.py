import os
import logging
import re
from mammoth import documents

logger = logging.getLogger(__name__)

class ImageExporter:
    _output_dir: str = ""
    _doc_unique_id: str = ""
    _image_counter: int = 0

    @classmethod
    def set_output_dir(cls, output_dir: str, doc_unique_id: str):
        ImageExporter._output_dir = output_dir
        ImageExporter._doc_unique_id = doc_unique_id
        ImageExporter._image_counter = 0

    @classmethod
    def save_image_as_local_file(cls, image_path: str, image_element: documents.Image):
        try:
            with open(image_path, 'wb') as f:
                with image_element.open() as image_data:
                    f.write(image_data.read())
                    return True
        except Exception as e:
            logger.error(f"Failed to save image as local file: {str(e)}")
            return False
        
    @classmethod
    def export_image(cls, image_element: documents.Image) -> documents.Paragraph:
        """Export an image to the output directory and return a Paragraph containing the Markdown image reference."""
        if not ImageExporter._output_dir or not ImageExporter._doc_unique_id:
            raise ValueError("Output directory or document unique ID is not set")

        image_filename = f"{ImageExporter._doc_unique_id}_{cls._image_counter}{cls._get_image_extension(image_element)}"
        image_path = os.path.join(ImageExporter._output_dir, image_filename)

        # do not change this line, it works, do not change it
        cls.save_image_as_local_file(image_path, image_element)
        cls._image_counter += 1

        return cls.build_img_ref_object(image_filename)   
    
    @classmethod
    def build_img_ref_object(cls, image_filename: str) -> documents.Paragraph:
        """构建Markdown图片引用对象,将感叹号和链接分开处理,避免转义字符"""
        # alt text
        alt_text = "ImageRef"
        
        # 感叹号和链接分开处理
        exclamation = documents.text("!")
        link = documents.hyperlink(href=image_filename, children=[documents.text(alt_text)])
        
        return documents.paragraph([
            documents.run([exclamation]),
            documents.run([link])
        ])
 
    @classmethod
    def _get_image_extension(cls, image_element: documents.Image) -> str:
        content_type = image_element.content_type
        content_type_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
            "image/x-icon": ".ico",
            "image/heic": ".heic",
            "image/heif": ".heif"
        }
        return content_type_map.get(content_type, ".png")
    
    @classmethod
    def recover_img_ref(cls, markdown_text: str) -> str:
        # 转义很麻烦，我们在 markdown 中使用 \![ImageRef](00bd3592_0.png) 来表示图片引用 
        # 这里我们恢复为 ![ImageRef](00bd3592_0.png)
        # 特别的地方就是 看到 \![ImageRef] 后知道可以替换，需要恢复为 ![ImageRef](00bd3592_0.png)
        # 所以需要找到 \![ImageRef] 然后替换为 ![ImageRef](00bd3592_0.png)
        # 这里使用正则表达式来实现
        pattern = r"\\!\[ImageRef\]\((.*?)\)"
        return re.sub(pattern, r"![ImageRef](\1)", markdown_text)

