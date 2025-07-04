# =================================================================
# المرحلة 0: استيراد المكتبات وتجهيز البيئة
# =================================================================

# --- الخطوة 0.1: استيراد المكتبات المطلوبة ---
import pygame
import math
from collections import deque      # لاستخدام طابور (Queue) فعال في خوارزمية BFS
from queue import PriorityQueue  # لاستخدام طابور الأولوية (Priority Queue) في خوارزمية A*



# =================================================================
# المرحلة 1: تعريف الثوابت والإعدادات العامة
# =================================================================
# الهدف: مركزة كل الإعدادات الثابتة في مكان واحد لسهولة التعديل.

# --- الخطوة 1.1: إعدادات نافذة Pygame ---
WIDTH = 800  # عرض النافذة بالبكسل
ROWS = 50    # عدد الصفوف والأعمدة في الشبكة
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("محلل المتاهة المرئي: A*, BFS, DFS")

# --- الخطوة 1.2: تعريف لوحة الألوان ---
# نستخدم متغيرات لتسهيل قراءة الكود وفهم دور كل لون.
RED = (255, 0, 0)       # خلية مغلقة (تمت زيارتها)
GREEN = (0, 255, 0)     # خلية مفتوحة (في قائمة الانتظار)
BLUE = (0, 0, 255)      # خلية النهاية
YELLOW = (255, 255, 0)  # خلية في المسار النهائي
WHITE = (255, 255, 255) # خلية فارغة
BLACK = (0, 0, 0)       # خلية جدار
PURPLE = (128, 0, 128)  # خلية البداية
GREY = (128, 128, 128)  # لون خطوط الشبكة

# --- الخطوة 1.3: تعريف حالات الخلية ---
# نستخدم أرقامًا لتمثيل حالة كل خلية بدلاً من الاعتماد على الألوان مباشرة.
STATE_EMPTY = 0
STATE_WALL = 1
STATE_START = 2
STATE_END = 3
STATE_CLOSED = 4  # تمت زيارته
STATE_OPEN = 5    # في قائمة الانتظار
STATE_PATH = 6    # المسار النهائي

# --- الخطوة 1.4: ربط كل حالة بلون للرسم ---
# قاموس لترجمة حالة الخلية الرقمية إلى لون مرئي.
STATE_COLORS = {
    STATE_EMPTY: WHITE,
    STATE_WALL: BLACK,
    STATE_START: PURPLE,
    STATE_END: BLUE,
    STATE_CLOSED: RED,
    STATE_OPEN: GREEN,
    STATE_PATH: YELLOW
}



# =================================================================
# المرحلة 2: تعريف الدوال المساعدة للرسم والشبكة
# =================================================================

# --- الخطوة 2.1: دالة لرسم الشبكة بالكامل ---
def draw_grid(win, grid, rows, width):
    """دالة لرسم الشبكة بأكملها بناءً على حالاتها الرقمية."""
    win.fill(WHITE)
    gap = width // rows
    for row_idx, row in enumerate(grid):
        for col_idx, state in enumerate(row):
            color = STATE_COLORS[state]
            pygame.draw.rect(win, color, (row_idx * gap, col_idx * gap, gap, gap))

    # رسم خطوط الشبكة
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))
    pygame.display.update()

# --- الخطوة 2.2: دالة لتحويل إحداثيات الفأرة إلى إحداثيات الشبكة ---
def get_clicked_pos(pos, rows, width):
    """تحول إحداثيات (x, y) بالبكسل إلى (صف, عمود) في الشبكة."""
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

# --- الخطوة 2.3: دالة لإيجاد جيران خلية صالحة للحركة ---
def get_neighbors(pos, grid):
    """تجد الجيران الصالحين (ليسوا جدرانًا) لخلية معينة."""
    row, col = pos
    neighbors = []
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # أسفل, أعلى, يمين, يسار
    for move_r, move_c in moves:
        n_row, n_col = row + move_r, col + move_c
        # التحقق من أن الجار داخل حدود الشبكة
        if 0 <= n_row < ROWS and 0 <= n_col < ROWS:
            # التحقق من أن الجار ليس جداراً
            if grid[n_row][n_col] != STATE_WALL:
                neighbors.append((n_row, n_col))
    return neighbors

