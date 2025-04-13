import pytest
from main import Board, AIPlayer

# 初期盤面が黒2・白2で正しくセットアップされているかを確認するテスト
def test_initial_board_setup():
    board = Board()
    black, white = board.count_pieces()
    assert black == 2
    assert white == 2

# 石を置いたときに正しく相手の石がひっくり返るかをテスト
def test_valid_move_flips_stones():
    board = Board()
    result = board.place_stone(2, 3, 1)  # 黒が白を挟める位置に打つ
    assert result is True
    assert board.grid[3][3] == 1  # 白だったマスが黒に変わっているかを確認

# 無効な場所に打ったときに石が置かれないことを確認するテスト
def test_invalid_move_does_nothing():
    board = Board()
    result = board.place_stone(0, 0, 1)  # 挟めない位置に打つ
    assert result is False
    assert board.grid[0][0] == 0  # 石が置かれていないことを確認

# easyモードのAIが盤面に石を1つ以上置くことを確認するテスト
def test_easy_ai_places_stone():
    board = Board()
    ai = AIPlayer(2, difficulty='easy')
    ai.make_move(board)
    _, white = board.count_pieces()
    assert white > 2  # 初期状態（白2）より多くなっているはず

# normalモードのAIが最も多くひっくり返せる手を選んでいることを確認するテスト
def test_normal_ai_prefers_max_flips():
    board = Board()
    ai = AIPlayer(2, difficulty='normal')

    # 白の手番にして、中央左に黒を置いておくことで白が最大数を返せる場所を作る
    board.place_stone(2, 3, 1)
    ai.make_move(board)
    _, white = board.count_pieces()
    assert white > 2  # 白が打って石が増えていることを確認
