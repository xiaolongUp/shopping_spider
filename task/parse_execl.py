import openpyxl
from pathlib import Path


class BolCategory(object):
    level1 = None
    level2 = None
    level3 = None

    def __init__(self, level1, level2, level3):
        self.level1 = level1
        self.level2 = level2
        self.level3 = level3

    @staticmethod
    def traverse_categories(file_path) -> list:
        list_categories = []
        # 加载工作簿
        # 获取当前脚本所在目录的父目录
        parent_dir = Path(__file__).parent.parent  # __file__ 是当前脚本路径
        file_path = parent_dir / "bol类目.xlsx"
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        # 初始化变量
        current_level1 = ""
        current_level2 = ""

        # 遍历每一行（从第二行开始，跳过标题行）
        for row in sheet.iter_rows(min_row=2, values_only=True):
            level1, level2, level3 = row

            # 更新当前一级类目（如果不为空）
            if level1:
                current_level1 = level1

            # 更新当前二级类目（如果不为空）
            if level2:
                current_level2 = level2
            list_categories.append(BolCategory(current_level1, current_level2, level3))
            # # 打印或处理各级类目
            # print(f"一级类目: {current_level1}")
            # print(f"二级类目: {current_level2}")
            # print(f"三级类目: {level3}")
            # print("-" * 50)  # 分隔线
        return list_categories


if __name__ == '__main__':
    # 使用示例
    list_categories = BolCategory.traverse_categories("../bol类目.xlsx")
    for category in list_categories:
        print(category.level1, category.level2, category.level3)
