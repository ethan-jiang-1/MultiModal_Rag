import os
import logging
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
        try:
            base_name = os.path.basename(image_filename)
            markdown_ref = "!" + "[" + f"{base_name}" + "]" + "(" + base_name + ")"
            logger.info(f"Exported image to: {image_filename}")
            return documents.paragraph(
                children=[documents.run(
                    children=[documents.text(markdown_ref)],
                    style_id=None,
                    style_name=None,
                    is_bold=False,
                    is_italic=False,
                    is_underline=False,
                    is_strikethrough=False,
                    is_all_caps=False,
                    is_small_caps=False,
                    vertical_alignment=None,
                    font=None,
                    font_size=None,
                    highlight=None
                )],
                style_id="normal",
                style_name="Normal",
                numbering=None,
                alignment=None,
                indent=None
            )
        except Exception as e:
            logger.error(f"Failed to export image: {str(e)}")
            return documents.paragraph(
                children=[documents.run(
                    children=[documents.text("[Image export failed]")],
                    style_id=None,
                    style_name=None,
                    is_bold=False,
                    is_italic=False,
                    is_underline=False,
                    is_strikethrough=False,
                    is_all_caps=False,
                    is_small_caps=False,
                    vertical_alignment=None,
                    font=None,
                    font_size=None,
                    highlight=None
                )],
                style_id="normal",
                style_name="Normal",
                numbering=None,
                alignment=None,
                indent=None
            )
 
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
        return content_type_map.get(content_type, ".png")  # Default to PNG
