"""Simple test"""
import pytest

def test_simple():
    assert 1 == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
