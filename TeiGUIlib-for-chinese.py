import os
import sys
import time
import msvcrt

WHITE_ON_BLACK = '\033[30;47m'  # 黑字白底
RESET = '\033[0m'  # 重置颜色

def input_box_with_prompt(text="请输入内容:", confirm_text="确认", cancel_text="取消"):
    """
    带有提示文本的输入框函数。
    输入:
    - text: 提示文本，可以自定义
    - confirm_text: 确认按钮文本
    - cancel_text: 取消按钮文本
    输出:
    - 用户输入的内容（字符串），如果取消则返回 False
    """
    
    while True:
        user_input = ""  # 用户输入的内容
        selected_option = 0  # 0表示“确认”，1表示“取消”
        
        while True:
            # 清屏
            os.system('cls' if os.name == 'nt' else 'clear')

            # 显示提示文本和当前输入内容
            print(f"{text}")
            print(f"输入内容: {user_input}")
            print()
            
            # 显示“确认”和“取消”按钮，当前选项加上白字黑底
            if selected_option == 0:
                print(f"{WHITE_ON_BLACK}[{confirm_text}]{RESET}   [{cancel_text}]")
            else:
                print(f"[{confirm_text}]   {WHITE_ON_BLACK}[{cancel_text}]{RESET}")
                
            # 捕获键盘输入
            key = msvcrt.getch()

            if key == b'\r':  # Enter 键
                if selected_option == 0:  # 如果当前选项是“确认”
                    if user_input.strip() == "":  # 如果输入内容为空
                        break  # 重新输入
                    else:
                        return user_input  # 返回用户输入的内容
                elif selected_option == 1:  # 如果当前选项是“取消”
                    return False  # 返回 False

            elif key == b'\xe0':  # 方向键
                direction = msvcrt.getch()
                if direction == b'K':  # 左方向键
                    selected_option = (selected_option - 1) % 2
                elif direction == b'M':  # 右方向键
                    selected_option = (selected_option + 1) % 2
            
            elif key == b'\x08':  # 退格键
                user_input = user_input[:-1]  # 删除最后一个字符
                
            else:
                try:
                    # 捕获用户输入的字符，忽略解码错误
                    user_input += key.decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"解码错误: {e}")

def show_progress_bar(text, progress, total, bar_length=40):
    """
    在控制台显示进度条。
    输入:
    - test: 提示词
    - progress: 当前进度（整数）
    - total: 总进度（整数）
    - bar_length: 进度条长度（默认40）
    输出:
    - 动态更新的进度条显示
    """
    # 计算进度的百分比
    percent = float(progress) / total
    # 计算进度条中多少是满的
    filled_length = int(bar_length * percent)
    
    # 生成进度条字符串
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    # 通过覆盖上一行输出，动态显示进度
    sys.stdout.write(f'\r{text}进度: |{bar}| {percent * 100:.1f}% 已完成')
    sys.stdout.flush()

    # 在进度完成时换行
    if progress == total:
        print()

def clear_console():
    """ 清屏，模拟类似 curses 的效果 """
    os.system('cls' if os.name == 'nt' else 'clear')

