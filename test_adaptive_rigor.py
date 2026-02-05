"""
Property-Based Tests for Adaptive Rigor Protocol

Tests verify:
- Gradual recovery from crisis to normal mode
- Proof of Work validation correctness
- Difficulty scaling based on attack intensity
- Configuration broadcasting to listeners
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from aethel.core.adaptive_rigor import AdaptiveRigor, RigorConfig, SystemMode
import time


class TestAdaptiveRigorProperties:
    """Property-based tests for Adaptive Rigor Protocol"""
    
    @given(
        attack_intensity=st.floats(min_value=0.0, max_value=1.0),
        recovery_time=st.floats(min_value=0.0, max_value=70.0)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_17_gradual_recovery(self, attack_intensity, recovery_time):
        """
        Property 17: Gradual recovery
        
        **Validates: Requirements 3.6**
        
        PROPERTY: When Crisis Mode deactivates, the system SHALL gradually restore
        normal configuration over 60 seconds, with timeout increasing linearly,
        proof depth switching at 50% recovery, and PoW disabling at 75% recovery.
        """
        rigor = AdaptiveRigor()
        
        # Activate crisis mode
        rigor.activate_crisis_mode(attack_intensity)
        assert rigor.current_mode == SystemMode.CRISIS
        
        # Deactivate and simulate time passage
        rigor.deactivate_crisis_mode()
        assert rigor.current_mode == SystemMode.NORMAL
        
        # Simulate time passage
        if recovery_time > 0:
            rigor.recovery_start_time = time.time() - recovery_time
        
        config = rigor.get_current_config()
        
        if recovery_time >= 60.0:
            # Full recovery complete
            assert config.z3_timeout == 30
            assert config.proof_depth == "deep"
            assert config.require_pow is False
            assert rigor.recovery_start_time is None
        else:
            # Partial recovery
            progress = recovery_time / 60.0
            
            # Timeout should increase linearly from 5 to 30
            expected_timeout = int(5 + (30 - 5) * progress)
            assert config.z3_timeout == expected_timeout
            
            # Proof depth switches at 50%
            if progress >= 0.5:
                assert config.proof_depth == "deep"
            else:
                assert config.proof_depth == "shallow"
            
            # PoW disables at 75%
            if progress >= 0.75:
                assert config.require_pow is False
            else:
                assert config.require_pow is True
    
    @given(
        nonce=st.text(min_size=1, max_size=20),
        data=st.text(min_size=1, max_size=100),
        difficulty=st.integers(min_value=1, max_value=6)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_16_pow_validation(self, nonce, data, difficulty):
        """
        Property 16: Proof of Work validation
        
        **Validates: Requirements 3.5**
        
        PROPERTY: A PoW solution is valid IF AND ONLY IF the SHA256 hash of
        (data + nonce) starts with the required number of leading zeros.
        """
        rigor = AdaptiveRigor()
        
        # Set up crisis mode with specific difficulty
        rigor.current_config = RigorConfig(
            z3_timeout=5,
            proof_depth="shallow",
            require_pow=True,
            pow_difficulty=difficulty
        )
        
        # Validate PoW
        is_valid = rigor.validate_pow(nonce, data)
        
        # Manually check hash
        import hashlib
        combined = f"{data}{nonce}".encode('utf-8')
        hash_result = hashlib.sha256(combined).hexdigest()
        required_zeros = '0' * difficulty
        expected_valid = hash_result.startswith(required_zeros)
        
        # Property: validation result matches manual check
        assert is_valid == expected_valid
    
    @given(attack_intensity=st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=100)
    def test_property_18_difficulty_scaling(self, attack_intensity):
        """
        Property 18: Difficulty scaling
        
        **Validates: Requirements 3.7**
        
        PROPERTY: PoW difficulty SHALL scale linearly from 4 to 8 leading zeros
        based on attack intensity (0.0 to 1.0).
        """
        rigor = AdaptiveRigor()
        
        difficulty = rigor.calculate_pow_difficulty(attack_intensity)
        
        # Difficulty should be between 4 and 8
        assert 4 <= difficulty <= 8
        
        # Should scale linearly
        expected_difficulty = int(4 + (attack_intensity * 4))
        assert difficulty == expected_difficulty
        
        # Edge cases
        if attack_intensity == 0.0:
            assert difficulty == 4
        if attack_intensity == 1.0:
            assert difficulty == 8
    
    @given(
        attack_intensity=st.floats(min_value=0.0, max_value=1.0),
        num_listeners=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=50)
    def test_property_19_difficulty_notification(self, attack_intensity, num_listeners):
        """
        Property 19: Difficulty notification
        
        **Validates: Requirements 3.8**
        
        PROPERTY: When PoW difficulty changes, all registered listeners SHALL be
        notified within 1 second with the new configuration.
        """
        rigor = AdaptiveRigor()
        
        # Track notifications
        notifications = []
        
        def listener(config: RigorConfig):
            notifications.append((time.time(), config))
        
        # Register multiple listeners
        for _ in range(num_listeners):
            rigor.register_config_listener(listener)
        
        # Activate crisis mode
        start_time = time.time()
        rigor.activate_crisis_mode(attack_intensity)
        end_time = time.time()
        
        # All listeners should be notified
        assert len(notifications) == num_listeners
        
        # All notifications should happen within 1 second
        for notification_time, config in notifications:
            assert notification_time - start_time < 1.0
        
        # All notifications should have correct config
        for _, config in notifications:
            assert config.require_pow is True
            expected_difficulty = int(4 + (attack_intensity * 4))
            assert config.pow_difficulty == expected_difficulty


class TestAdaptiveRigorUnitTests:
    """Unit tests for specific scenarios"""
    
    def test_normal_mode_config(self):
        """Test normal mode configuration"""
        config = RigorConfig.normal_mode()
        
        assert config.z3_timeout == 30
        assert config.proof_depth == "deep"
        assert config.require_pow is False
        assert config.pow_difficulty == 0
    
    def test_crisis_mode_config(self):
        """Test crisis mode configuration"""
        config = RigorConfig.crisis_mode(attack_intensity=0.5)
        
        assert config.z3_timeout == 5
        assert config.proof_depth == "shallow"
        assert config.require_pow is True
        assert config.pow_difficulty == 6  # 4 + (0.5 * 4)
    
    def test_crisis_activation(self):
        """Test crisis mode activation"""
        rigor = AdaptiveRigor()
        
        assert rigor.current_mode == SystemMode.NORMAL
        
        rigor.activate_crisis_mode(0.5)
        
        assert rigor.current_mode == SystemMode.CRISIS
        assert rigor.current_config.require_pow is True
        assert rigor.crisis_start_time is not None
    
    def test_crisis_deactivation(self):
        """Test crisis mode deactivation"""
        rigor = AdaptiveRigor()
        
        rigor.activate_crisis_mode(0.5)
        rigor.deactivate_crisis_mode()
        
        assert rigor.current_mode == SystemMode.NORMAL
        assert rigor.recovery_start_time is not None
    
    def test_pow_not_required_in_normal_mode(self):
        """Test that PoW is not required in normal mode"""
        rigor = AdaptiveRigor()
        
        # Any nonce should be valid in normal mode
        assert rigor.validate_pow("any_nonce", "any_data") is True
    
    def test_pow_validation_with_valid_nonce(self):
        """Test PoW validation with a valid nonce"""
        rigor = AdaptiveRigor()
        rigor.activate_crisis_mode(0.0)  # difficulty = 4
        
        # Find a valid nonce (this might take a few tries)
        data = "test_data"
        for nonce in range(100000):
            if rigor.validate_pow(str(nonce), data):
                # Found valid nonce
                assert True
                return
        
        # If we get here, we didn't find a valid nonce in 100k tries
        # This is extremely unlikely with difficulty 4
        pytest.fail("Could not find valid PoW nonce in 100k tries")
    
    def test_listener_notification(self):
        """Test that listeners are notified of config changes"""
        rigor = AdaptiveRigor()
        
        notifications = []
        rigor.register_config_listener(lambda config: notifications.append(config))
        
        rigor.activate_crisis_mode(0.5)
        
        assert len(notifications) == 1
        assert notifications[0].require_pow is True
    
    def test_listener_error_handling(self):
        """Test that listener errors don't break the system"""
        rigor = AdaptiveRigor()
        
        def bad_listener(config):
            raise Exception("Listener error")
        
        rigor.register_config_listener(bad_listener)
        
        # Should not raise exception
        rigor.activate_crisis_mode(0.5)
        
        # System should still work
        assert rigor.current_mode == SystemMode.CRISIS
    
    def test_multiple_crisis_activations(self):
        """Test that multiple crisis activations update intensity"""
        rigor = AdaptiveRigor()
        
        rigor.activate_crisis_mode(0.25)
        first_difficulty = rigor.current_config.pow_difficulty
        
        rigor.activate_crisis_mode(0.75)
        second_difficulty = rigor.current_config.pow_difficulty
        
        # Difficulty should increase with intensity
        assert second_difficulty > first_difficulty
    
    def test_recovery_completion(self):
        """Test that recovery completes after 60 seconds"""
        rigor = AdaptiveRigor()
        
        rigor.activate_crisis_mode(0.5)
        rigor.deactivate_crisis_mode()
        
        # Simulate 60+ seconds passing
        rigor.recovery_start_time = time.time() - 61.0
        
        config = rigor.get_current_config()
        
        # Should be fully recovered
        assert config.z3_timeout == 30
        assert config.proof_depth == "deep"
        assert config.require_pow is False
        assert rigor.recovery_start_time is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
