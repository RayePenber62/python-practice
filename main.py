from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

# ========================================
# ゲームの準備
# ========================================

app = Ursina()

# 日本語対応フォント
# Pythonファイルと同じフォルダに入れてください
Text.default_font = "NotoSansJP-VariableFont_wght.ttf"

# 毎回同じコースを生成する
# random.seed(10)

# 空
Sky()

# 背景色
window.color = color.rgb(120, 180, 255)


# ========================================
# スタート地点
# ========================================

start_position = Vec3(0, 0, 0)

start_platform = Entity(
    model="cube",
    position=start_position,
    scale=(6, 1, 6),
    color=color.azure,
    collider="box",
    texture="white_cube",
)


# ========================================
# ランダムな足場を20個作る
# ========================================

platforms = []
platform_count = 20

# 今回は10個目だけをチェックポイントにする
checkpoint_number = 10
checkpoint_platform = None

current_x = 0
current_y = 0
current_z = 0

# スタート足場の奥行き
previous_depth = 6


for i in range(platform_count):

    # 人間が数える足場番号
    platform_number = i + 1

    # 後半ほど難しくする
    difficulty = i / (platform_count - 1)

    # 後半ほど小さい足場が出やすくなる
    minimum_size = 3.2 - difficulty * 0.8

    platform_width = random.uniform(
        minimum_size,
        4.8,
    )

    platform_depth = random.uniform(
        minimum_size,
        4.8,
    )

    platform_height = random.uniform(
        0.4,
        1.0,
    )

    # 後半ほど左右への変化を大きくする
    maximum_x_distance = 2.0 + difficulty * 2.0

    x_distance = random.uniform(
        -maximum_x_distance,
        maximum_x_distance,
    )

    # ときどき左右へ大きく移動する
    if random.random() < 0.25:
        direction = random.choice([-1, 1])

        x_distance = random.uniform(3.0, 4.5) * direction

    # 基本的には上へ進む
    y_distance = random.uniform(
        0.45,
        1.0,
    )

    # ときどき大きく上昇する
    if random.random() < 0.2:
        y_distance = random.uniform(
            1.0,
            1.4,
        )

    # ときどき少し下がる
    if random.random() < 0.12:
        y_distance = random.uniform(
            -0.5,
            -0.2,
        )

    # 後半ほど前後の隙間を広くする
    minimum_gap = 1.2 + difficulty * 0.3

    maximum_gap = 2.0 + difficulty * 0.8

    # 現在の難易度設定
    edge_gap = (
        random.uniform(
            minimum_gap,
            maximum_gap,
        )
        * 1.9
    )

    # 足場が重ならないように中心間距離を計算
    z_distance = previous_depth / 2 + edge_gap + platform_depth / 2

    # 新しい足場の位置
    current_x += x_distance * 1.5
    current_y += y_distance
    current_z += z_distance

    # 足場の色
    platform_color = random.choice(
        [
            color.orange,
            color.yellow,
            color.azure,
            color.violet,
            color.pink,
            color.cyan,
        ]
    )

    # 10個目かどうか
    is_checkpoint = platform_number == checkpoint_number

    # 10個目は緑色で少し大きくする
    if is_checkpoint:
        platform_color = color.lime
        platform_width = max(platform_width, 5.0)
        platform_depth = max(platform_depth, 5.0)

    # 足場を生成
    platform = Entity(
        model="cube",
        position=(
            current_x,
            current_y,
            current_z,
        ),
        scale=(
            platform_width,
            platform_height,
            platform_depth,
        ),
        color=platform_color,
        collider="box",
        texture="white_cube",
    )

    # 足場に情報を保存する
    platform.platform_number = platform_number
    platform.is_checkpoint = is_checkpoint

    platforms.append(platform)

    # 10個目の足場を覚えておく
    if is_checkpoint:
        checkpoint_platform = platform

    previous_depth = platform_depth


# ========================================
# 最後の足場をゴールにする
# ========================================

goal_platform = platforms[-1]
goal_platform.color = color.red

goal_guide_text = Text(
    text="赤い足場がゴール！",
    origin=(0, 0),
    position=(0, 0.44),
    scale=1.4,
    color=color.red,
    background=True,
)


