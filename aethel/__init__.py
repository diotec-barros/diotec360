"""
Aethel - The First Programming Language That Refuses "Maybe"

A proof system that generates code as a byproduct of mathematical certainty.
"""

__version__ = "1.8.0"
__epoch__ = 1
__status__ = "SYNCHRONY_PROTOCOL"

from aethel.core.parser import AethelParser
from aethel.core.judge import AethelJudge
from aethel.core.bridge import AethelBridge
from aethel.core.kernel import AethelKernel
from aethel.core.vault import AethelVault
from aethel.core.weaver import AethelWeaver

__all__ = [
    'AethelParser',
    'AethelJudge',
    'AethelBridge',
    'AethelKernel',
    'AethelVault',
    'AethelWeaver',
]
