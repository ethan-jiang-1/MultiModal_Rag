"""
标题层级管理模块
负责管理标题的层级关系、章节编号和层级描述
"""

class HeadingStack:
    def __init__(self):
        """初始化堆栈"""
        self._stack = []  # 堆栈，存储当前层级标题
        self._chapter_numbers = []  # 专门跟踪每个层级的编号
        self._log = []  # 日志，用于记录操作历史，便于调试

    def _reset(self, title: str):
        """
        重置堆栈（如遇到一级标题时清空）
        :param title: 一级标题内容
        """
        self._stack = [{"title": title}]
        if len(self._chapter_numbers) > 0:
            self._chapter_numbers = [self._chapter_numbers[0] + 1]
        else:
            self._chapter_numbers = [1]  # 一级标题从 1 开始
        self._log.append(f"Reset stack: {self._stack}, chapter_numbers: {self._chapter_numbers}")

    def _adjust_to_level(self, level: int):
        """
        调整编号和堆栈到指定的标题层级：
        - 补齐跳跃层级。
        - 清理过深层级。
        :param level: 标题层级（如 1 表示 `#`）
        """
        # 弹出多余层级
        while len(self._chapter_numbers) > level:
            self._chapter_numbers.pop()
            self._stack.pop()

        # 补齐缺失层级
        if len(self._chapter_numbers) < level:
            for _ in range(len(self._chapter_numbers), level - 1):
                self._chapter_numbers.append(1)
                self._stack.append({"title": f"PL{len(self._stack) + 1}"})

    def push_level(self, level: int, title: str) -> str:
        """
        根据标题层级和内容，更新堆栈并返回章节编号。
        :param level: 标题层级
        :param title: 标题内容
        :return: 生成的章节编号（如 `1.1` 或 `1`）
        """
        if level == 1:
            # 重置堆栈和编号
            self._reset(title)
        else:
            # 调整堆栈到指定层级
            self._adjust_to_level(level)

            # 更新当前层级的编号
            if len(self._chapter_numbers) == level - 1:
                self._chapter_numbers.append(1)
                self._stack.append({"title": title})
            else:
                self._chapter_numbers[-1] += 1
                self._stack[-1] = {"title": title}

        # 生成章节编号
        chapter_number = ".".join(map(str, self._chapter_numbers))
        self._log.append(f"Added title '{title}' at level {level}: {chapter_number}")
        return chapter_number

    def get_hierarchy_desc(self, separator: str = " __ ") -> str:
        """
        返回当前堆栈层级的描述字符串
        :param separator: 分隔符，默认为 " __ "
        :return: 当前层级的描述字符串（如 "Introduction __ Background"）
        """
        return separator.join(item["title"] for item in self._stack)

    def _get_state(self) -> dict:
        """
        获取堆栈和编号的当前状态以及操作日志。
        :return: 堆栈状态和日志
        """
        return {
            "stack": self._stack,
            "chapter_numbers": self._chapter_numbers,
            "log": self._log
        }

if __name__ == "__main__":
    # 测试用例：模拟一个典型的文档结构
    stack = HeadingStack()
    
    # 测试一级标题
    print("\n=== 测试一级标题 ===")
    num = stack.push_level(1, "引言")
    print(f"章节号: {num}")
    print(f"层级描述: {stack.get_hierarchy_desc()}")
    
    # 测试二级标题
    print("\n=== 测试二级标题 ===")
    num = stack.push_level(2, "研究背景")
    print(f"章节号: {num}")
    print(f"层级描述: {stack.get_hierarchy_desc()}")
    
    # 测试跳级（直接三级标题）
    print("\n=== 测试跳级（三级标题）===")
    num = stack.push_level(3, "具体问题")
    print(f"章节号: {num}")
    print(f"层级描述: {stack.get_hierarchy_desc()}")
    
    # 测试返回上级（二级标题）
    print("\n=== 测试返回上级（二级标题）===")
    num = stack.push_level(2, "研究方法")
    print(f"章节号: {num}")
    print(f"层级描述: {stack.get_hierarchy_desc()}")
    
    # 测试新的一级标题（重置堆栈）
    print("\n=== 测试新的一级标题 ===")
    num = stack.push_level(1, "实验结果")
    print(f"章节号: {num}")
    print(f"层级描述: {stack.get_hierarchy_desc()}")
    
    # 打印完整的状态日志
    print("\n=== 完整状态日志 ===")
    import json
    print(json.dumps(stack._get_state(), ensure_ascii=False, indent=2)) 