# ========================================
# プレイヤー
# ========================================

player = FirstPersonController()

player.position = (0, 2, 0)

normal_speed = 5
sprint_speed = 10

player.speed = normal_speed
player.jump_height = 2.2
player.gravity = 1


# ========================================
# ゲームの状態
# ========================================

paused = False
goal_reached = False
game_started = False
countdown_running = False
falling = False

elapsed_time = 0.0
fall_count = 0

# チェックポイントを通過したか
checkpoint_activated = False

# 最初の復活地点
respawn_position = Vec3(0, 2, 0)


# ========================================
# プレイ中の画面表示
# ========================================

fall_count_text = Text(
    text="落下回数：0",
    position=(-0.72, 0.45),
    scale=1.3,
    background=True,
)

timer_text = Text(
    text="TIME：0.00秒",
    position=(-0.72, 0.39),
    scale=1.3,
    background=True,
)

checkpoint_status_text = Text(
    text="チェックポイント：未通過",
    position=(-0.72, 0.33),
    scale=1.1,
    background=True,
)


# ========================================
# スタート画面
# ========================================

start_overlay = Entity(
    parent=camera.ui,
    model="quad",
    scale=(2, 2),
    color=color.rgba(0, 0, 0, 190),
    z=1,
    enabled=True,
)

start_panel = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.75, 0.72),
    color=color.rgb(35, 35, 45),
    z=0,
    enabled=True,
)

start_title = Text(
    parent=start_panel,
    text="SKY PARKOUR",
    origin=(0, 0),
    position=(0, 0.38),
    scale=2.5,
    color=color.azure,
)

controls_text = Text(
    parent=start_panel,
    text=(
        "WASD：移動\n"
        "SPACE：ジャンプ\n"
        "SHIFT：ダッシュ\n"
        "ESC：ポーズ\n\n"
        "10個目の緑の足場：チェックポイント\n"
        "最後の赤い足場：ゴール"
    ),
    origin=(0, 0),
    position=(0, 0.05),
    scale=1.05,
    line_height=1.3,
)

start_button = Button(
    parent=start_panel,
    text="ゲーム開始",
    scale=(0.65, 0.15),
    position=(0, -0.36),
    color=color.azure,
)


# ========================================
# カウントダウン表示
# ========================================

countdown_text = Text(
    text="3",
    origin=(0, 0),
    position=(0, 0),
    scale=6,
    color=color.white,
    background=True,
    enabled=False,
)

# ========================================
# チェックポイント通知
# ========================================

checkpoint_message = Text(
    text="CHECKPOINT!",
    origin=(0, 0),
    position=(0, 0.25),
    scale=2.5,
    color=color.lime,
    background=True,
    enabled=False,
)


# ========================================
# ポーズ画面
# ========================================

pause_overlay = Entity(
    parent=camera.ui,
    model="quad",
    scale=(2, 2),
    color=color.rgba(0, 0, 0, 180),
    z=1,
    enabled=False,
)

pause_panel = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.55, 0.4),
    color=color.rgb(35, 35, 45),
    z=0,
    enabled=False,
)

pause_title = Text(
    parent=pause_panel,
    text="PAUSED",
    origin=(0, 0),
    position=(0, 0.32),
    scale=2,
)

resume_button = Button(
    parent=pause_panel,
    text="ゲームに戻る",
    scale=(0.7, 0.2),
    position=(0, 0.05),
    color=color.azure,
)

quit_button = Button(
    parent=pause_panel,
    text="ゲームを終了",
    scale=(0.7, 0.2),
    position=(0, -0.2),
    color=color.red,
)


# ========================================
# ゴール画面
# ========================================

goal_overlay = Entity(
    parent=camera.ui,
    model="quad",
    scale=(2, 2),
    color=color.rgba(0, 0, 0, 190),
    z=1,
    enabled=False,
)

goal_panel = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.65, 0.55),
    color=color.rgb(35, 35, 45),
    z=0,
    enabled=False,
)

goal_title = Text(
    parent=goal_panel,
    text="GOAL!",
    origin=(0, 0),
    position=(0, 0.34),
    scale=3,
    color=color.yellow,
)

