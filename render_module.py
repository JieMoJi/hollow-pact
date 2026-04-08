import cv2
import numpy as np


def render_game(frame, state, gesture, debug_info=None):
    """
    渲染游戏画面
    :param frame: 摄像头原始画面 (numpy array)
    :param state: 游戏状态字典 {"energy": int, "combo": int, "score": int, "blast_trigger": bool}
    :param gesture: 当前手势字符串 "charge"/"blast"/"none"
    :param debug_info: 调试信息字典 (可选)
    :return: 绘制后的画面
    """
    if frame is None:
        return None

    h, w = frame.shape[:2]
    overlay = frame.copy()

    # 1. 能量条 (底部居中)
    bar_w = int(w * 0.6)
    bar_h = 30
    bar_x = (w - bar_w) // 2
    bar_y = h - 60

    # 防止能量超出范围导致绘图错误
    energy = max(0, min(100, state.get("energy", 0)))
    fill_w = int(bar_w * energy / 100)

    # 背景 (深灰色)
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)

    # 填充色 (绿 -> 黄 -> 红)
    if energy < 50:
        color = (0, 255, 0)
    elif energy < 80:
        color = (0, 255, 255)
    else:
        color = (0, 0, 255)

    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)

    # 边框 (白色)
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)

    # 能量数值文字
    cv2.putText(overlay, f"Energy: {energy}", (bar_x, bar_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 2. 分数与连击 (左上角)
    cv2.putText(overlay, f"Score: {state.get('score', 0)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(overlay, f"Combo: x{state.get('combo', 0)}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # 3. 当前手势 (右上角)
    g_color = (0, 255, 0) if gesture == "charge" else (0, 0, 255) if gesture == "blast" else (200, 200, 200)
    cv2.putText(overlay, f"Gesture: {gesture.upper()}", (w - 250, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, g_color, 2)

    # 4. 调试信息 (左下角，可选)
    if debug_info:
        txt = f"Dist:{debug_info.get('dist', 0):.2f} Ext:{debug_info.get('ext', 0):.2f}"
        cv2.putText(overlay, txt, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

    # 5. 发波特效 (屏幕中央红圈 + 文字)
    if state.get("blast_trigger", False):
        cv2.circle(overlay, (w // 2, h // 2), 100, (0, 0, 255), 10)
        cv2.putText(overlay, "BLAST!", (w // 2 - 80, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

    # 混合图层 (80% 原图 + 20% 特效，或者反过来看需求，这里用 addWeighted)
    # 注意：如果 overlay 和 frame 完全一样，addWeighted 效果不明显，通常 overlay 是在 frame 上画出来的
    # 这里为了简单，直接返回 overlay 即可，因为上面已经在 overlay 上画图了
    # 如果想做半透明特效，可以用 addWeighted，但上面 draw 操作已经是不透明的了
    # 修正：直接返回 overlay 即可，因为所有画图都在 overlay 上进行了
    return overlay