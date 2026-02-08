"""
俄罗斯方块游戏
使用 tkinter 库实现（Python 自带，无需安装）
"""

import tkinter as tk
import random

# 游戏设置
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 颜色定义
COLORS = [
    "#00FFFF",  # I - 青色
    "#FFFF00",  # O - 黄色
    "#800080",  # T - 紫色
    "#00FF00",  # S - 绿色
    "#FF0000",  # Z - 红色
    "#0000FF",  # J - 蓝色
    "#FFA500",  # L - 橙色
]

# 方块形状定义
SHAPES = [
    # I
    [[1, 1, 1, 1]],
    # O
    [[1, 1],
     [1, 1]],
    # T
    [[0, 1, 0],
     [1, 1, 1]],
    # S
    [[0, 1, 1],
     [1, 1, 0]],
    # Z
    [[1, 1, 0],
     [0, 1, 1]],
    # J
    [[1, 0, 0],
     [1, 1, 1]],
    # L
    [[0, 0, 1],
     [1, 1, 1]],
]


class Tetris:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("俄罗斯方块")
        self.root.resizable(False, False)

        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(padx=10, pady=10)

        # 游戏画布
        self.canvas = tk.Canvas(
            self.main_frame,
            width=GRID_WIDTH * BLOCK_SIZE,
            height=GRID_HEIGHT * BLOCK_SIZE,
            bg="#16213e",
            highlightthickness=2,
            highlightbackground="#0f3460"
        )
        self.canvas.pack(side=tk.LEFT)

        # 信息面板
        self.info_frame = tk.Frame(self.main_frame, bg="#1a1a2e", width=150)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))

        # 下一个方块预览
        tk.Label(self.info_frame, text="下一个", font=("Arial", 14, "bold"),
                 fg="white", bg="#1a1a2e").pack(pady=(0, 5))
        self.preview_canvas = tk.Canvas(
            self.info_frame, width=120, height=80,
            bg="#16213e", highlightthickness=1, highlightbackground="#0f3460"
        )
        self.preview_canvas.pack()

        # 分数
        tk.Label(self.info_frame, text="分数", font=("Arial", 14, "bold"),
                 fg="white", bg="#1a1a2e").pack(pady=(20, 5))
        self.score_label = tk.Label(self.info_frame, text="0", font=("Arial", 18),
                                     fg="#e94560", bg="#1a1a2e")
        self.score_label.pack()

        # 等级
        tk.Label(self.info_frame, text="等级", font=("Arial", 14, "bold"),
                 fg="white", bg="#1a1a2e").pack(pady=(15, 5))
        self.level_label = tk.Label(self.info_frame, text="1", font=("Arial", 18),
                                     fg="#e94560", bg="#1a1a2e")
        self.level_label.pack()

        # 消除行数
        tk.Label(self.info_frame, text="行数", font=("Arial", 14, "bold"),
                 fg="white", bg="#1a1a2e").pack(pady=(15, 5))
        self.lines_label = tk.Label(self.info_frame, text="0", font=("Arial", 18),
                                     fg="#e94560", bg="#1a1a2e")
        self.lines_label.pack()

        # 操作说明
        help_text = """
操作说明:
← → 移动
↑ 旋转
↓ 加速
空格 硬降
P 暂停
R 重新开始
        """
        tk.Label(self.info_frame, text=help_text, font=("Arial", 10),
                 fg="#aaa", bg="#1a1a2e", justify=tk.LEFT).pack(pady=(30, 0))

        # 绑定键盘事件
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.rotate)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<space>", self.hard_drop)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<P>", self.toggle_pause)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)

        # 初始化游戏
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_color = 0
        self.next_piece = None
        self.next_color = 0
        self.fall_speed = 500
        self.spawn_piece()
        self.update_info()
        self.game_loop()

    def spawn_piece(self):
        """生成新方块"""
        if self.next_piece is None:
            idx = random.randint(0, len(SHAPES) - 1)
            self.next_piece = [row[:] for row in SHAPES[idx]]
            self.next_color = idx

        self.current_piece = self.next_piece
        self.current_color = self.next_color

        idx = random.randint(0, len(SHAPES) - 1)
        self.next_piece = [row[:] for row in SHAPES[idx]]
        self.next_color = idx

        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0

        if not self.valid_position(self.current_piece, self.current_x, self.current_y):
            self.game_over = True

        self.draw_preview()

    def valid_position(self, piece, x, y):
        """检查位置是否有效"""
        for row_idx, row in enumerate(piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    if new_x < 0 or new_x >= GRID_WIDTH:
                        return False
                    if new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def rotate_piece(self, piece):
        """旋转方块（顺时针90度）"""
        rows = len(piece)
        cols = len(piece[0])
        rotated = [[piece[rows - 1 - j][i] for j in range(rows)] for i in range(cols)]
        return rotated

    def lock_piece(self):
        """锁定当前方块到网格"""
        for row_idx, row in enumerate(self.current_piece):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_y = self.current_y + row_idx
                    grid_x = self.current_x + col_idx
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_color + 1

    def clear_lines(self):
        """消除完整的行"""
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines_to_clear.append(i)

        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * GRID_WIDTH)

        lines_count = len(lines_to_clear)
        if lines_count > 0:
            self.lines_cleared += lines_count
            scores = [0, 100, 300, 500, 800]
            self.score += scores[min(lines_count, 4)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)
            self.update_info()

    def drop_piece(self):
        """方块下落一格"""
        if self.valid_position(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
            return True
        else:
            self.lock_piece()
            self.clear_lines()
            self.spawn_piece()
            return False

    def move_left(self, event=None):
        """向左移动"""
        if not self.game_over and not self.paused:
            if self.valid_position(self.current_piece, self.current_x - 1, self.current_y):
                self.current_x -= 1
                self.draw()

    def move_right(self, event=None):
        """向右移动"""
        if not self.game_over and not self.paused:
            if self.valid_position(self.current_piece, self.current_x + 1, self.current_y):
                self.current_x += 1
                self.draw()

    def move_down(self, event=None):
        """向下移动（加速）"""
        if not self.game_over and not self.paused:
            if self.drop_piece():
                self.score += 1
                self.update_info()
            self.draw()

    def rotate(self, event=None):
        """旋转方块"""
        if not self.game_over and not self.paused:
            rotated = self.rotate_piece(self.current_piece)
            if self.valid_position(rotated, self.current_x, self.current_y):
                self.current_piece = rotated
            elif self.valid_position(rotated, self.current_x - 1, self.current_y):
                self.current_x -= 1
                self.current_piece = rotated
            elif self.valid_position(rotated, self.current_x + 1, self.current_y):
                self.current_x += 1
                self.current_piece = rotated
            self.draw()

    def hard_drop(self, event=None):
        """硬降"""
        if not self.game_over and not self.paused:
            while self.valid_position(self.current_piece, self.current_x, self.current_y + 1):
                self.current_y += 1
                self.score += 2
            self.lock_piece()
            self.clear_lines()
            self.spawn_piece()
            self.update_info()
            self.draw()

    def toggle_pause(self, event=None):
        """切换暂停状态"""
        if not self.game_over:
            self.paused = not self.paused
            if not self.paused:
                self.game_loop()
            self.draw()

    def restart(self, event=None):
        """重新开始游戏"""
        self.reset_game()

    def update_info(self):
        """更新信息显示"""
        self.score_label.config(text=str(self.score))
        self.level_label.config(text=str(self.level))
        self.lines_label.config(text=str(self.lines_cleared))

    def draw_block(self, canvas, x, y, color, size=BLOCK_SIZE, offset_x=0, offset_y=0):
        """绘制单个方块"""
        x1 = offset_x + x * size
        y1 = offset_y + y * size
        x2 = x1 + size - 2
        y2 = y1 + size - 2
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333")
        # 高光效果
        canvas.create_line(x1, y1, x2, y1, fill="#fff", width=1)
        canvas.create_line(x1, y1, x1, y2, fill="#fff", width=1)

    def draw_preview(self):
        """绘制下一个方块预览"""
        self.preview_canvas.delete("all")
        if self.next_piece:
            piece_width = len(self.next_piece[0])
            piece_height = len(self.next_piece)
            offset_x = (120 - piece_width * 25) // 2
            offset_y = (80 - piece_height * 25) // 2

            for row_idx, row in enumerate(self.next_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        self.draw_block(
                            self.preview_canvas,
                            col_idx, row_idx,
                            COLORS[self.next_color],
                            size=25,
                            offset_x=offset_x,
                            offset_y=offset_y
                        )

    def draw(self):
        """绘制游戏画面"""
        self.canvas.delete("all")

        # 绘制网格线
        for i in range(GRID_WIDTH + 1):
            x = i * BLOCK_SIZE
            self.canvas.create_line(x, 0, x, GRID_HEIGHT * BLOCK_SIZE, fill="#1f4068")
        for i in range(GRID_HEIGHT + 1):
            y = i * BLOCK_SIZE
            self.canvas.create_line(0, y, GRID_WIDTH * BLOCK_SIZE, y, fill="#1f4068")

        # 绘制已锁定的方块
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_block(self.canvas, x, y, COLORS[cell - 1])

        # 绘制当前方块
        if self.current_piece:
            for row_idx, row in enumerate(self.current_piece):
                for col_idx, cell in enumerate(row):
                    if cell:
                        self.draw_block(
                            self.canvas,
                            self.current_x + col_idx,
                            self.current_y + row_idx,
                            COLORS[self.current_color]
                        )

        # 游戏结束
        if self.game_over:
            self.canvas.create_rectangle(
                0, GRID_HEIGHT * BLOCK_SIZE // 2 - 40,
                GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE // 2 + 40,
                fill="#1a1a2e", outline=""
            )
            self.canvas.create_text(
                GRID_WIDTH * BLOCK_SIZE // 2,
                GRID_HEIGHT * BLOCK_SIZE // 2 - 15,
                text="游戏结束",
                font=("Arial", 20, "bold"),
                fill="#e94560"
            )
            self.canvas.create_text(
                GRID_WIDTH * BLOCK_SIZE // 2,
                GRID_HEIGHT * BLOCK_SIZE // 2 + 15,
                text="按 R 重新开始",
                font=("Arial", 14),
                fill="white"
            )

        # 暂停
        if self.paused:
            self.canvas.create_rectangle(
                0, GRID_HEIGHT * BLOCK_SIZE // 2 - 30,
                GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE // 2 + 30,
                fill="#1a1a2e", outline=""
            )
            self.canvas.create_text(
                GRID_WIDTH * BLOCK_SIZE // 2,
                GRID_HEIGHT * BLOCK_SIZE // 2,
                text="已暂停",
                font=("Arial", 20, "bold"),
                fill="white"
            )

    def game_loop(self):
        """游戏主循环"""
        if not self.game_over and not self.paused:
            self.drop_piece()
            self.draw()
            self.root.after(self.fall_speed, self.game_loop)
        elif self.game_over:
            self.draw()

    def run(self):
        """运行游戏"""
        self.draw()
        self.root.mainloop()


if __name__ == "__main__":
    game = Tetris()
    game.run()