clear_time_text = Text(
    parent=goal_panel,
    text="クリアタイム：0.00秒",
    origin=(0, 0),
    position=(0, 0.12),
    scale=1.5,
)

result_fall_text = Text(
    parent=goal_panel,
    text="落下回数：0回",
    origin=(0, 0),
    position=(0, -0.02),
    scale=1.3,
)

retry_button = Button(
    parent=goal_panel,
    text="もう一度遊ぶ",
    scale=(0.7, 0.16),
    position=(0, -0.22),
    color=color.azure,
)

goal_quit_button = Button(
    parent=goal_panel,
    text="ゲームを終了",
    scale=(0.7, 0.16),
    position=(0, -0.41),
    color=color.red,
)


# ========================================
# カウントダウン表示を変更する
# ========================================


def set_countdown_text(message):
    countdown_text.text = message
    countdown_text.enabled = True


# ========================================
# カウントダウン終了
# ========================================


def finish_countdown():
    global game_started
    global countdown_running

    game_started = True
    countdown_running = False

    countdown_text.enabled = False

    player.enabled = True

    mouse.locked = True
    mouse.visible = False


# ========================================
# カウントダウン開始
# ========================================


def begin_countdown():
    global countdown_running

    if countdown_running:
        return

    countdown_running = True

    # スタート画面を閉じる
    start_overlay.enabled = False
    start_panel.enabled = False

    # カウントダウン中は操作停止
    player.enabled = False

    mouse.locked = True
    mouse.visible = False

    countdown_sequence = Sequence(
        Func(set_countdown_text, "3"),
        Wait(1),
        Func(set_countdown_text, "2"),
        Wait(1),
        Func(set_countdown_text, "1"),
        Wait(1),
        Func(set_countdown_text, "START!"),
        Wait(0.7),
        Func(finish_countdown),
    )

    countdown_sequence.start()


# ========================================
# チェックポイント通知を消す
# ========================================


def hide_checkpoint_message():
    checkpoint_message.enabled = False


# ========================================
# チェックポイントを有効にする
# ========================================


def activate_checkpoint():
    global checkpoint_activated
    global respawn_position

    if checkpoint_activated:
        return

    checkpoint_activated = True

    # チェックポイントの上面
    checkpoint_top = checkpoint_platform.y + checkpoint_platform.scale_y / 2

    # 落下後の復活地点を設定
    respawn_position = Vec3(
        checkpoint_platform.x,
        checkpoint_top + 1.5,
        checkpoint_platform.z,
    )

    checkpoint_status_text.text = "チェックポイント：通過済み"

    checkpoint_message.text = "CHECKPOINT 10!"
    checkpoint_message.enabled = True

    invoke(
        hide_checkpoint_message,
        delay=1.5,
    )


# ========================================
# チェックポイント判定
# ========================================


def check_checkpoint():

    if checkpoint_activated:
        return

    checkpoint_top = checkpoint_platform.y + checkpoint_platform.scale_y / 2

    inside_x = abs(player.x - checkpoint_platform.x) <= checkpoint_platform.scale_x / 2

    inside_z = abs(player.z - checkpoint_platform.z) <= checkpoint_platform.scale_z / 2

    on_checkpoint_height = checkpoint_top <= player.y <= checkpoint_top + 2.5

    if inside_x and inside_z and on_checkpoint_height:
        activate_checkpoint()


# ========================================
# 落下後に復活する
# ========================================


def finish_fall():
    global falling

    # スタートまたはチェックポイントに戻す
    player.position = respawn_position
    player.air_time = 0
    player.enabled = True

    mouse.locked = True
    mouse.visible = False

    falling = False


# ========================================
# 落下演出を始める
# ========================================


def start_fall():
    global fall_count
    global falling

    if falling:
        return

    falling = True

    fall_count += 1

    fall_count_text.text = f"落下回数：{fall_count}"

    # プレイヤー操作を止める
    player.enabled = False

    # 0.8秒後に復活
    invoke(
        finish_fall,
        delay=0.8,
    )


# ========================================
# ゴールしたとき
# ========================================


