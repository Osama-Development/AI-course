# =================================================================
# المرحلة 0: استيراد المكتبات وتجهيز البيئة
# =================================================================

# --- الخطوة 0.1: استيراد المكتبات المطلوبة ---
import math  # للتعامل مع قيم لا نهائية (infinity) في خوارزمية Minimax
import time  # لإضافة تأخير بسيط بين الحركات لجعل اللعبة أكثر واقعية
import os    # لتشغيل أوامر النظام، هنا لتفعيل رموز الألوان في ويندوز

# --- الخطوة 0.2: تفعيل رموز الألوان (ANSI) ---
# هذا السطر ضروري لضمان عمل رموز تلوين النص على طرفية ويندوز
os.system('')



# =================================================================
# المرحلة 1: تعريف الثوابت والمتغيرات العامة
# =================================================================
# الهدف: مركزة كل القيم الثابتة في مكان واحد لسهولة التعديل عليها مستقبلاً.

# --- الخطوة 1.1: تعريف رموز الألوان ---
# نستخدم رموز ANSI للتحكم في ألوان النص في الطرفية.
COLOR_RED = '\033[91m'     # لون اللاعب 'X' (الكمبيوتر)
COLOR_BLUE = '\033[94m'    # لون اللاعب 'O' (الإنسان)
COLOR_WHITE = '\033[97m'   # لون أرقام الخانات المتاحة
COLOR_RESET = '\033[0m'    # رمز لإعادة تعيين اللون إلى الوضع الافتراضي

# --- الخطوة 1.2: تعريف رموز اللاعبين ---
# استخدام متغيرات لأسماء اللاعبين يجعل الكود أكثر قابلية للقراءة.
AI_PLAYER = 'X'
HUMAN_PLAYER = 'O'



# =================================================================
# المرحلة 2: تعريف دوال إدارة اللوحة واللعبة
# =================================================================
# الهدف: إنشاء مجموعة من الدوال المسؤولة عن كل ما يتعلق بحالة اللوحة واللعبة.

# --- الخطوة 2.1: دالة لإنشاء لعبة جديدة ---
def create_game():
    """تنشئ قاموسًا جديدًا يمثل حالة اللعبة في بدايتها."""
    # القاموس يحتوي على:
    # 'board': قائمة من 9 عناصر تمثل اللوحة، تبدأ فارغة.
    # 'winner': لتخزين الفائز عند انتهاء اللعبة، تبدأ بـ None.
    return {
        'board': [' ' for _ in range(9)],
        'winner': None
    }

# --- الخطوة 2.2: دالة لطباعة اللوحة الحالية ---
def print_board(board):
    """تطبع اللوحة الحالية مع تلوين قطع اللاعبين."""
    for row_indices in [range(j*3, (j+1)*3) for j in range(3)]:
        colored_row = []
        for i in row_indices:
            spot = board[i]
            if spot == AI_PLAYER:
                colored_row.append(f"{COLOR_RED}{spot}{COLOR_RESET}")
            elif spot == HUMAN_PLAYER:
                colored_row.append(f"{COLOR_BLUE}{spot}{COLOR_RESET}")
            else:
                colored_row.append(spot)
        print('| ' + ' | '.join(colored_row) + ' |')

# --- الخطوة 2.3: دالة لطباعة الخانات المتاحة ---
def print_available_moves_board(board):
    """تطبع لوحة توضيحية تظهر فيها أرقام الخانات الفارغة المتاحة للعب."""
    colored_board = []
    for i, spot in enumerate(board):
        if spot == AI_PLAYER:
            colored_board.append(f"{COLOR_RED}{spot}{COLOR_RESET}")
        elif spot == HUMAN_PLAYER:
            colored_board.append(f"{COLOR_BLUE}{spot}{COLOR_RESET}")
        else:
            colored_board.append(f"{COLOR_WHITE}{str(i)}{COLOR_RESET}")
    
    print("الخانات المتاحة:")
    for row_indices in [range(j*3, (j+1)*3) for j in range(3)]:
        row_str = [colored_board[i] for i in row_indices]
        print('| ' + ' | '.join(row_str) + ' |')

