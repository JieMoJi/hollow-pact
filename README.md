# AI-Gesture-Game-
A gesture-controlled game using MediaPipe hand tracking. Players use fist (charge) and palm (blast) to interact.
# AI Gesture Game

## 安装依赖
pip install mediapipe opencv-python numpy

## 运行手势测试
python test.py

## 文件结构
- gesture_module.py : 手势识别模块，提供 GestureRecognizer 类
- game_engine.py : 游戏引擎
- render_module.py : 游戏渲染
- hand_landmarker.task : 手势AI大模型
- main.py : 主函数
