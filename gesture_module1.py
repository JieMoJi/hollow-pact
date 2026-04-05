import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import math
import numpy as np


class GestureRecognizer:
    """手势识别器：封装初始化、识别、资源释放"""

    def __init__(self, model_path='hand_landmarker.task'):
        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(0)
        self.timestamp_ms = 0

    def get_gesture(self):
        """
        返回: (gesture_str, camera_frame)
        gesture_str: "charge" | "blast" | "none"
        camera_frame: numpy array (BGR格式)，如果读取失败则为 None
        """
        ret, frame = self.cap.read()
        if not ret:
            return "none", None

        frame = cv2.flip(frame, 1)

        # 时间戳递增（假设30fps，约33ms一帧）
        self.timestamp_ms += 33

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        result = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)

        gesture = "none"
        if result.hand_landmarks:
            gesture = self._classify(result.hand_landmarks[0])

        return gesture, frame

    def _classify(self, landmarks):
        """内部：握拳/摊掌分类"""
        WRIST = 0
        THUMB_TIP = 4
        FINGER_TIPS = [8, 12, 16, 20]
        FINGER_PIPS = [6, 10, 14, 18]

        def distance(p1, p2):
            return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

        wrist = landmarks[WRIST]

        tip_distances = [distance(landmarks[tip], wrist) for tip in FINGER_TIPS]
        avg_tip_dist = sum(tip_distances) / len(tip_distances)

        extensions = []
        for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
            tip_to_pip = distance(landmarks[tip], landmarks[pip])
            pip_to_wrist = distance(landmarks[pip], wrist)
            if pip_to_wrist > 0.001:
                extensions.append(tip_to_pip / pip_to_wrist)
        avg_extension = sum(extensions) / len(extensions) if extensions else 0

        CHARGE_MAX_DIST = 0.20
        BLAST_MIN_DIST = 0.35
        BLAST_MIN_EXTENSION = 0.30

        if avg_tip_dist < CHARGE_MAX_DIST:
            return "charge"
        elif avg_tip_dist > BLAST_MIN_DIST and avg_extension > BLAST_MIN_EXTENSION:
            return "blast"
        else:
            return "none"

    def release(self):
        self.cap.release()
