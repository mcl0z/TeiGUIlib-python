import os
import sys
import time
import msvcrt

WHITE_ON_BLACK = '\033[30;47m'  # 黑字白底
RESET = '\033[0m'  # 重置颜色

def input_box_with_prompt(text="请输入内容:", confirm_text="确认", cancel_text="取消"):
    """
    带有提示文本的输入框函数（改进版：仅更新输入区域，避免闪屏）。
    输出:
      - 用户输入的内容（字符串），如果取消则返回 False
    """
    user_input = ""
    selected_option = 0

    # 初始打印界面
    print(text)
    print("输入内容: " + user_input)
    print()  # 空行
    if selected_option == 0:
        print(f"{WHITE_ON_BLACK}[{confirm_text}]{RESET}   [{cancel_text}]")
    else:
        print(f"[{confirm_text}]   {WHITE_ON_BLACK}[{cancel_text}]{RESET}")

    while True:
        key = msvcrt.getwch()
        if key == '\r':  # Enter 键
            if selected_option == 0:
                if user_input.strip() == "":
                    continue
                else:
                    return user_input
            else:
                return False
        elif key in ('\x00', '\xe0'):  # 处理扩展键（方向键）
            direction = msvcrt.getwch()
            if direction == 'K':  # 左方向键
                selected_option = (selected_option - 1) % 2
            elif direction == 'M':  # 右方向键
                selected_option = (selected_option + 1) % 2
        elif key == '\x08':  # 退格键
            user_input = user_input[:-1]
        else:
            user_input += key

        # 仅更新输入行和按钮所在行（避免全屏清理造成闪烁）
        sys.stdout.write("\033[3A")  # 向上移动3行到“输入内容”那一行
        sys.stdout.write("\033[2K")  # 清除当前行
        sys.stdout.write("输入内容: " + user_input + "\n")
        sys.stdout.write("\033[2K\n")
        sys.stdout.write("\033[2K")
        if selected_option == 0:
            sys.stdout.write(f"{WHITE_ON_BLACK}[{confirm_text}]{RESET}   [{cancel_text}]\n")
        else:
            sys.stdout.write(f"[{confirm_text}]   {WHITE_ON_BLACK}[{cancel_text}]{RESET}\n")
        sys.stdout.flush()

def show_progress_bar(text, progress, total, bar_length=40):
    """
    在控制台显示进度条。
    """
    percent = float(progress) / total
    filled_length = int(bar_length * percent)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{text}进度: |{bar}| {percent * 100:.1f}% 已完成')
    sys.stdout.flush()
    if progress == total:
        print()

def clear_console():
    """ 清屏函数 """
    os.system('cls' if os.name == 'nt' else 'clear')

def render_options(input_type, array_size=None, options=None, text="选择一个选项", visible_rows=25, multi_select=False):
    """
    显示选项列表（支持普通列表和二维数组选择），并增加了多选功能。

    参数:
      - input_type: 1 表示普通列表；2 表示二维数组。
      - array_size: 二维数组的大小，仅当 input_type 为 2 时启用，格式为 (rows, cols)。
      - options: 列表或二维数组选项。
      - text: 提示文本。
      - visible_rows: 显示的最大行数，默认25。
      - multi_select: 是否启用多选功能，默认为 False。
    
    返回:
      - 单选模式下，返回选中的下标（或二维数组中的 (row, col)）。
      - 多选模式下，返回一个列表，列表中为选中的下标或坐标。
    """
    def get_max_width(options):
        if isinstance(options[0], list):
            return max(len(item) for row in options for item in row)
        else:
            return max(len(item) for item in options)

    selected_row = 0
    selected_col = 0
    scroll_offset = 0
    max_width = get_max_width(options) + 2
    rows, cols = array_size if array_size else (len(options), 1)

    if multi_select:
        selected_items = set()

    print(text)
    print()

    def render_page():
        for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
            if input_type == 1:
                if multi_select:
                    marker = "[√] " if row in selected_items else "[ ] "
                else:
                    marker = ""
                print("  " + marker + options[row].ljust(max_width))
            elif input_type == 2:
                line = ""
                for col in range(cols):
                    if multi_select:
                        marker = "[√] " if (row, col) in selected_items else "[ ] "
                    else:
                        marker = ""
                    line += "  " + marker + options[row][col].ljust(max_width)
                print(line)
    render_page()

    while True:
        for _ in range(min(visible_rows, rows)):
            print("\033[F", end="")  # 上移一行

        if input_type == 1:
            for idx in range(scroll_offset, min(scroll_offset + visible_rows, len(options))):
                if multi_select:
                    marker = "[√] " if idx in selected_items else "[ ] "
                else:
                    marker = ""
                padded_option = options[idx].ljust(max_width)
                if idx == selected_row:
                    print(f"> {marker}{WHITE_ON_BLACK}{padded_option}{RESET}")
                else:
                    print(f"  {marker}{padded_option}")
        elif input_type == 2:
            for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
                line = ""
                for col in range(cols):
                    if multi_select:
                        marker = "[√] " if (row, col) in selected_items else "[ ] "
                    else:
                        marker = ""
                    padded_option = options[row][col].ljust(max_width)
                    if row == selected_row and col == selected_col:
                        line += "  " + marker + WHITE_ON_BLACK + padded_option + RESET
                    else:
                        line += "  " + marker + padded_option
                print(line)

        key = msvcrt.getwch()
        if key == '\r':  # Enter 键
            if multi_select:
                if input_type == 1:
                    return list(selected_items)
                elif input_type == 2:
                    return list(selected_items)
            else:
                if input_type == 1:
                    return selected_row
                elif input_type == 2:
                    return (selected_row, selected_col)
        elif key == ' ':
            # 空格键用于切换多选状态（仅在多选模式下有效）
            if multi_select:
                if input_type == 1:
                    if selected_row in selected_items:
                        selected_items.remove(selected_row)
                    else:
                        selected_items.add(selected_row)
                elif input_type == 2:
                    current_coord = (selected_row, selected_col)
                    if current_coord in selected_items:
                        selected_items.remove(current_coord)
                    else:
                        selected_items.add(current_coord)
        elif key in ('\x00', '\xe0'):
            direction = msvcrt.getwch()
            if direction == 'H':  # 上方向键
                if selected_row > 0:
                    selected_row -= 1
                if selected_row < scroll_offset:
                    scroll_offset -= 1
            elif direction == 'P':  # 下方向键
                if selected_row < rows - 1:
                    selected_row += 1
                if selected_row >= scroll_offset + visible_rows:
                    scroll_offset += 1
            elif direction == 'K':  # 左方向键（仅对二维数组有效）
                if input_type == 2:
                    selected_col = (selected_col - 1) % cols
            elif direction == 'M':  # 右方向键（仅对二维数组有效）
                if input_type == 2:
                    selected_col = (selected_col + 1) % cols

