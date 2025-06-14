from pathlib import Path

from src.strategies.base import BaseStrategy
from src.strategies.kaufland import KauflandStrategy
from src.strategies.metro import MetroStrategy
from src.strategies.provitus import ProvitusStrategy
from src.strategies.standard import StandardStrategy

ROOT_PATH = Path(__file__).parent.parent
OUTPUT_PATH = f"{ROOT_PATH}/output/"

STRATEGIES: list[type[BaseStrategy]] = [
    StandardStrategy,
    ProvitusStrategy,
    MetroStrategy,
    KauflandStrategy,
]
