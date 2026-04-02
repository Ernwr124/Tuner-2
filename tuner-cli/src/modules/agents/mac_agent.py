import os
import platform

class MacExpertAgent:
    """ИИ-Агент эксперт по Apple Silicon (Metal Performance Shaders)"""
    def __init__(self):
        self.device = "mps" if platform.processor() == "arm" else "cpu"

    def get_config(self, ram_gb):
        return {
            "backend": "mlx-lm",
            "optimization": "unified-memory-access",
            "max_temp": 45,
            "batch_size": 4 if ram_gb >= 16 else 2,
            "instruction": "Используйте MLX для нативной производительности на Mac M1/M2/M3."
        }