def reach_goal():
    global goal_reached

    if goal_reached:
        return

    goal_reached = True

    clear_time_text.text = f"クリアタイム：{elapsed_time:.2f}秒"

    result_fall_text.text = f"落下回数：{fall_count}回"

    goal_overlay.enabled = True
    goal_panel.enabled = True

    player.enabled = False

    mouse.locked = False
    mouse.visible = True


# ========================================
# もう一度遊ぶ
# ========================================


def retry_game():
    global elapsed_time
    global fall_count
    global goal_reached
    global paused
    global game_started
    global countdown_running
    global falling
    global checkpoint_activated
    global respawn_position

    # ゲーム状態を初期化
    elapsed_time = 0.0
    fall_count = 0
    goal_reached = False
    paused = False
    game_started = False
    countdown_running = False
    falling = False
    checkpoint_activated = False

    # 復活地点をスタートへ戻す
    respawn_position = Vec3(0, 2, 0)

    # 画面表示を初期化
    timer_text.text = "TIME：0.00秒"
    fall_count_text.text = "落下回数：0"

    checkpoint_status_text.text = "チェックポイント：未通過"

    checkpoint_message.enabled = False
    countdown_text.enabled = False

    # ゴール画面を閉じる
    goal_overlay.enabled = False
    goal_panel.enabled = False

    # ポーズ画面を閉じる
    pause_overlay.enabled = False
    pause_panel.enabled = False

    # スタート画面を表示
    start_overlay.enabled = True
    start_panel.enabled = True

    # プレイヤーをスタートへ戻す
    player.position = (0, 2, 0)
    player.air_time = 0
    player.speed = normal_speed
    player.enabled = False

    mouse.locked = False
    mouse.visible = True


# ========================================
# ポーズ画面を開く
# ========================================


def open_pause():
    global paused

    paused = True

    pause_overlay.enabled = True
    pause_panel.enabled = True

    player.enabled = False

    mouse.locked = False
    mouse.visible = True


# ========================================
# ポーズ画面を閉じる
# ========================================


def close_pause():
    global paused

    paused = False

    pause_overlay.enabled = False
    pause_panel.enabled = False

    player.enabled = True
    player.speed = normal_speed

    mouse.locked = True
    mouse.visible = False


# ========================================
# ゴール判定
# ========================================


def check_goal():

    goal_top = goal_platform.y + goal_platform.scale_y / 2

    inside_goal_x = abs(player.x - goal_platform.x) <= goal_platform.scale_x / 2

    inside_goal_z = abs(player.z - goal_platform.z) <= goal_platform.scale_z / 2

    on_goal_height = goal_top <= player.y <= goal_top + 2.5

    if inside_goal_x and inside_goal_z and on_goal_height:
        reach_goal()


# ========================================
# 毎フレーム行う処理
# ========================================


def update():
    global elapsed_time

    # スタート前は処理しない
    if not game_started:
        return

    # ポーズ中、ゴール後、落下演出中は停止
    if paused or goal_reached or falling:
        return

    # タイマーを進める
    elapsed_time += time.dt

    timer_text.text = f"TIME：{elapsed_time:.2f}秒"

    # Shiftキーでダッシュ
    if held_keys["shift"]:
        player.speed = sprint_speed
    else:
        player.speed = normal_speed

    # 奈落への落下判定
    if player.y < -15:
        start_fall()
        return

    # 10個目のチェックポイント判定
    check_checkpoint()

    # ゴール判定
    check_goal()


# ========================================
# キー入力
# ========================================


def input(key):

    # 開始前、ゴール後、落下演出中は無効
    if not game_started:
        return

    if goal_reached or falling:
        return

    # Escキーでポーズ
    if key == "escape":

        if paused:
            close_pause()
        else:
            open_pause()


# ========================================
# ボタンの設定
# ========================================

start_button.on_click = begin_countdown

resume_button.on_click = close_pause
quit_button.on_click = application.quit

retry_button.on_click = retry_game
goal_quit_button.on_click = application.quit


# ========================================
# 起動時の設定
# ========================================

# スタート画面ではプレイヤーを止める
player.enabled = False

mouse.locked = False
mouse.visible = True


# ========================================
# ゲーム開始
# ========================================

app.run()
