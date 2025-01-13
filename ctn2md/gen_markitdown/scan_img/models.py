from dataclasses import dataclass

@dataclass
class ImageReference:
    """图片引用信息"""
    ref_name: str            # 图片引用名称
    position: int           # 在文档中的位置
    context_before: str     # 图片前的上下文
    context_after: str      # 图片后的上下文
    line_number: int        # 所在行号
    figure_name: str = ""   # 图片标题
    image_description: str = ""  # 图片描述
    
    def needs_update(self) -> bool:
        """检查是否需要更新figure_name和image_description"""
        return not (self.figure_name and self.image_description)
    
    def update_description(self, figure_name: str, description: str) -> None:
        """更新figure_name和image_description"""
        self.figure_name = figure_name
        self.image_description = description
        
    def to_markdown(self) -> str:
        """生成markdown格式的图片引用"""
        if self.needs_update():
            return f"![{self.ref_name}]({self.ref_name})"
        return f"![{self.figure_name}]({self.ref_name} \"{self.image_description}\")" 