# --- الخطوة 2.4: دالة للحصول على الحركات المتاحة ---
def available_moves(board):
    """ترجع قائمة بفهارس جميع الخانات الفارغة (' ') على اللوحة."""
    return [i for i, spot in enumerate(board) if spot == ' ']

# --- الخطوة 2.5: دالة للتحقق من الفائز ---
def check_winner(board, letter, square):
    """تتحقق مما إذا كان اللاعب 'letter' قد فاز بعد لعبه في الخانة 'square'."""
    # التحقق من الصف الذي تقع فيه الحركة
    row_ind = square // 3
    row = board[row_ind*3 : (row_ind+1)*3]
    if all([spot == letter for spot in row]):
        return True
        
    # التحقق من العمود الذي تقع فيه الحركة
    col_ind = square % 3
    column = [board[col_ind+i*3] for i in range(3)]
    if all([spot == letter for spot in column]):
        return True
        
    # التحقق من الأقطار (فقط إذا كانت الحركة في مربع قطري)
    if square % 2 == 0:
        if all([board[i] == letter for i in [0, 4, 8]]): # القطر الرئيسي
            return True
        if all([board[i] == letter for i in [2, 4, 6]]): # القطر الثانوي
            return True
            
    return False

# --- الخطوة 2.6: دالة لتنفيذ الحركة على اللوحة ---
def make_move(game_state, square, letter):
    """تنفذ الحركة على اللوحة وتحدث حالة الفائز إذا لزم الأمر."""
    if game_state['board'][square] == ' ':
        game_state['board'][square] = letter
        if check_winner(game_state['board'], letter, square):
            game_state['winner'] = letter
        return True
    return False



# =================================================================
# المرحلة 3: تعريف دوال اللاعبين (الإنسان والذكاء الاصطناعي)
# =================================================================
# الهدف: فصل منطق كل لاعب في دالة خاصة به.

# --- الخطوة 3.1: دالة لأخذ حركة من اللاعب البشري ---
def get_human_move(board):
    """تأخذ حركة من اللاعب البشري وتتحقق من صحتها."""
    valid_square = False
    val = None
    print_available_moves_board(board) # عرض الخيارات المتاحة قبل طلب الإدخال
    while not valid_square:
        prompt = f"{COLOR_BLUE}{HUMAN_PLAYER}{COLOR_RESET} - حان دورك. أدخل رقم الخانة التي تريدها: "
        square_input = input(prompt)
        try:
            val = int(square_input)
            if val not in available_moves(board): # التحقق من أن الخانة المختارة متاحة
                raise ValueError
            valid_square = True
        except (ValueError, IndexError): # التعامل مع الإدخالات الخاطئة (نص أو رقم خارج النطاق)
            print(f'{COLOR_RED}إدخال خاطئ. الرجاء اختيار رقم من الخانات المتاحة.{COLOR_RESET}')
    return val

# --- الخطوة 3.2: دالة لحساب حركة الذكاء الاصطناعي ---
def get_ai_move(board):
    """تحسب أفضل حركة للذكاء الاصطناعي باستخدام خوارزمية Minimax."""
    if board.count(' ') == 9:
        return 4  # كاستراتيجية بداية، العب في المنتصف دائمًا لأنه أفضل مربع
    else:
        # استدعاء الخوارزمية الذكية لإيجاد أفضل حركة
        best_move = minimax(board, AI_PLAYER)['position']
        return best_move



# =================================================================
# المرحلة 4: تطبيق خوارزمية البحث التنافسي (Minimax)
# =================================================================
# الهدف: بناء العقل المفكر للذكاء الاصطناعي.

