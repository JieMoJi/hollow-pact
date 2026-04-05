import cv2
import time
from game_engine import GameEngine
from gesture_module import GestureRecognizer
import os

print("当前工作目录:", os.getcwd())
print("查找模型文件...")
for root, dirs, files in os.walk(r'D:\Code_Python'):
    if 'hand_landmarker.task' in files:
        print(f"找到: {os.path.join(root, 'hand_landmarker.task')}")
        break

# 模式选择
USE_CAMERA = True   # False = 键盘模拟，True = 真实摄像头

def render_debug(frame, state, gesture, debug_info=None):
    """临时渲染，供你测试用（增加 debug 信息显示）"""
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # 能量条（底部）
    bar_width = int(w * 0.6)
    bar_height = 30
    bar_x = (w - bar_width) // 2
    bar_y = h - 60
    fill_width = int(bar_width * state["energy"] / 100)

    # 背景
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                  (50, 50, 50), -1)
    # 填充色（绿→黄→红）
    if state["energy"] < 50:
        color = (0, 255, 0)
    elif state["energy"] < 80:
        color = (0, 255, 255)
    else:
        color = (0, 0, 255)
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height),
                  color, -1)
    # 边框
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                  (255, 255, 255), 2)

    # 文字
    cv2.putText(overlay, f"Energy: {state['energy']}", (bar_x, bar_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(overlay, f"Combo: x{state['combo']}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(overlay, f"Score: {state['score']}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(overlay, f"Gesture: {gesture.upper()}", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 显示 debug 信息（dist, ext）
    if debug_info:
        cv2.putText(overlay, f"dist={debug_info.get('dist',0):.2f} ext={debug_info.get('ext',0):.2f}",
                    (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # 发波特效
    if state["blast_trigger"]:
        cv2.circle(overlay, (w // 2, h // 2), 100, (0, 0, 255), 10)
        cv2.putText(overlay, "BLAST!", (w // 2 - 80, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

    # 混合
    return cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)


def main():
    engine = GameEngine()
    recognizer = None

    if USE_CAMERA:
        print("启动摄像头模式...")
        recognizer = GestureRecognizer()
    else:
        print("键盘模拟模式：")
        print(" [C] = charge (聚气), [B] = blast (发波), [其他] = none")
        print(" 按住 C 3秒聚满，然后按 B 发波")

    cap = cv2.VideoCapture(0)   # 用于获取画面尺寸
    last_time = time.time()

    while True:
        gesture = "none"
        frame = None
        debug_info = None

        if USE_CAMERA and recognizer:
            # 修复：get_gesture() 返回三个值，第三个是 debug 字典
            gesture, frame, debug_info = recognizer.get_gesture()
        else:
            # 键盘模拟
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                gesture = "charge"
            elif key == ord('b'):
                gesture = "blast"

        # 获取一帧用于显示（键盘模式也需要画面）
        if frame is None:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)

        # 计算 delta time
        now = time.time()
        delta = now - last_time
        last_time = now

        # 更新游戏引擎
        state = engine.update(gesture, delta)

        # 渲染（传入 debug_info）
        if frame is not None:
            display = render_debug(frame, state, gesture, debug_info)
            cv2.imshow("Game Test", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    if recognizer:
        recognizer.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"最终分数: {state['score']}, 最高连击: {state['combo']}")


if __name__ == "__main__":
    main()