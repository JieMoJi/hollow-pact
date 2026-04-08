本项目是一款基于 计算机视觉 (Computer Vision) 和 人工智能 的实时互动游戏。玩家无需佩戴任何传感器，仅通过摄像头捕捉手部动作，即可控制游戏角色进行“聚气”、“发波”及释放多种元素技能。

项目旨在探索轻量化 AI 模型在边缘计算设备（如昇腾开发板）上的实时推理应用，实现低延迟、高流畅度的体感交互体验。
# AI-Gesture-Game-
A gesture-controlled game using MediaPipe hand tracking. Players use fist (charge) and palm (blast) to interact.
# AI Gesture Game

## 安装依赖
pip install mediapipe opencv-python numpy

## 文件结构
- gesture_module.py : 手势识别模块，提供 GestureRecognizer 类
- game_engine.py : 游戏引擎
- render_module.py : 游戏渲染
- hand_landmarker.task : 手势AI大模型
- main.py : 主函数
