import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import math
import numpy as np


class GestureRecognizer:
    """手势识别器：输出标准 charge/blast/none 供游戏引擎使用"""

    def __init__(self, model_path='hand_landmarker.task'):
        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(0)
        self.timestamp_ms = 0

        # 调参记录（根据实际运行数据更新）
        self.last_debug = {}

    def get_gesture(self):
        """
        返回: (gesture_str, frame, debug_info)
        gesture_str: "charge" | "blast" | "none"
        """
        ret, frame = self.cap.read()
        if not ret:
            return "none", None, {}

        frame = cv2.flip(frame, 1)
        self.timestamp_ms += 33

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        result = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)

        gesture = "none"
        debug = {"dist": 0, "ext": 0, "points": []}

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            gesture, debug = self._classify_with_debug(landmarks)

            # 画关键点
            h, w = frame.shape[:2]
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

        self.last_debug = debug
        return gesture, frame, debug

    def _classify_with_debug(self, landmarks):
        """分类并返回调试数据"""
        WRIST = 0
        FINGER_TIPS = [8, 12, 16, 20]
        FINGER_PIPS = [6, 10, 14, 18]

        def dist(p1, p2):
            return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

        wrist = landmarks[WRIST]

        # 计算特征
        tip_dists = [dist(landmarks[tip], wrist) for tip in FINGER_TIPS]
        avg_tip_dist = sum(tip_dists) / len(tip_dists)

        extensions = []
        for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
            tip_to_pip = dist(landmarks[tip], landmarks[pip])
            pip_to_wrist = dist(landmarks[pip], wrist)
            if pip_to_wrist > 0.001:
                extensions.append(tip_to_pip / pip_to_wrist)
        avg_ext = sum(extensions) / len(extensions) if extensions else 0

        # 阈值判定（基于你的实际数据）
        CHARGE_MAX = 0.25
        BLAST_MIN_DIST = 0.45
        BLAST_MIN_EXT = 0.28

        if avg_tip_dist < CHARGE_MAX:
            gesture = "charge"
        elif avg_tip_dist > BLAST_MIN_DIST and avg_ext > BLAST_MIN_EXT:
            gesture = "blast"
        else:
            gesture = "none"

        debug = {
            "dist": round(avg_tip_dist, 3),
            "ext": round(avg_ext, 3),
            "thresholds": f"charge<{CHARGE_MAX}, blast>{BLAST_MIN_DIST}&ext>{BLAST_MIN_EXT}"
        }
        return gesture, debug

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
