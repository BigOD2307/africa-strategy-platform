# Africa Strategy - Prompts Configuration
# Chaque bloc a son propre fichier de prompt

from .bloc1_prompt import BLOC1_PROMPT
from .bloc2_prompt import BLOC2_PROMPT
from .bloc3_prompt import BLOC3_PROMPT
from .bloc4_prompt import BLOC4_PROMPT
from .bloc5_prompt import BLOC5_PROMPT
from .bloc6_prompt import BLOC6_PROMPT
from .bloc7_prompt import BLOC7_PROMPT

ALL_PROMPTS = {
    "BLOC1": BLOC1_PROMPT,
    "BLOC2": BLOC2_PROMPT,
    "BLOC3": BLOC3_PROMPT,
    "BLOC4": BLOC4_PROMPT,
    "BLOC5": BLOC5_PROMPT,
    "BLOC6": BLOC6_PROMPT,
    "BLOC7": BLOC7_PROMPT,
}

__all__ = [
    "BLOC1_PROMPT",
    "BLOC2_PROMPT", 
    "BLOC3_PROMPT",
    "BLOC4_PROMPT",
    "BLOC5_PROMPT",
    "BLOC6_PROMPT",
    "BLOC7_PROMPT",
    "ALL_PROMPTS",
]

