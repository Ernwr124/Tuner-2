import platform
import os
import sys

# Импортируем наших новых экспертов
try:
    from .mac_agent import MacExpertAgent
    from .cpu_agent import CPUEquationAgent
    from .win_agent import WindowsTacticalAgent
except ImportError:
    # На случай если запуск идет не как модуль
    sys.path.append(os.path.dirname(__file__))
    from mac_agent import MacExpertAgent
    from cpu_agent import CPUEquationAgent
    from win_agent import WindowsTacticalAgent

class AgentDispatcher:
    """Мозг системы: анализирует среду и вызывает нужного агента-специалиста"""

    def __init__(self, hw_info):
        self.hw = hw_info
        self.os_name = platform.system()
        self.is_apple = platform.processor() == "arm" or "mac" in self.os_name.lower()
        self.has_gpu = hw_info.get("cuda", {}).get("gpu") is not None

    def dispatch_mission(self):
        """Выбирает стратегию и соответствующего агента"""

        # 1. Если это Mac
        if self.is_apple:
            agent = MacExpertAgent()
            return "MAC_STRATEGY", agent.get_config(self.hw.get("ram_gb", 8))

        # 2. Если это Windows
        if self.os_name == "Windows":
            agent = WindowsTacticalAgent()
            # Для Windows проверяем наличие GPU
            if self.has_gpu:
                return "WIN_GPU_STRATEGY", agent.fix_bitsandbytes()
            else:
                cpu_agent = CPUEquationAgent()
                return "WIN_CPU_STRATEGY", cpu_agent.get_config(self.hw.get("cpu", {}).get("count", 4))

        # 3. Если это Linux (как сейчас)
        if self.os_name == "Linux":
            if self.has_gpu:
                # Текущая стандартная логика (Unsloth)
                return "LINUX_GPU_POWER", {"engine": "unsloth", "status": "optimal"}
            else:
                agent = CPUEquationAgent()
                return "LINUX_CPU_SURVIVAL", agent.get_config(self.hw.get("cpu", {}).get("count", 4))

        return "UNKNOWN_ENVIRONMENT", {"action": "standard_fallback"}

def get_global_recommendation(hw_info):
    """Быстрая функция для получения совета от системы агентов"""
    dispatcher = AgentDispatcher(hw_info)
    strategy, config = dispatcher.dispatch_mission()
    return f"Агент-Диспетчер определил стратегию: {strategy}. Рекомендуемые параметры: {config}"
