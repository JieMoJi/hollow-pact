import cv2
import time
from gesture_module import GestureRecognizer
from game_engine import GameEngine
from render_module import render_game


def main():
    print("🚀 启动 AI 手势体感游戏...")

    engine = GameEngine()
    recognizer = GestureRecognizer()
    last_time = time.time()

    while True:
        # 1. 获取手势
        gesture, frame, debug = recognizer.get_gesture()
        if frame is None:
            break

        # 2. 计算时间差
        now = time.time()
        dt = now - last_time
        last_time = now

        # 3. 更新游戏状态
        state = engine.update(gesture, dt)

        # 4. 渲染画面
        display = render_game(frame, state, gesture, debug)

        # 5. 显示
        cv2.imshow("AI Gesture Game", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    recognizer.release()
    cv2.destroyAllWindows()
    print(f"🎮 游戏结束！最终得分：{state['score']}")


if __name__ == "__main__":
    main()