# --- الخطوة 2.4: دالة لإعادة بناء المسار النهائي ورسمه ---
def reconstruct_path(parent_map, current_pos, grid):
    """تتتبع المسار من النهاية إلى البداية باستخدام قاموس الآباء وترسمه."""
    while current_pos in parent_map:
        current_pos = parent_map[current_pos]
        if grid[current_pos[0]][current_pos[1]] != STATE_START:
            grid[current_pos[0]][current_pos[1]] = STATE_PATH



# =================================================================
# المرحلة 3: تطبيق خوارزميات البحث
# =================================================================
# الهدف: تنفيذ المنطق الأساسي لكل خوارزمية بحث.

# --- الخطوة 3.1: دالة الاستدلال (Heuristic) لخوارزمية A* ---
def heuristic(pos1, pos2):
    """تحسب مسافة مانهاتن (Manhattan Distance) بين نقطتين."""
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)

# --- الخطوة 3.2: خوارزمية البحث بالعرض أولاً (BFS) ---
def bfs(grid, start_pos, end_pos, draw_func):
    """تنفذ خوارزمية BFS لإيجاد أقصر مسار (بأقل عدد من الخطوات)."""
    queue = deque([start_pos])
    visited = {start_pos}
    parent_map = {}  # قاموس لتتبع المسار: {child_pos: parent_pos}

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        current_pos = queue.popleft()
        if current_pos == end_pos:
            reconstruct_path(parent_map, current_pos, grid)
            return True

        if grid[current_pos[0]][current_pos[1]] not in [STATE_START, STATE_END]:
            grid[current_pos[0]][current_pos[1]] = STATE_CLOSED

        for neighbor_pos in get_neighbors(current_pos, grid):
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                parent_map[neighbor_pos] = current_pos
                queue.append(neighbor_pos)
                if grid[neighbor_pos[0]][neighbor_pos[1]] != STATE_END:
                    grid[neighbor_pos[0]][neighbor_pos[1]] = STATE_OPEN
        
        draw_func()  # تحديث الرسم بعد كل خطوة
    return False

# --- الخطوة 3.3: خوارزمية البحث بالعمق أولاً (DFS) ---
def dfs(grid, start_pos, end_pos, draw_func):
    """تنفذ خوارزمية DFS (لا تضمن أقصر مسار)."""
    stack = [start_pos]
    visited = {start_pos}
    parent_map = {}

    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        current_pos = stack.pop()
        if current_pos == end_pos:
            reconstruct_path(parent_map, current_pos, grid)
            return True
            
        if grid[current_pos[0]][current_pos[1]] not in [STATE_START, STATE_END]:
            grid[current_pos[0]][current_pos[1]] = STATE_CLOSED
        
        for neighbor_pos in reversed(get_neighbors(current_pos, grid)):
            if neighbor_pos not in visited:
                visited.add(neighbor_pos)
                parent_map[neighbor_pos] = current_pos
                stack.append(neighbor_pos)
                if grid[neighbor_pos[0]][neighbor_pos[1]] != STATE_END:
                    grid[neighbor_pos[0]][neighbor_pos[1]] = STATE_OPEN
        draw_func()
    return False

