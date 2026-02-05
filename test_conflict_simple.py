"""Simple conflict detection test without Hypothesis"""

import pytest
from aethel.core.synchrony import Transaction, ConflictType
from aethel.core.dependency_analyzer import DependencyAnalyzer
from aethel.core.conflict_detector import ConflictDetector


def test_no_conflict_disjoint_accounts():
    """Unit test: No conflict with disjoint accounts"""
    t1 = Transaction(
        id="t1",
        intent_name="transfer",
        accounts={"alice": {"balance": 100}},
        operations=[],
        verify_conditions=[]
    )
    
    t2 = Transaction(
        id="t2",
        intent_name="transfer",
        accounts={"bob": {"balance": 100}},
        operations=[],
        verify_conditions=[]
    )
    
    analyzer = DependencyAnalyzer()
    graph = analyzer.analyze([t1, t2])
    
    detector = ConflictDetector()
    conflicts = detector.detect_conflicts([t1, t2], graph)
    
    # Should have NO conflicts
    assert len(conflicts) == 0, f"Expected no conflicts, got {len(conflicts)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
