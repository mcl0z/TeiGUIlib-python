import os
import sys
import msvcrt
from enum import Enum
from typing import List, Tuple, Union

# 启用ANSI转义码
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# 颜色代码
class Color:
    RESET = '\033[0m'
    WHITE_BG = '\033[30;47m'
    BLUE_TEXT = '\033[34m'
    HIGHLIGHT = '\033[7m'
    SELECTED_BG = '\033[44m'

# 组件类型枚举
class ComponentType(Enum):
    INPUT_BOX = 1
    LIST_BOX = 2
    BUTTON_GROUP = 3
    GRID_BOX = 4

class LayoutManager:
    """网格布局管理器"""
    def __init__(self):
        self.components = []
        self.row_config = {}
        self.col_config = {}
        self._calculated_positions = {}

    def add_component(self, component, row, column, 
                     rowspan=1, columnspan=1, 
                     padx=2, pady=1, 
                     sticky='nsew'):
        """添加组件到布局"""
        self.components.append({
            'component': component,
            'row': row,
            'column': column,
            'rowspan': rowspan,
            'columnspan': columnspan,
            'padx': padx,
            'pady': pady,
            'sticky': sticky.lower()
        })

    def calculate_layout(self):
        """计算所有组件的实际位置"""
        # 计算列宽和行高
        col_widths = {}
        row_heights = {}
        
        for comp in self.components:
            c = comp['component']
            # 更新列宽
            for col in range(comp['column'], comp['column'] + comp['columnspan']):
                current = col_widths.get(col, 0)
                col_width = c.width // comp['columnspan']
                if col_width > current:
                    col_widths[col] = col_width
            # 更新行高
            for row in range(comp['row'], comp['row'] + comp['rowspan']):
                current = row_heights.get(row, 0)
                row_height = c.height // comp['rowspan']
                if row_height > current:
                    row_heights[row] = row_height

        # 计算累计偏移量
        col_offsets = {0: 0}
        for col in sorted(col_widths.keys()):
            prev = max(col_offsets.keys())
            col_offsets[col+1] = col_offsets[prev] + col_widths.get(col, 10) + 2

        row_offsets = {0: 0}
        for row in sorted(row_heights.keys()):
            prev = max(row_offsets.keys())
            row_offsets[row+1] = row_offsets[prev] + row_heights.get(row, 3) + 1

        # 计算组件位置
        self._calculated_positions = {}
        for comp in self.components:
            c = comp['component']
            # 计算起始位置
            x = col_offsets[comp['column']] + comp['padx']
            y = row_offsets[comp['row']] + comp['pady']
            
            # 计算实际占用的空间
            total_col_width = sum(col_widths.get(col, 10) for col in 
                                range(comp['column'], comp['column'] + comp['columnspan']))
            total_row_height = sum(row_heights.get(row, 3) for row in 
                                 range(comp['row'], comp['row'] + comp['rowspan']))
            
            # 处理对齐方式
            sticky = comp['sticky']
            if 'e' in sticky:
                x += total_col_width - c.width
            elif 'w' in sticky:
                pass  # 默认左对齐
            else:  # 居中
                x += (total_col_width - c.width) // 2

            if 's' in sticky:
                y += total_row_height - c.height
            elif 'n' in sticky:
                pass  # 默认顶对齐
            else:  # 居中
                y += (total_row_height - c.height) // 2

            self._calculated_positions[c] = (x, y)

    def get_position(self, component):
        """获取组件计算后的位置"""
        return self._calculated_positions.get(component, (0, 0))

class UIComponent:
    """UI组件基类"""
    def __init__(self, component_type, width=30, height=5):
        self.type = component_type
        self.width = width
        self.height = height
        self.has_focus = False
        self.visible = True
        self.title = "Untitled"
        self.prev_state = {}

    def render(self, x, y):
        """渲染组件（需要子类实现）"""
        pass

    def handle_input(self, key):
        """处理输入（需要子类实现）"""
        pass

    def get_cursor_pos(self, x, y):
        """获取光标应停留的位置"""
        return (x, y + 1)

