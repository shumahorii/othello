# pygameライブラリを使って、ウィンドウや描画を行う
import pygame
# プログラムの終了処理などに必要
import sys
# AIのeasyモードでランダムな手を打つときに使う
import random

# 画面サイズの設定（正方形のオセロ盤）
WIDTH, HEIGHT = 640, 640

# オセロは 8×8 のマスを使う
ROWS, COLS = 8, 8

# 各マスの1辺の長さ（正方形なので縦横同じ）
SQUARE_SIZE = WIDTH // COLS

# 色をRGB（赤・緑・青）で定義
GREEN = (0, 128, 0)     # 盤面の背景色（緑）
WHITE = (255, 255, 255) # 白石の色
BLACK = (0, 0, 0)       # 黒石や線の色
GRAY = (180, 180, 180)  # 勝敗テキストなどに使用
BLUE = (0, 0, 255)      # ボタン背景色（青）

# オセロで石をひっくり返す方向（上下左右と斜め）
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]

#----------------------------------------------------
# ボタンクラス：難易度選択画面で使用するボタン
#----------------------------------------------------
class Button:
    def __init__(self, text, x, y, width, height, callback):
        # ボタンに表示する文字列
        self.text = text
        # ボタンの位置とサイズ（四角形）
        self.rect = pygame.Rect(x, y, width, height)
        # ボタンがクリックされたときに呼ばれる関数
        self.callback = callback
        # フォントの初期化（サイズ36）
        self.font = pygame.font.SysFont(None, 36)

    # ボタンを画面に描画する
    def draw(self, screen):
        # ボタンの背景を青色で塗る
        pygame.draw.rect(screen, BLUE, self.rect)
        # ボタンの枠線を黒で描画
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        # ボタン内のテキストを白で描画
        text_surf = self.font.render(self.text, True, WHITE)
        # テキストをボタンの中央に配置
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    # ボタンがクリックされたかどうかを判定し、押されたらcallbackを呼ぶ
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