def display_aligned_text(text_list, leftorright='left', padding=2):
    """
    在控制台显示对齐的文本列表。
    """
    max_length = max([len(text) for text in text_list]) + padding
    for text in text_list:
        if leftorright == 'left':
            print(text.ljust(max_length))
        elif leftorright == 'right':
            print(text.rjust(max_length))

def popup_dialog(prompt, button_list):
    """
    弹窗函数：显示提示信息和一行按钮（类似输入框的风格，但没有输入区域）。
    参数:
      - prompt: 提示文本（可以包含换行）
      - button_list: 按钮列表，例如 ["确定", "取消"]
    返回:
      - 用户选择的按钮下标
    """
    selected_index = 0
    # 显示提示信息
    print(prompt)
    # 显示按钮（与 input_box 的按钮显示类似）
    def render_buttons():
        line = ""
        for i, btn in enumerate(button_list):
            if i == selected_index:
                line += f"{WHITE_ON_BLACK}[{btn}]{RESET}   "
            else:
                line += f"[{btn}]   "
        print(line)
    render_buttons()
    while True:
        key = msvcrt.getwch()
        if key == '\r':  # Enter 键确认选择
            return selected_index
        elif key in ('\x00', '\xe0'):
            direction = msvcrt.getwch()
            if direction == 'K':  # 左方向键
                selected_index = (selected_index - 1) % len(button_list)
            elif direction == 'M':  # 右方向键
                selected_index = (selected_index + 1) % len(button_list)
        # 更新按钮显示：先将光标上移一行，然后清除并重绘按钮行
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[2K")
        render_buttons()

def showing():
    menu_options = [
        "二维数组显示",
        "进度显示",
        "文本显示(左对齐)",
        "文本显示(右对齐)",
        "文本输入",
        "列表多选",
        "二维数组多选",
        "单项列表单选",
        "弹窗测试"
    ]
    a = render_options(input_type=1, options=menu_options, 
                       text="欢迎使用TeiGUI-Lib V1.2 测试版\n你正处于 __main__ 模式(展示模式)\n请选择功能:")
    if a == 0:
        pos = render_options(input_type=2, array_size=(2, 2), 
                             options=[['A1', 'B1'], ['A2', 'B2']], text="二维数组测试")
        print("二维数组返回:", pos)
    elif a == 1:
        for i in range(100):
            show_progress_bar("下载中..", progress=i, total=100)
            time.sleep(0.01)
    elif a == 2:
        display_aligned_text(text_list=["字符串文本展示", "欢迎使用TeiGUI"], leftorright='left')
    elif a == 3:
        display_aligned_text(text_list=["字符串文本展示", "欢迎使用TeiGUI!!!!!!!!!!!"], leftorright='right')
    elif a == 4:
        result = input_box_with_prompt("请输入内容:", "确定", "取消")
        if result:
            print("你输入的是:", result)
        else:
            print("输入被取消")
    elif a == 5:
        res = render_options(input_type=1, options=["选项1", "选项2", "选项3", "选项4", "选项5"],
                             text="列表多选测试\n（空格键切换选中状态，Enter确认）", multi_select=True)
        print("列表多选返回:", res)
    elif a == 6:
        res = render_options(input_type=2, array_size=(3, 3), 
                             options=[['A1', 'B1', 'C1'], ['A2', 'B2', 'C2'], ['A3', 'B3', 'C3']],
                             text="二维数组多选测试\n（空格键切换选中状态，Enter确认）", multi_select=True)
        print("二维数组多选返回:", res)
    elif a == 7:
        res = render_options(input_type=1, options=["选项A", "选项B", "选项C"],
                             text="单项列表单选测试")
        print("单项列表单选返回:", res)
    elif a == 8:
        # 弹窗测试：只显示提示和按钮，没有输入区域
        choice = popup_dialog("这是一个弹窗测试。\n请根据提示选择一个选项。", ["确定", "取消", "稍后再说"])
        print("弹窗返回:", choice)

if __name__ == '__main__':
    while True:
        showing()