class InputBox(UIComponent):
    """输入框组件"""
    def __init__(self, title="Input", width=30):
        super().__init__(ComponentType.INPUT_BOX, width, 3)
        self.title = title
        self.text = ""
        self.cursor_pos = 0
        self.max_length = width - 2

    def render(self, x, y):
        if not self.visible: 
            return
            
        current_state = {
            "text": self.text,
            "cursor": self.cursor_pos,
            "focus": self.has_focus
        }
        if current_state == self.prev_state:
            return
            
        self.prev_state = current_state.copy()

        # 绘制标题
        sys.stdout.write(f"\033[{y+1};{x+1}H")
        print(f"{Color.BLUE_TEXT}{self.title}{Color.RESET}")

        # 绘制边框和内容
        border_top = '┌' + '─'*(self.width-2) + '┐'
        content_line = f"│{self.text.ljust(self.width-2)}│"
        border_bottom = '└' + '─'*(self.width-2) + '┘'

        color = Color.WHITE_BG if self.has_focus else ""
        sys.stdout.write(f"\033[{y+2};{x+1}H")
        print(f"{color}{border_top}{Color.RESET}")

        sys.stdout.write(f"\033[{y+3};{x+1}H")
        print(f"{color}{content_line}{Color.RESET}")

        sys.stdout.write(f"\033[{y+4};{x+1}H")
        print(f"{color}{border_bottom}{Color.RESET}")

        # 定位光标
        x_pos = x + 2 + min(self.cursor_pos, self.width-3)
        sys.stdout.write(f"\033[{y+3};{x_pos}H")

    def handle_input(self, key):
        if key == '\x08':  # Backspace
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key == '\r':
            return self.text
        elif key in ('\x00', '\xe0'):
            key = msvcrt.getwch()
            if key == 'K':  # Left
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif key == 'M':  # Right
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
        elif key.isprintable():
            if len(self.text) < self.max_length:
                self.text = self.text[:self.cursor_pos] + key + self.text[self.cursor_pos:]
                self.cursor_pos += 1
        return None

    def get_cursor_pos(self, x, y):
        return (x + 2 + self.cursor_pos, y + 3)
