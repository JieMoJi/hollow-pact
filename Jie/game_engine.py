import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameState:
    """游戏状态数据结构"""
    energy: int = 0               # 0-100 能量值
    combo: int = 0                # 连击数
    score: int = 0                # 总分
    blast_trigger: bool = False   # 是否触发发波（渲染用）
    blast_cooldown: float = 0.0   # 发波冷却时间戳

    def to_dict(self) -> dict:
        """转为字典，供渲染模块使用"""
        return {
            "energy": self.energy,
            "combo": self.combo,
            "score": self.score,
            "blast_trigger": self.blast_trigger,
        }


class GameEngine:
    """游戏引擎：管理能量、连击、发波逻辑"""

    def __init__(self):
        self.state = GameState()
        self.last_gesture = "none"
        self.charge_start_time = 0.0       # 开始聚气的时间
        self.combo_window = 2.0            # 连击判定窗口（秒）
        self.last_blast_time = 0.0         # 上次发波时间
        self.max_energy = 100
        self.blast_cost = 30               # 发波消耗能量
        self.blast_cooldown_duration = 0.5 # 发波冷却（秒）

    def update(self, gesture: str, delta_time: float = 0.033) -> dict:
        """
        主更新函数，每帧调用
        输入: gesture - "charge" | "blast" | "none"
              delta_time - 帧间隔（默认30fps≈0.033s）
        返回: 状态字典供渲染使用
        """
        now = time.time()
        # 重置每帧标志
        self.state.blast_trigger = False

        # ===== 手势处理 =====
        if gesture == "charge":
            self._handle_charge(now)
        elif gesture == "blast":
            self._handle_blast(now)
        # "none" 时不做额外处理

        # 更新冷却
        if now < self.state.blast_cooldown:
            self.state.blast_trigger = False

        self.last_gesture = gesture
        return self.state.to_dict()

    def _handle_charge(self, now: float):
        """聚气：能量增加，启动连击计时"""
        self.state.energy = min(self.state.energy + 1, self.max_energy)
        if self.charge_start_time == 0:
            self.charge_start_time = now

    def _handle_blast(self, now: float):
        """发波：消耗能量，触发特效，计算连击"""
        # 检查冷却和能量
        if now < self.state.blast_cooldown:
            return
        if self.state.energy < self.blast_cost:
            return

        # 执行发波
        self.state.energy -= self.blast_cost
        self.state.blast_trigger = True
        self.state.blast_cooldown = now + self.blast_cooldown_duration
        self.last_blast_time = now

        # 连击计算
        if (self.charge_start_time > 0 and
            (now - self.last_blast_time) < self.combo_window + 3.0):
            self.state.combo += 1
            self.state.score += 100 * self.state.combo
        else:
            self.state.combo = 1
            self.state.score += 100

        # 重置聚气计时
        self.charge_start_time = 0

    def reset(self):
        """重置游戏"""
        self.state = GameState()
        self.last_gesture = "none"
        self.charge_start_time = 0.0
        self.last_blast_time = 0.0