def minimax(current_board, current_player):
    """خوارزمية Minimax التي تستكشف شجرة اللعبة لإيجاد الحركة المثلى."""
    
    # --- الخطوة 4.1: تحديد اللاعبين في هذه الجولة ---
    max_player = AI_PLAYER
    other_player = HUMAN_PLAYER if current_player == AI_PLAYER else AI_PLAYER

    # --- الخطوة 4.2: تحديد الحالات النهائية (Base Cases) التي توقف العودية ---
    # تحقق من الفائز في الحالة السابقة (قبل هذه الحركة)
    # يمكن تحسين هذا، لكنه يبسط المنطق الحالي
    
    # تحقق إذا انتهت اللعبة بالتعادل (لا توجد حركات متاحة)
    if not available_moves(current_board):
        return {'position': None, 'score': 0}

    # --- الخطوة 4.3: إعداد متغير لتخزين أفضل نتيجة ---
    if current_player == max_player:
        best = {'position': None, 'score': -math.inf} # نبدأ بسالب لانهاية لأننا نريد التعظيم
    else:
        best = {'position': None, 'score': math.inf}  # نبدأ بموجب لانهاية لأننا نريد التقليل

    # --- الخطوة 4.4: استكشاف كل الحركات الممكنة (الخطوة العودية) ---
    for possible_move in available_moves(current_board):
        # 4.4.1: قم بالحركة على نسخة جديدة من اللوحة (لتجنب تعديل اللوحة الأصلية)
        new_board = current_board[:]
        new_board[possible_move] = current_player

        # 4.4.2: تحقق من الفائز *بعد* الحركة الافتراضية. إذا فاز أحد، فهذه نهاية الفرع.
        if check_winner(new_board, current_player, possible_move):
            score = 1 * (new_board.count(' ') + 1) if current_player == max_player else -1 * (new_board.count(' ') + 1)
            return {'position': possible_move, 'score': score}
        
        # 4.4.3: إذا لم يفز أحد، استمر في البحث بالاستدعاء العودي للاعب الآخر
        sim_score = minimax(new_board, other_player)

        # 4.4.4: تحديث أفضل حركة تم العثور عليها
        if current_player == max_player:
            if sim_score['score'] > best['score']:
                best = {'position': possible_move, 'score': sim_score['score']}
        else: # دور اللاعب MIN
            if sim_score['score'] < best['score']:
                best = {'position': possible_move, 'score': sim_score['score']}

    # --- الخطوة 4.5: إرجاع أفضل حركة ونتيجتها لهذا الفرع ---
    return best



# =================================================================
# المرحلة 5: حلقة اللعب الرئيسية التي تربط كل شيء معًا
# =================================================================

def run_game():
    """الدالة الرئيسية التي تدير تدفق اللعبة من البداية إلى النهاية."""
    
    # --- الخطوة 5.1: إنشاء لعبة جديدة وتحديد اللاعب البادئ ---
    game = create_game()
    current_letter = AI_PLAYER # الكمبيوتر يبدأ دائمًا

    # --- الخطوة 5.2: بدء حلقة اللعب الرئيسية ---
    # تستمر الحلقة طالما أن اللوحة ليست ممتلئة ولم يفز أحد
    while ' ' in game['board'] and not game['winner']:
        
        # 5.2.1: تحديد اللاعب الذي سيلعب
        if current_letter == AI_PLAYER:
            square = get_ai_move(game['board'])
            print(f"الكمبيوتر ({COLOR_RED}{AI_PLAYER}{COLOR_RESET}) يختار الخانة رقم {square}")
        else:
            square = get_human_move(game['board'])
            print(f"أنت ({COLOR_BLUE}{HUMAN_PLAYER}{COLOR_RESET}) اخترت الخانة رقم {square}")

        # 5.2.2: تنفيذ الحركة وتحديث حالة اللعبة
        if make_move(game, square, current_letter):
            print_board(game['board'])
            print('') # طباعة سطر فارغ للفصل بين الأدوار

        # 5.2.3: تبديل اللاعب للدور التالي
        current_letter = HUMAN_PLAYER if current_letter == AI_PLAYER else AI_PLAYER
        
        # 5.2.4: إضافة تأخير بسيط لجعل اللعب يبدو طبيعيًا أكثر
        time.sleep(0.8)

    # --- الخطوة 5.3: طباعة النتيجة النهائية بعد انتهاء اللعبة ---
    if game['winner']:
        winner_color = COLOR_RED if game['winner'] == AI_PLAYER else COLOR_BLUE
        print(f"{winner_color}اللاعب {game['winner']} فاز!{COLOR_RESET}")
    else:
        print("انتهت اللعبة بالتعادل!")



# =================================================================
# المرحلة 6: نقطة انطلاق البرنامج
# =================================================================
# هذا هو المدخل الرئيسي للبرنامج.
# الكود داخل هذا الشرط لن يعمل إلا إذا تم تشغيل الملف مباشرة.

if __name__ == '__main__':
    run_game()