class ListBox(UIComponent):
    """列表框组件（支持多选）"""
    def __init__(self, title="List", width=30, height=8, multi_select=False):
        super().__init__(ComponentType.LIST_BOX, width, height)
        self.title = title
        self.items = []
        self.cursor_pos = 0
        self.selected_indices = set()
        self.multi_select = multi_select
        self.scroll_offset = 0

    def render(self, x, y):
        if not self.visible:
            return

        current_state = {
            "cursor": self.cursor_pos,
            "selected": self.selected_indices.copy(),
            "focus": self.has_focus
        }
        if current_state == self.prev_state:
            return
        self.prev_state = current_state.copy()

        # 绘制标题
        sys.stdout.write(f"\033[{y+1};{x+1}H")
        print(f"{Color.BLUE_TEXT}{self.title}{Color.RESET}")

        # 绘制边框
        border_top = '┌' + '─'*(self.width-2) + '┐'
        border_bottom = '└' + '─'*(self.width-2) + '┘'
        sys.stdout.write(f"\033[{y+2};{x+1}H")
        print(border_top)
        
        for dy in range(self.height-2):
            sys.stdout.write(f"\033[{y+3+dy};{x+1}H")
            print("│" + " "*(self.width-2) + "│")
            
        sys.stdout.write(f"\033[{y+self.height};{x+1}H")
        print(border_bottom)

        # 绘制内容
        max_visible = self.height - 2
        start = max(0, min(self.cursor_pos - max_visible//2, len(self.items)-max_visible))
        
        for i in range(start, min(start+max_visible, len(self.items))):
            dy = i - start
            cy = y + 3 + dy
            sys.stdout.write(f"\033[{cy};{x+2}H")
            
            is_selected = i in self.selected_indices
            is_cursor = i == self.cursor_pos
            
            prefix = "▶ " if is_cursor and self.has_focus else "  "
            text = f"{prefix}{self.items[i]}".ljust(self.width-4)
            
            if is_selected:
                text = f"{Color.SELECTED_BG}{text}{Color.RESET}"
            elif is_cursor and self.has_focus:
                text = f"{Color.HIGHLIGHT}{text}{Color.RESET}"
                
            sys.stdout.write(text)

    def handle_input(self, key):
        if key in ('\x00', '\xe0'):
            key = msvcrt.getwch()
            if key == 'H':  # Up
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif key == 'P':  # Down
                self.cursor_pos = min(len(self.items)-1, self.cursor_pos + 1)
        elif key == ' ' and self.multi_select:
            if self.cursor_pos in self.selected_indices:
                self.selected_indices.remove(self.cursor_pos)
            else:
                self.selected_indices.add(self.cursor_pos)
        elif key == '\r':
            return sorted(self.selected_indices) if self.multi_select else self.cursor_pos
        return None

class GridBox(UIComponent):
    """二维表格选择组件"""
    def __init__(self, title="Grid", width=30, height=10, rows=5, cols=5, multi_select=False):
        super().__init__(ComponentType.GRID_BOX, width, height)
        self.title = title
        self.rows = rows
        self.cols = cols
        self.cursor_row = 0
        self.cursor_col = 0
        self.selected_cells = set()
        self.multi_select = multi_select
        self.cell_width = (width-2) // cols

    def render(self, x, y):
        if not self.visible:
            return

        current_state = {
            "cursor": (self.cursor_row, self.cursor_col),
            "selected": self.selected_cells.copy(),
            "focus": self.has_focus
        }
        if current_state == self.prev_state:
            return
        self.prev_state = current_state.copy()

        # 绘制标题
        sys.stdout.write(f"\033[{y+1};{x+1}H")
        print(f"{Color.BLUE_TEXT}{self.title}{Color.RESET}")

        # 绘制边框
        border_top = '┌' + '─'*(self.width-2) + '┐'
        border_bottom = '└' + '─'*(self.width-2) + '┘'
        sys.stdout.write(f"\033[{y+2};{x+1}H")
        print(border_top)
        
        for dy in range(self.height-2):
            sys.stdout.write(f"\033[{y+3+dy};{x+1}H")
            print("│" + " "*(self.width-2) + "│")
            
        sys.stdout.write(f"\033[{y+self.height};{x+1}H")
        print(border_bottom)

        # 绘制单元格
        for r in range(self.rows):
            for c in range(self.cols):
                cell_x = x + 2 + c * self.cell_width
                cell_y = y + 3 + r
                sys.stdout.write(f"\033[{cell_y};{cell_x}H")
                
                is_selected = (r, c) in self.selected_cells
                is_cursor = (r == self.cursor_row and c == self.cursor_col)
                content = f"[{r},{c}]".center(self.cell_width)
                
                if is_selected:
                    content = f"{Color.SELECTED_BG}{content}{Color.RESET}"
                elif is_cursor and self.has_focus:
                    content = f"{Color.HIGHLIGHT}{content}{Color.RESET}"
                else:
                    content = f"{Color.RESET}{content}"
                    
                sys.stdout.write(content)

    def handle_input(self, key):
        if key in ('\x00', '\xe0'):
            key = msvcrt.getwch()
            if key == 'H' and self.cursor_row > 0:
                self.cursor_row -= 1
            elif key == 'P' and self.cursor_row < self.rows-1:
                self.cursor_row += 1
            elif key == 'K' and self.cursor_col > 0:
                self.cursor_col -= 1
            elif key == 'M' and self.cursor_col < self.cols-1:
                self.cursor_col += 1
        elif key == ' ' and self.multi_select:
            cell = (self.cursor_row, self.cursor_col)
            if cell in self.selected_cells:
                self.selected_cells.remove(cell)
            else:
                self.selected_cells.add(cell)
        elif key == '\r':
            return sorted(self.selected_cells) if self.multi_select else (self.cursor_row, self.cursor_col)
        return None

class ButtonGroup(UIComponent):
    """按钮组组件"""
    def __init__(self, title="Actions", buttons=["OK", "Cancel"], width=30):
        super().__init__(ComponentType.BUTTON_GROUP, width, 3)
        self.title = title
        self.buttons = buttons
        self.selected = 0

    def render(self, x, y):
        if not self.visible:
            return

        current_state = {
            "selected": self.selected,
            "focus": self.has_focus
        }
        if current_state == self.prev_state:
            return
        self.prev_state = current_state.copy()

        # 绘制标题
        sys.stdout.write(f"\033[{y+1};{x+1}H")
        print(f"{Color.BLUE_TEXT}{self.title}{Color.RESET}")

        # 绘制按钮行
        line = ""
        for i, btn in enumerate(self.buttons):
            if i == self.selected and self.has_focus:
                line += f"{Color.WHITE_BG}[{btn}]{Color.RESET} "
            else:
                line += f"[{btn}] "
        
        sys.stdout.write(f"\033[{y+2};{x+1}H")
        print(line.center(self.width))

    def handle_input(self, key):
        if key in ('\x00', '\xe0'):
            key = msvcrt.getwch()
            if key == 'K':  # Left
                self.selected = max(0, self.selected - 1)
            elif key == 'M':  # Right
                self.selected = min(len(self.buttons)-1, self.selected + 1)
        elif key == '\r':
            return self.buttons[self.selected]
        return None
class UIManager:
    """UI管理引擎"""
    def __init__(self):
        self.layout = LayoutManager()
        self.components = []
        self.focus_index = 0
        self.running = False

    def add_component(self, component, row, column,**kwargs):
        """添加组件到布局"""
        self.layout.add_component(component, row, column,**kwargs)
        self.components.append(component)
        if len(self.components) == 1:
            self.components[0].has_focus = True

    def switch_focus(self):     
        """切换焦点到下一个组件"""
        if len(self.components) < 2:
            return
        self.components[self.focus_index].has_focus = False
        self.focus_index = (self.focus_index + 1) % len(self.components)
        self.components[self.focus_index].has_focus = True

    def initialize(self):
        """初始化界面"""
        self.layout.calculate_layout()
        sys.stdout.write("\033[2J")  # 清屏
        for comp in self.components:
            x, y = self.layout.get_position(comp)
            comp.render(x, y)
        sys.stdout.flush()

    def redraw(self):
        """重绘所有组件"""
        for comp in self.components:
            x, y = self.layout.get_position(comp)
            comp.render(x, y)
        # 定位光标到当前焦点组件
        current = self.components[self.focus_index]
        x, y = current.get_cursor_pos(*self.layout.get_position(current))
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    def main_loop(self):
        """主事件循环"""
        self.running = True
        self.initialize()
        while self.running:
            key = msvcrt.getwch()
            if key == '\t':  # Tab切换焦点
                self.switch_focus()
                self.redraw()
            elif key == '\x1b':  # ESC退出
                self.running = False
            else:
                # 将输入传递给当前焦点组件
                current = self.components[self.focus_index]
                result = current.handle_input(key)
                if result is not None:
                    self.handle_result(result)
                self.redraw()

    def handle_result(self, result):
        """处理组件返回结果"""
        print(f"\n操作结果: {result}")
        # 可根据需要添加业务逻辑处理

if __name__ == "__main__":
    # 创建UI管理器
    ui = UIManager()

    # 第一行：两个输入框
    ui.add_component(
        InputBox(title="用户名", width=30),
        row=0, column=0, columnspan=2, sticky='w'
    )
    ui.add_component(
        InputBox(title="密码", width=20),
        row=0, column=2, sticky='e'
    )

    # # 第二行：左右两个列表
    # single_list = ListBox(title="单选列表", width=35, height=8)
    # single_list.items = [f"项目 {i}" for i in range(10)]
    # ui.add_component(single_list, row=1, column=0, rowspan=2, sticky='nsew')

    # multi_list = ListBox(title="多选列表", width=35, height=8, multi_select=True)
    # multi_list.items = [f"选项 {i}" for i in range(10)]
    # ui.add_component(multi_list, row=1, column=1, rowspan=2, sticky='nsew')

    # # 第三行：多选表格
    # grid = GridBox(title="数据表格", width=60, height=10, rows=5, cols=5, multi_select=True)
    # ui.add_component(grid, row=3, column=0, columnspan=2, rowspan=3, sticky='nsew')

    # 右侧边栏
    right_grid = GridBox(title="属性", width=30, height=15, rows=8, cols=3)
    ui.add_component(right_grid, row=0, column=3, rowspan=6, sticky='nsew')

    # 底部按钮组
    buttons = ButtonGroup(title="操作", buttons=["保存", "删除", "退出"], width=40)
    ui.add_component(buttons, row=6, column=0, columnspan=3, sticky='center')

    # 运行界面
    ui.main_loop()
    print("\033[0m")  # 重置终端样式
