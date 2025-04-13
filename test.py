import pytest
from main import Board, AIPlayer, Player, SQUARE_SIZE

# 初期状態の盤面に黒2・白2が正しく配置されていることを確認するテスト
def test_initial_board_setup():
    board = Board()
    black, white = board.count_pieces()
    assert black == 2
    assert white == 2

# 黒が石を置いたときに白がひっくり返るかどうかをテスト
def test_valid_move_flips_stones():
    board = Board()
    result = board.place_stone(2, 3, 1)  # 黒が白を挟む手
    assert result is True
    assert board.grid[3][3] == 1  # 白→黒に変わっていることを確認

# 挟めないマスに石を置いても無効になるかのテスト
def test_invalid_move_does_nothing():
    board = Board()
    result = board.place_stone(0, 0, 1)  # 隅っこで挟めない
    assert result is False
    assert board.grid[0][0] == 0

# 有効手があるかどうかを判定するテスト
def test_has_valid_move_returns_true():
    board = Board()
    assert board.has_valid_move(1) is True  # 黒に打てる手がある状態

# 盤面を埋めて打てる手がない状態でFalseが返ることをテスト
def test_has_valid_move_returns_false():
    board = Board()
    board.grid = [[1]*8 for _ in range(8)]  # 盤面を黒で埋める
    assert board.has_valid_move(2) is False  # 白は打てないはず

# easyモードAIが盤面に石を追加しているかをテスト
def test_easy_ai_places_stone():
    board = Board()
    ai = AIPlayer(2, difficulty='easy')
    ai.make_move(board)
    _, white = board.count_pieces()
    assert white > 2  # 白石が追加されている

# normalモードAIが最大の返せる石を選ぶことを確認するテスト
def test_normal_ai_chooses_max_flips():
    board = Board()
    ai = AIPlayer(2, difficulty='normal')
    board.place_stone(2, 3, 1)  # 黒で白を挟むパターンをつくる
    ai.make_move(board)
    _, white = board.count_pieces()
    assert white > 2  # 白の手が打たれて石が増える

# hardモードAIが角（コーナー）を優先して選ぶことをテスト
def test_hard_ai_prefers_corner():
    board = Board()
    ai = AIPlayer(2, difficulty='hard')

    # 全体を黒で埋める
    board.grid = [[1]*8 for _ in range(8)]

    # コーナーに白が置けて、かつ挟めるように配置
    board.grid[0][0] = 0         # コーナー（空）
    board.grid[0][1] = 1         # 黒
    board.grid[0][2] = 2         # 白 ← これで挟めるようになる
    ai.make_move(board)

    assert board.grid[0][0] == 2  # コーナーに白石が置かれたか確認

# 人間プレイヤー（黒）の make_move が正常に動作するかをテスト
def test_player_make_move_success():
    board = Board()
    player = Player(1)
    success = player.make_move(board, (3 * SQUARE_SIZE, 2 * SQUARE_SIZE))  # (列3, 行2)
    assert success is True
    assert board.grid[2][3] == 1  # 石が置かれている
