"""
Adaptive Rigor Protocol - Dynamic Defense Scaling

This module implements dynamic adjustment of verification rigor based on threat level.
During normal operations, the system uses standard timeouts and proof depth.
During Crisis Mode, the system reduces timeouts, requires Proof of Work, and applies
stricter validation to defend against attacks while maintaining service for legitimate users.

Key Components:
- RigorConfig: Configuration for normal and crisis modes
- SystemMode: Enum for system operational states
- AdaptiveRigor: Main class managing mode transitions and PoW validation
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
import hashlib
import time


class SystemMode(Enum):
    """System operational modes"""
    NORMAL = "normal"
    CRISIS = "crisis"


@dataclass
class RigorConfig:
    """
    Configuration for verification rigor levels.
    
    Attributes:
        z3_timeout: Z3 solver timeout in seconds
        proof_depth: Depth of proof verification (shallow/deep)
        require_pow: Whether Proof of Work is required
        pow_difficulty: Number of leading zeros required in PoW hash
    """
    z3_timeout: int
    proof_depth: str  # "shallow" or "deep"
    require_pow: bool
    pow_difficulty: int = 0
    
    @staticmethod
    def normal_mode() -> 'RigorConfig':
        """Standard configuration for normal operations"""
        return RigorConfig(
            z3_timeout=30,
            proof_depth="deep",
            require_pow=False,
            pow_difficulty=0
        )
    
    @staticmethod
    def crisis_mode(attack_intensity: float = 0.5) -> 'RigorConfig':
        """
        Emergency configuration for crisis operations.
        
        Args:
            attack_intensity: Float between 0.0 and 1.0 indicating attack severity
        
        Returns:
            RigorConfig with crisis mode settings
        """
        # Scale PoW difficulty from 4 to 8 zeros based on intensity
        pow_difficulty = int(4 + (attack_intensity * 4))
        
        return RigorConfig(
            z3_timeout=5,
            proof_depth="shallow",
            require_pow=True,
            pow_difficulty=pow_difficulty
        )


class AdaptiveRigor:
    """
    Manages dynamic adjustment of verification rigor based on threat level.
    
    This class handles:
    - Mode transitions between normal and crisis states
    - Proof of Work validation during attacks
    - Gradual recovery after crisis ends
    - Configuration broadcasting to other components
    """
    
    def __init__(self):
        self.current_mode = SystemMode.NORMAL
        self.current_config = RigorConfig.normal_mode()
        self.crisis_start_time: Optional[float] = None
        self.recovery_start_time: Optional[float] = None
        self.config_listeners: list[Callable[[RigorConfig], None]] = []
    
    def activate_crisis_mode(self, attack_intensity: float = 0.5) -> None:
        """
        Activate Crisis Mode with appropriate configuration.
        
        Args:
            attack_intensity: Float between 0.0 and 1.0 indicating attack severity
        """
        if self.current_mode == SystemMode.CRISIS:
            # Already in crisis, update intensity if needed
            new_config = RigorConfig.crisis_mode(attack_intensity)
            if new_config.pow_difficulty != self.current_config.pow_difficulty:
                self.current_config = new_config
                self._broadcast_config()
            return
        
        self.current_mode = SystemMode.CRISIS
        self.current_config = RigorConfig.crisis_mode(attack_intensity)
        self.crisis_start_time = time.time()
        self.recovery_start_time = None
        
        self._broadcast_config()
    
    def deactivate_crisis_mode(self) -> None:
        """
        Deactivate Crisis Mode and begin gradual recovery.
        
        Recovery happens over 60 seconds to avoid sudden load spikes.
        """
        if self.current_mode == SystemMode.NORMAL:
            return
        
        self.current_mode = SystemMode.NORMAL
        self.recovery_start_time = time.time()
        
        # Start gradual recovery
        self._begin_gradual_recovery()
    
    def _begin_gradual_recovery(self) -> None:
        """
        Gradually restore normal configuration over 60 seconds.
        
        This prevents sudden load spikes when transitioning from crisis to normal mode.
        """
        if self.recovery_start_time is None:
            return
        
        elapsed = time.time() - self.recovery_start_time
        recovery_duration = 60.0  # seconds
        
        if elapsed >= recovery_duration:
            # Full recovery complete
            self.current_config = RigorConfig.normal_mode()
            self.recovery_start_time = None
        else:
            # Partial recovery - interpolate between crisis and normal
            progress = elapsed / recovery_duration
            
            normal_config = RigorConfig.normal_mode()
            crisis_config = RigorConfig.crisis_mode()
            
            # Linear interpolation of timeout
            timeout = int(
                crisis_config.z3_timeout + 
                (normal_config.z3_timeout - crisis_config.z3_timeout) * progress
            )
            
            # Switch to deep proof at 50% recovery
            proof_depth = "deep" if progress >= 0.5 else "shallow"
            
            # Disable PoW at 75% recovery
            require_pow = progress < 0.75
            
            self.current_config = RigorConfig(
                z3_timeout=timeout,
                proof_depth=proof_depth,
                require_pow=require_pow,
                pow_difficulty=0 if not require_pow else crisis_config.pow_difficulty
            )
        
        self._broadcast_config()
    
    def get_current_config(self) -> RigorConfig:
        """
        Get current rigor configuration.
        
        If in recovery mode, updates the configuration based on elapsed time.
        
        Returns:
            Current RigorConfig
        """
        if self.recovery_start_time is not None:
            self._begin_gradual_recovery()
        
        return self.current_config
    
    def validate_pow(self, nonce: str, data: str) -> bool:
        """
        Validate Proof of Work solution.
        
        Args:
            nonce: Nonce value to test
            data: Data being verified
        
        Returns:
            True if PoW is valid, False otherwise
        """
        if not self.current_config.require_pow:
            return True  # PoW not required
        
        # Calculate hash of data + nonce
        combined = f"{data}{nonce}".encode('utf-8')
        hash_result = hashlib.sha256(combined).hexdigest()
        
        # Check if hash has required number of leading zeros
        required_zeros = '0' * self.current_config.pow_difficulty
        return hash_result.startswith(required_zeros)
    
    def calculate_pow_difficulty(self, attack_intensity: float) -> int:
        """
        Calculate PoW difficulty based on attack intensity.
        
        Args:
            attack_intensity: Float between 0.0 and 1.0
        
        Returns:
            Number of leading zeros required (4-8)
        """
        return int(4 + (attack_intensity * 4))
    
    def register_config_listener(self, listener: Callable[[RigorConfig], None]) -> None:
        """
        Register a callback to be notified of configuration changes.
        
        Args:
            listener: Callback function that receives RigorConfig
        """
        self.config_listeners.append(listener)
    
    def _broadcast_config(self) -> None:
        """Notify all registered listeners of configuration change"""
        for listener in self.config_listeners:
            try:
                listener(self.current_config)
            except Exception:
                # Don't let listener errors break the system
                pass