# --- الخطوة 3.4: خوارزمية البحث A* (A-Star) ---
def a_star(grid, start_pos, end_pos, draw_func):
    """تنفذ خوارزمية A* الذكية لإيجاد أقصر مسار بكفاءة عالية."""
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start_pos))
    open_set_hash = {start_pos}
    
    parent_map = {}
    g_score = { (r,c): float("inf") for r in range(ROWS) for c in range(ROWS) }
    g_score[start_pos] = 0
    f_score = { (r,c): float("inf") for r in range(ROWS) for c in range(ROWS) }
    f_score[start_pos] = heuristic(start_pos, end_pos)

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        current_pos = open_set.get()[2]
        open_set_hash.remove(current_pos)

        if current_pos == end_pos:
            reconstruct_path(parent_map, current_pos, grid)
            return True

        for neighbor_pos in get_neighbors(current_pos, grid):
            temp_g_score = g_score[current_pos] + 1
            if temp_g_score < g_score[neighbor_pos]:
                parent_map[neighbor_pos] = current_pos
                g_score[neighbor_pos] = temp_g_score
                f_score[neighbor_pos] = temp_g_score + heuristic(neighbor_pos, end_pos)
                if neighbor_pos not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor_pos], count, neighbor_pos))
                    open_set_hash.add(neighbor_pos)
                    if grid[neighbor_pos[0]][neighbor_pos[1]] != STATE_END:
                         grid[neighbor_pos[0]][neighbor_pos[1]] = STATE_OPEN
        
        draw_func()
        if grid[current_pos[0]][current_pos[1]] not in [STATE_START, STATE_END]:
            grid[current_pos[0]][current_pos[1]] = STATE_CLOSED
    return False



# =================================================================
# المرحلة 4: حلقة البرنامج الرئيسية (Main Loop)
# =================================================================
# الهدف: إدارة تفاعل المستخدم مع البرنامج وتشغيل الخوارزميات.

def main():
    # --- الخطوة 4.1: تهيئة متغيرات اللعبة ---
    grid = [[STATE_EMPTY for _ in range(ROWS)] for _ in range(ROWS)]
    start_pos = None
    end_pos = None
    run = True

    # --- الخطوة 4.2: بدء حلقة اللعبة الرئيسية ---
    while run:
        # 4.2.1: رسم الشبكة في كل إطار (frame)
        draw_grid(WIN, grid, ROWS, WIDTH)

        # 4.2.2: معالجة أحداث المستخدم (ضغطات الفأرة ولوحة المفاتيح)
        for event in pygame.event.get():
            # إغلاق البرنامج
            if event.type == pygame.QUIT:
                run = False

            # التعامل مع ضغطات الفأرة
            if pygame.mouse.get_pressed()[0]: # الزر الأيسر
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                
                if not start_pos:
                    start_pos = (row, col)
                    grid[row][col] = STATE_START
                elif not end_pos and (row, col) != start_pos:
                    end_pos = (row, col)
                    grid[row][col] = STATE_END
                elif (row, col) != start_pos and (row, col) != end_pos:
                    grid[row][col] = STATE_WALL
            
            elif pygame.mouse.get_pressed()[2]: # الزر الأيمن (للمسح)
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                if (row, col) == start_pos:
                    start_pos = None
                elif (row, col) == end_pos:
                    end_pos = None
                grid[row][col] = STATE_EMPTY

            # التعامل مع ضغطات لوحة المفاتيح
            if event.type == pygame.KEYDOWN:
                # تشغيل الخوارزميات فقط إذا تم تحديد البداية والنهاية
                if start_pos and end_pos:
                    # قبل التشغيل، نظف الشبكة من محاولات البحث السابقة
                    for r in range(ROWS):
                        for c in range(ROWS):
                            state = grid[r][c]
                            if state in [STATE_OPEN, STATE_CLOSED, STATE_PATH]:
                                grid[r][c] = STATE_EMPTY
                    
                    if event.key == pygame.K_a: # حرف A لتشغيل A*
                        a_star(grid, start_pos, end_pos, lambda: draw_grid(WIN, grid, ROWS, WIDTH))
                    if event.key == pygame.K_b: # حرف B لتشغيل BFS
                        bfs(grid, start_pos, end_pos, lambda: draw_grid(WIN, grid, ROWS, WIDTH))
                    if event.key == pygame.K_d: # حرف D لتشغيل DFS
                        dfs(grid, start_pos, end_pos, lambda: draw_grid(WIN, grid, ROWS, WIDTH))

                if event.key == pygame.K_c: # حرف C لمسح الكل (Clear)
                    grid = [[STATE_EMPTY for _ in range(ROWS)] for _ in range(ROWS)]
                    start_pos = None
                    end_pos = None
    
    # --- الخطوة 4.3: إغلاق Pygame بأمان ---
    pygame.quit()



# =================================================================
# المرحلة 5: نقطة انطلاق البرنامج
# =================================================================

if __name__ == "__main__":
    main()