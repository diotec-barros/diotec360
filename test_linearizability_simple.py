"""
Simple Unit Tests for Linearizability Prover
"""

import pytest
from aethel.core.linearizability_prover import LinearizabilityProver
from aethel.core.synchrony import Transaction, ExecutionResult, ExecutionEvent, EventType


def test_prover_creation():
    """Test that prover can be created"""
    prover = LinearizabilityProver(timeout_seconds=30)
    assert prover is not None
    assert prover.timeout_seconds == 30


def test_encode_execution_basic():
    """Test basic execution encoding"""
    prover = LinearizabilityProver()
    
    transactions = [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}, "B": {}},
            operations=[],
            verify_conditions=[]
        )
    ]
    
    execution_result = ExecutionResult(
        final_states={"A": {"balance": 100}, "B": {"balance": 200}},
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    constraints = prover.encode_execution(execution_result, transactions)
    assert len(constraints) > 0


def test_find_serial_order_single():
    """Test finding serial order for single transaction"""
    prover = LinearizabilityProver()
    
    transactions = [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}},
            operations=[],
            verify_conditions=[]
        )
    ]
    
    execution_result = ExecutionResult(
        final_states={"A": {"balance": 100}},
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    serial_order = prover.find_serial_order(transactions, execution_result)
    assert serial_order is not None
    assert len(serial_order) == 1
    assert serial_order[0] == "T1"


def test_prove_linearizability_single():
    """Test linearizability proof for single transaction"""
    prover = LinearizabilityProver()
    
    transactions = [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}},
            operations=[],
            verify_conditions=[]
        )
    ]
    
    execution_result = ExecutionResult(
        final_states={"A": {"balance": 100}},
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    proof_result = prover.prove_linearizability(execution_result, transactions)
    assert proof_result.is_linearizable is True
    assert proof_result.serial_order is not None
    assert proof_result.proof is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