#----------------------------------------------------
# オセロの盤面を管理するクラス
#----------------------------------------------------
class Board:
    def __init__(self):
        # 8×8の盤面をすべて0（空）で初期化
        self.grid = [[0] * COLS for _ in range(ROWS)]

        # 初期配置（中央に黒と白を2個ずつ置く）
        self.grid[3][3] = self.grid[4][4] = 2  # 白石
        self.grid[3][4] = self.grid[4][3] = 1  # 黒石

    # 指定されたマス（row, col）が盤面内かどうかを判定
    def is_on_board(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS

    # 指定した位置に石を置いたとき、どの石がひっくり返せるかを返す
    def get_flippable_stones(self, row, col, turn):
        # すでに石がある場合は何も返さない
        if self.grid[row][col] != 0:
            return []

        flippable = []  # ひっくり返す候補の石の位置リスト

        # 8方向すべてをチェック
        for dx, dy in DIRECTIONS:
            r, c = row + dy, col + dx
            path = []  # この方向で挟めるかどうかの一時保存

            # 相手の石が続く限り進む
            while self.is_on_board(r, c) and self.grid[r][c] == 3 - turn:
                path.append((r, c))
                r += dy
                c += dx

            # 最後に自分の石があり、間に相手の石がある場合は挟める
            if self.is_on_board(r, c) and self.grid[r][c] == turn and path:
                flippable.extend(path)

        return flippable

    # 現在のプレイヤーが打てる手があるかをチェック
    def has_valid_move(self, turn):
        for row in range(ROWS):
            for col in range(COLS):
                if self.get_flippable_stones(row, col, turn):
                    return True
        return False

    # 石を置く処理（成功すればTrueを返す）
    def place_stone(self, row, col, turn):
        # 挟める石を取得
        to_flip = self.get_flippable_stones(row, col, turn)
        if not to_flip:
            return False  # 挟めない＝置けない

        # 挟んだ石を自分の色に変える
        for r, c in to_flip:
            self.grid[r][c] = turn

        # 最後に石を置く
        self.grid[row][col] = turn
        return True

    # 盤面を画面に描画する
    def draw(self, screen):
        # 背景を緑で塗りつぶす
        screen.fill(GREEN)
        for row in range(ROWS):
            for col in range(COLS):
                # マスを表す四角を作る
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                # 黒枠でマスを描画
                pygame.draw.rect(screen, BLACK, rect, 1)

                # 石が置かれているかどうか
                piece = self.grid[row][col]
                if piece != 0:
                    # 黒または白を設定
                    color = BLACK if piece == 1 else WHITE
                    # 中心に石（円）を描画
                    pygame.draw.circle(screen, color, rect.center, SQUARE_SIZE // 2 - 5)

    # 石の数をカウントして返す（黒, 白）
    def count_pieces(self):
        black = sum(row.count(1) for row in self.grid)
        white = sum(row.count(2) for row in self.grid)
        return black, white

#----------------------------------------------------
# プレイヤークラス（人間、黒）
#----------------------------------------------------
class Player:
    def __init__(self, turn):
        self.turn = turn  # プレイヤーの色（1=黒）

    # マウスクリック位置から石を置く
    def make_move(self, board, pos):
        x, y = pos  # マウスの座標（ピクセル）
        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return board.place_stone(row, col, self.turn)

#----------------------------------------------------
# コンピュータ（白）のAIクラス
#----------------------------------------------------
class AIPlayer:
    def __init__(self, turn, difficulty='normal'):
        self.turn = turn  # プレイヤーの色（2=白）
        self.difficulty = difficulty  # 難易度モードを保存

    # AIが石を置く処理（難易度に応じた戦略）
    def make_move(self, board):
        moves = []  # [(行, 列, [ひっくり返す石リスト])]
        for row in range(ROWS):
            for col in range(COLS):
                flips = board.get_flippable_stones(row, col, self.turn)
                if flips:
                    moves.append((row, col, flips))

        if not moves:
            return  # 打てる手がない場合は何もしない

        if self.difficulty == 'easy':
            # ランダムな手を選ぶ
            row, col, _ = random.choice(moves)

        elif self.difficulty == 'normal':
            # 一番多くひっくり返せる手を選ぶ
            row, col, _ = max(moves, key=lambda m: len(m[2]))

        elif self.difficulty == 'hard':
            # 角を優先的に選ぶ（それがなければnormal戦略）
            corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
            for r, c, flips in moves:
                if (r, c) in corners:
                    board.place_stone(r, c, self.turn)
                    return
            row, col, _ = max(moves, key=lambda m: len(m[2]))

        # 選んだ手で石を置く
        board.place_stone(row, col, self.turn)

#----------------------------------------------------
# 難易度選択メニューのクラス
#----------------------------------------------------
class DifficultySelector:
    def __init__(self, screen, start_callback):
        self.screen = screen
        self.buttons = []  # ボタンのリスト
        self.font = pygame.font.SysFont(None, 48)
        self.start_callback = start_callback  # 難易度選択後にゲーム開始する関数
        self.create_buttons()

    # 難易度選択ボタンを生成
    def create_buttons(self):
        levels = ['easy', 'normal', 'hard']
        for i, level in enumerate(levels):
            btn = Button(
                text=level.capitalize(),  # 表示は先頭大文字
                x=WIDTH // 2 - 100,
                y=180 + i * 100,
                width=200,
                height=60,
                callback=lambda l=level: self.start_callback(l)  # 難易度を渡してゲーム開始
            )
            self.buttons.append(btn)

    # 選択画面を表示して処理を待つ
    def run(self):
        while True:
            self.screen.fill(GREEN)

            # タイトル文字を表示
            title = self.font.render("Select AI Difficulty", True, BLACK)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for btn in self.buttons:
                    btn.handle_event(event)

            # ボタン描画
            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()

#----------------------------------------------------
# ゲーム本体の管理クラス
#----------------------------------------------------
class Game:
    def __init__(self, difficulty='normal'):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Othello")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 40)

        self.board = Board()
        self.player = Player(1)           # 人間プレイヤー（黒）
        self.ai = AIPlayer(2, difficulty) # AIプレイヤー（白）
        self.current_turn = 1             # 黒からスタート
        self.game_over = False            # ゲーム終了フラグ

    # 次のターンに進む（AIの番ならタイマー起動）
    def next_turn(self):
        opponent = 3 - self.current_turn
        if self.board.has_valid_move(opponent):
            self.current_turn = opponent
            if self.current_turn == 2:
                # 0.5秒後にAIを自動実行するタイマー設定
                pygame.time.set_timer(pygame.USEREVENT, 500)
        elif self.board.has_valid_move(self.current_turn):
            pass  # 相手は打てないが自分は続行
        else:
            self.game_over = True  # 両者とも打てなければ終了

    # 勝敗と石数を表示
    def draw_result(self):
        black, white = self.board.count_pieces()
        if black > white:
            text = f"Black Wins! ({black} vs {white})"
        elif white > black:
            text = f"White Wins! ({white} vs {black})"
        else:
            text = f"Draw! ({black} vs {white})"

        img = self.font.render(text, True, GRAY)
        self.screen.blit(img, (WIDTH // 2 - img.get_width() // 2, HEIGHT // 2 - img.get_height() // 2))

    # ゲームのメインループ（プレイヤー操作・AI処理・描画）
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.game_over:
                    continue

                # 人間プレイヤーの操作（マウスクリックで石を置く）
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_turn == 1:
                    if self.player.make_move(self.board, pygame.mouse.get_pos()):
                        self.next_turn()

                # タイマー発火でAIが動く
                if event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)  # タイマーをリセット
                    self.ai.make_move(self.board)
                    self.next_turn()

            self.board.draw(self.screen)

            if self.game_over:
                self.draw_result()

            pygame.display.flip()
            self.clock.tick(60)

#----------------------------------------------------
# プログラムの開始点（まず難易度選択から始まる）
#----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # 難易度が選ばれたらゲーム開始
    selector = DifficultySelector(screen, start_callback=lambda difficulty: Game(difficulty).run())
    selector.run()

# Pythonスクリプトとして直接実行されたときにmainを呼ぶ
if __name__ == "__main__":
    main()
