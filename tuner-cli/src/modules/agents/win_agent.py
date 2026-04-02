import os

class WindowsTacticalAgent:
    """ИИ-Агент для адаптации проекта под среду Windows"""
    def __init__(self):
        self.os_type = "nt"

    def get_adapter_path(self):
        # На Windows часто проблемы с длинными путями
        return os.path.abspath("./models").replace("\\", "/")

    def fix_bitsandbytes(self):
        return {
            "patch": "Replace libbitsandbytes_cuda.so with .dll",
            "env_var": "CUDA_VISIBLE_DEVICES",
            "tip": "Используйте WSL2 для 2х кратного ускорения на Windows."
        }
