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

    # 导出图片，返回包含Markdown语法的Paragraph对象
    @classmethod
    def export_image(cls, image_element: documents.Image) -> documents.Paragraph:
        """Export an image to the output directory and return a Paragraph containing the Markdown image reference."""
        try:
            if not ImageExporter._output_dir or not ImageExporter._doc_unique_id:
                raise ValueError("Output directory or document unique ID is not set")

            image_filename = f"{ImageExporter._doc_unique_id}_{cls._image_counter}{cls._get_image_extension(image_element)}"
            image_path = os.path.join(ImageExporter._output_dir, image_filename)
            
            with open(image_path, 'wb') as f:
                with image_element.open() as image_data:
                    f.write(image_data.read())
            
            markdown_ref = f"![image_{cls._image_counter}]({image_filename})"
            cls._image_counter += 1
            logger.info(f"Exported image to: {image_path}")
            return documents.Paragraph(
                children=[documents.Run(
                    children=[documents.Text(markdown_ref)],
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
            return None

    @classmethod
    def _get_image_extension(cls, image_element: documents.Image) -> str:
        content_type = image_element.content_type
        if content_type == "image/png":
            return ".png"
        elif content_type == "image/jpeg":
            return ".jpg"
        elif content_type == "image/gif":
            return ".gif"
        else:
            return ".png"  # Default to PNG
