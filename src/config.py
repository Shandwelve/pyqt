from pathlib import Path

from src.strategies.base import BaseStrategy
from src.strategies.provitus import ProvitusStrategy

ROOT_PATH = Path(__file__).parent.parent
OUTPUT_PATH = f"{ROOT_PATH}/output/"

STRATEGIES: list[type[BaseStrategy]] = [ProvitusStrategy]
