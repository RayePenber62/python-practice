from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# 地面
ground = Entity(
    model="plane",
    scale=(100, 1, 100),
    texture="white_cube",
    texture_scale=(100, 100),
    collider="box",
    color=color.green,
)

# 空
Sky()

# パルクールの足場
platform1 = Entity(
    model="cube", position=(0, 1, 5), scale=(4, 1, 4), color=color.azure, collider="box"
)

platform2 = Entity(
    model="cube",
    position=(0, 2, 10),
    scale=(3, 1, 3),
    color=color.orange,
    collider="box",
)

platform3 = Entity(
    model="cube",
    position=(3, 3, 15),
    scale=(3, 1, 3),
    color=color.yellow,
    collider="box",
)


# プレイヤー
player = FirstPersonController()
player.position = (0, 2, 0)

# 移動速度
normal_speed = 5
sprint_speed = 10

player.speed = normal_speed


# ポーズメニューの状態
paused = False

# Shiftキーでダッシュ
def update():
    if paused:
        player.speed = 0
        return

    if held_keys["shift"]:
        player.speed = sprint_speed
    else:
        player.speed = normal_speed


# ポーズメニューの状態
paused = False

# 背景を暗くするオーバーレイ
pause_overlay = Entity(
    parent=camera.ui,
    model="quad",
    scale=(2, 2),
    color=color.rgba(0, 0, 0, 180),
    z=1,
    enabled=False,
)

# メニューのパネル
pause_panel = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.55, 0.4),
    color=color.rgb(35, 35, 45),
    z=0,
    enabled=False,
)

# タイトル
pause_title = Text(
    parent=pause_panel,
    text="PAUSED",
    origin=(0, 0),
    position=(0, 0.32),
    scale=2,
    enabled=False,
)

# ゲームに戻るボタン
resume_button = Button(
    parent=pause_panel,
    text="ゲームに戻る",
    scale=(0.7, 0.2),
    position=(0, 0.05),
    color=color.azure,
    enabled=False,
)

# ゲーム終了ボタン
quit_button = Button(
    parent=pause_panel,
    text="ゲームを終了",
    scale=(0.7, 0.2),
    position=(0, -0.2),
    color=color.red,
    enabled=False,
)


def open_pause():
    global paused
    paused = True

    pause_overlay.enabled = True
    pause_panel.enabled = True
    pause_title.enabled = True
    resume_button.enabled = True
    quit_button.enabled = True

    player.speed = 0
    mouse.locked = False


def close_pause():
    global paused
    paused = False

    pause_overlay.enabled = False
    pause_panel.enabled = False
    pause_title.enabled = False
    resume_button.enabled = False
    quit_button.enabled = False

    player.speed = normal_speed
    mouse.locked = True


def input(key):
    if key == "escape":
        if paused:
            close_pause()
        else:
            open_pause()


resume_button.on_click = close_pause
quit_button.on_click = application.quit


app.run()
#This is Version 3