def render_options(input_type, array_size=None, options=None, text="选择一个选项", visible_rows=25):
    """
    输入:
    - input_type: 1表示普通列表，2表示二维数组
    - array_size: (rows, cols)，二维数组的大小 (仅当 input_type 为 2 时启用)
    - options: 普通列表或二维数组
    - text: 要显示的提示词
    - visible_rows: 最多的显示行数 默认25
    输出:
    - 选择的选项的下标（对于列表）或坐标（对于二维数组）
    """
    def get_max_width(options):
        if isinstance(options[0], list):  # 检查是否为二维数组
            return max(len(item) for row in options for item in row)
        else:
            return max(len(item) for item in options)

    # 初始化选项下标
    selected_row = 0
    selected_col = 0
    scroll_offset = 0  # 当前滚动的偏移量

    max_width = get_max_width(options) + 2  # 获取最大宽度并在两边添加2个空格用于对齐

    # 首次渲染提示文本（仅显示一次）
    rows, cols = array_size if array_size else (len(options), 1)  # 计算行和列
    print(text)  # 只输出一次提示文本
    print()

    # 渲染可见的选项
    def render_page():
        for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
            if input_type == 1:
                print("  " + options[row].ljust(max_width))
            elif input_type == 2:
                for col in range(cols):
                    print(f"  {options[row][col].ljust(max_width)}", end="")
                print()

    render_page()

    while True:
        # 使用转义码移动光标到选项部分
        for _ in range(min(visible_rows, rows)):  # 回退到选项部分
            print("\033[F", end="")

        # 重新渲染选项，只更新高亮部分
        if input_type == 1:  # 处理普通列表
            for idx in range(scroll_offset, min(scroll_offset + visible_rows, len(options))):
                padded_option = options[idx].ljust(max_width)  # 使选项左对齐并按最大宽度填充
                if idx == selected_row:
                    print(f"> {WHITE_ON_BLACK}{padded_option}{RESET}")  # 用白字黑底高亮当前选项
                else:
                    print(f"  {padded_option}")

        elif input_type == 2:  # 处理二维数组
            for row in range(scroll_offset, min(scroll_offset + visible_rows, rows)):
                for col in range(cols):
                    padded_option = options[row][col].ljust(max_width)  # 左对齐并按最大宽度填充
                    if row == selected_row and col == selected_col:
                        print(f"  {WHITE_ON_BLACK}{padded_option}{RESET}", end="")  # 用白字黑底高亮当前选项
                    else:
                        print(f"  {padded_option}", end="")
                print()  # 换行

        # 捕获键盘输入
        key = msvcrt.getch()

        if key == b'\r':  # Enter 键
            if input_type == 1:
                return selected_row  # 返回选项下标
            elif input_type == 2:
                return (selected_row, selected_col)  # 返回二维数组坐标

        elif key == b'\xe0':  # 特殊按键（方向键）
            direction = msvcrt.getch()

            if direction == b'H':  # 上方向键
                if selected_row > 0:
                    selected_row -= 1
                if selected_row < scroll_offset:
                    scroll_offset -= 1  # 向上滚动
            elif direction == b'P':  # 下方向键
                if selected_row < rows - 1:
                    selected_row += 1
                if selected_row >= scroll_offset + visible_rows:
                    scroll_offset += 1  # 向下滚动
            elif direction == b'K':  # 左方向键 (仅对二维数组有效)
                if input_type == 2:
                    selected_col = (selected_col - 1) % cols
            elif direction == b'M':  # 右方向键 (仅对二维数组有效)
                if input_type == 2:
                    selected_col = (selected_col + 1) % cols

def display_aligned_text(text_list, leftorright='left', padding=2):
    """
    在控制台显示文本，并确保对齐。
    输入:
    - text_list: 字符串列表
    - leftorright: 对齐方式，'left'表示左对齐，'right'表示右对齐，默认左对齐
    - padding: 在文本右侧添加的空格，默认是2个空格
    输出:
    - 对齐文本的显示
    """
    max_length = max([len(text) for text in text_list]) + padding

    for text in text_list:
        if leftorright == 'left':
            print(text.ljust(max_length))  # 左对齐
        elif leftorright == 'right':
            print(text.rjust(max_length))  # 右对齐

def showing():
    # # 示例调用 render_options 函数，选择并高亮显示选项
    # result = input_box_with_prompt("请输入你的名字:", "确定", "取消")
    # if result:
    #     print(f"你输入的是: {result}")
    # else:
        # print("输入被取消")
    # for i in range(100):
    #     show_progress_bar("下载中..",progress=i,total=100)
    #     time.sleep(0.1)
    text_showing_render = "欢迎使用TeiGUI-Lib V1 测试版\n你正处于__main__模式(展示模式)\n请选择你要看的功能展示:"
    a = render_options(input_type=1,options=["二维数组显示","进度显示","文本显示(左对齐)","文本显示(右对齐)","文本输入"],text=text_showing_render)
    if(a == 0):
        a = render_options(2,array_size=(2,2),options=[['A1','B1'],['A2','B2']],text="二维数组测试")
        print(a)
    elif(a == 1):
        for i in range(100):
            show_progress_bar("下载中..",progress=i,total=100)
            time.sleep(0.01)
    elif(a==2):
        display_aligned_text(text_list=["字符串文本展示","欢迎使用TeiGUI"],leftorright='left')
    elif(a==3):
        display_aligned_text(text_list=["字符串文本展示","欢迎使用TeiGUI!!!!!!!!!!!"],leftorright='right')
    elif(a==4):
        result = input_box_with_prompt("请输入(目前不支持中文):", "确定", "取消")
        if result:
            print(f"你输入的是: {result}")
        else:
            print("输入被取消")
if __name__ == '__main__':
    showing()
    input("__main__finshed press enter to exit \n return 0")
