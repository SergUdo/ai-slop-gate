from enum import Enum


class Signal(str, Enum):
    INSECURE_CONFIG = "insecure_config"
    BEST_PRACTICE = "best_practice"
    MISCONFIGURATION = "misconfiguration"
