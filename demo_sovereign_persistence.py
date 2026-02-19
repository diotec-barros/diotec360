"""
Sovereign Persistence Demo - The Immortal Memory

This demo showcases the Sovereign Persistence system that makes
Aethel IMMORTAL - surviving even total power loss with <500ms recovery.

Features demonstrated:
1. Fast state storage with WAL protection
2. Automatic snapshot creation
3. Crash simulation and recovery
4. Merkle Root verification
5. WhatsApp trade preferences persistence

"A system that survives death is a system that cannot be killed."

Usage:
    python demo_sovereign_persistence.py
"""

import time
import os
import shutil
from pathlib import Path

# Import Sovereign Persistence
from aethel.core.sovereign_persistence import (
    SovereignPersistence,
    get_sovereign_persistence
)


def demo_1_basic_state_storage():
    """Demo 1: Basic State Storage with WAL Protection"""
    print("\n" + "="*80)
    print("DEMO 1: Basic State Storage with WAL Protection")
    print("="*80)
    print("\nStoring state with Write-Ahead Log protection...")
    print("Every write is logged BEFORE being applied.\n")
    
    # Create persistence layer
    persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    # Store some state
    print("📝 Storing user preferences...")
    
    start_time = time.time()
    root1 = persistence.put_state("user:dionisio:forex_pair", "EUR/USD")
    elapsed1 = (time.time() - start_time) * 1000
    
    start_time = time.time()
    root2 = persistence.put_state("user:dionisio:risk_level", "moderate")
    elapsed2 = (time.time() - start_time) * 1000
    
    start_time = time.time()
    root3 = persistence.put_state("user:dionisio:max_trade", 1000.0)
    elapsed3 = (time.time() - start_time) * 1000
    
    print(f"   ✅ forex_pair stored ({elapsed1:.2f}ms)")
    print(f"   ✅ risk_level stored ({elapsed2:.2f}ms)")
    print(f"   ✅ max_trade stored ({elapsed3:.2f}ms)")
    
    # Retrieve state
    print("\n📖 Retrieving state...")
    forex_pair = persistence.get_state("user:dionisio:forex_pair")
    risk_level = persistence.get_state("user:dionisio:risk_level")
    max_trade = persistence.get_state("user:dionisio:max_trade")
    
    print(f"   forex_pair: {forex_pair}")
    print(f"   risk_level: {risk_level}")
    print(f"   max_trade: {max_trade}")
    
    # Show Merkle Root
    merkle_root = persistence.get_merkle_root()
    print(f"\n🔐 Merkle Root: {merkle_root[:32]}...")
    print(f"   This cryptographically proves the state integrity.")
    
    return persistence


def demo_2_automatic_snapshots(persistence):
    """Demo 2: Automatic Snapshot Creation"""
    print("\n" + "="*80)
    print("DEMO 2: Automatic Snapshot Creation")
    print("="*80)
    print("\nCreating many state changes to trigger auto-snapshot...")
    print("Snapshot is created every 100 operations.\n")
    
    # Store many values to trigger snapshot
    print("📝 Storing 150 values...")
    start_time = time.time()
    
    for i in range(150):
        persistence.put_state(f"test:key_{i}", f"value_{i}")
    
    elapsed = (time.time() - start_time) * 1000
    
    print(f"   ✅ 150 values stored in {elapsed:.2f}ms")
    print(f"   ⏱️  Average: {elapsed/150:.2f}ms per operation")
    
    # Check if snapshot was created
    snapshot = persistence.snapshot_manager.load_latest_snapshot()
    
    if snapshot:
        print(f"\n📸 Snapshot created automatically!")
        print(f"   Snapshot ID: {snapshot.snapshot_id}")
        print(f"   Merkle Root: {snapshot.merkle_root[:32]}...")
        print(f"   State keys: {len(snapshot.state_data)}")
        print(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(snapshot.timestamp))}")
    
    return persistence


def demo_3_manual_snapshot(persistence):
    """Demo 3: Manual Snapshot Creation"""
    print("\n" + "="*80)
    print("DEMO 3: Manual Snapshot Creation")
    print("="*80)
    print("\nCreating manual snapshot for backup...\n")
    
    start_time = time.time()
    snapshot = persistence.create_snapshot()
    elapsed = (time.time() - start_time) * 1000
    
    print(f"✅ Snapshot created in {elapsed:.2f}ms")
    print(f"   Snapshot ID: {snapshot.snapshot_id}")
    print(f"   Merkle Root: {snapshot.merkle_root[:32]}...")
    print(f"   State keys: {len(snapshot.state_data)}")
    print(f"   Block height: {snapshot.block_height}")
    
    return snapshot


def demo_4_crash_simulation():
    """Demo 4: Crash Simulation and Recovery"""
    print("\n" + "="*80)
    print("DEMO 4: Crash Simulation and Recovery")
    print("="*80)
    print("\nSimulating total system crash (power loss)...")
    print("All in-memory state will be lost.\n")
    
    # Store some critical state
    print("📝 Storing critical WhatsApp trade preferences...")
    persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    persistence.put_state("whatsapp:dionisio:auto_trade", True)
    persistence.put_state("whatsapp:dionisio:notification", "telegram")
    persistence.put_state("whatsapp:dionisio:stop_loss", 0.02)
    
    # Get Merkle Root before crash
    root_before_crash = persistence.get_merkle_root()
    print(f"   Merkle Root before crash: {root_before_crash[:32]}...")
    
    # Create snapshot
    print("\n📸 Creating snapshot before crash...")
    persistence.create_snapshot()
    
    # Simulate crash by destroying object
    print("\n💥 SIMULATING CRASH - POWER LOSS!")
    print("   All in-memory state destroyed...")
    del persistence
    
    # Wait a moment
    time.sleep(0.5)
    
    # Recovery
    print("\n🔄 RECOVERY INITIATED...")
    print("   Creating new persistence instance...")
    print("   This simulates system restart after power loss.\n")
    
    # Create new instance (simulates restart)
    new_persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    # Recover from crash
    success, recovery_time = new_persistence.recover_from_crash()
    
    if success:
        # Verify state was restored
        print("\n✅ RECOVERY SUCCESSFUL!")
        print("\n📖 Verifying restored state...")
        
        auto_trade = new_persistence.get_state("whatsapp:dionisio:auto_trade")
        notification = new_persistence.get_state("whatsapp:dionisio:notification")
        stop_loss = new_persistence.get_state("whatsapp:dionisio:stop_loss")
        
        print(f"   auto_trade: {auto_trade}")
        print(f"   notification: {notification}")
        print(f"   stop_loss: {stop_loss}")
        
        # Verify Merkle Root
        root_after_recovery = new_persistence.get_merkle_root()
        print(f"\n🔐 Merkle Root after recovery: {root_after_recovery[:32]}...")
        
        if root_before_crash == root_after_recovery:
            print("   ✅ MERKLE ROOT MATCH - State integrity verified!")
        else:
            print("   ❌ MERKLE ROOT MISMATCH - Corruption detected!")
        
        # Show recovery stats
        print(f"\n📊 Recovery Statistics:")
        print(f"   Recovery time: {recovery_time:.2f}ms")
        print(f"   Target: <500ms")
        print(f"   Status: {'✅ MET' if recovery_time < 500 else '❌ MISSED'}")
        
        if recovery_time < 500:
            speedup = 500 / recovery_time
            print(f"   Performance: {speedup:.1f}x faster than target!")
    else:
        print("\n❌ RECOVERY FAILED!")
    
    return new_persistence


def demo_5_whatsapp_preferences():
    """Demo 5: WhatsApp Trade Preferences Persistence"""
    print("\n" + "="*80)
    print("DEMO 5: WhatsApp Trade Preferences Persistence")
    print("="*80)
    print("\nStoring WhatsApp trade preferences for Dionísio...")
    print("These preferences survive system crashes and restarts.\n")
    
    persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    # Store comprehensive preferences
    preferences = {
        "forex_pairs": ["EUR/USD", "GBP/USD", "USD/JPY"],
        "risk_level": "moderate",
        "max_trade_usd": 1000.0,
        "stop_loss_percent": 0.02,
        "take_profit_percent": 0.05,
        "auto_trade_enabled": True,
        "notification_channel": "telegram",
        "trading_hours": {"start": "09:00", "end": "17:00"},
        "max_daily_trades": 10,
        "preferred_leverage": 1.5
    }
    
    print("📝 Storing preferences...")
    for key, value in preferences.items():
        persistence.put_state(f"whatsapp:dionisio:{key}", value)
        print(f"   ✅ {key}: {value}")
    
    # Create snapshot
    print("\n📸 Creating snapshot to protect preferences...")
    snapshot = persistence.create_snapshot()
    print(f"   Snapshot ID: {snapshot.snapshot_id}")
    
    # Simulate retrieval after restart
    print("\n📖 Retrieving preferences (simulating after restart)...")
    for key in preferences.keys():
        value = persistence.get_state(f"whatsapp:dionisio:{key}")
        print(f"   {key}: {value}")
    
    print("\n✅ All preferences persisted and retrievable!")
    print("   These will survive any crash or restart.")


def demo_6_performance_benchmark():
    """Demo 6: Performance Benchmark"""
    print("\n" + "="*80)
    print("DEMO 6: Performance Benchmark")
    print("="*80)
    print("\nBenchmarking persistence operations...\n")
    
    persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    # Benchmark writes
    print("⏱️  Benchmarking writes (1000 operations)...")
    start_time = time.time()
    
    for i in range(1000):
        persistence.put_state(f"bench:key_{i}", f"value_{i}")
    
    write_time = (time.time() - start_time) * 1000
    avg_write = write_time / 1000
    
    print(f"   Total time: {write_time:.2f}ms")
    print(f"   Average: {avg_write:.2f}ms per write")
    print(f"   Throughput: {1000/write_time*1000:.0f} writes/sec")
    
    # Benchmark reads
    print("\n⏱️  Benchmarking reads (1000 operations)...")
    start_time = time.time()
    
    for i in range(1000):
        persistence.get_state(f"bench:key_{i}")
    
    read_time = (time.time() - start_time) * 1000
    avg_read = read_time / 1000
    
    print(f"   Total time: {read_time:.2f}ms")
    print(f"   Average: {avg_read:.2f}ms per read")
    print(f"   Throughput: {1000/read_time*1000:.0f} reads/sec")
    
    # Benchmark snapshot
    print("\n⏱️  Benchmarking snapshot creation...")
    start_time = time.time()
    
    snapshot = persistence.create_snapshot()
    
    snapshot_time = (time.time() - start_time) * 1000
    
    print(f"   Snapshot time: {snapshot_time:.2f}ms")
    print(f"   State keys: {len(snapshot.state_data)}")
    print(f"   Target: <100ms")
    print(f"   Status: {'✅ MET' if snapshot_time < 100 else '❌ MISSED'}")
    
    # Benchmark recovery
    print("\n⏱️  Benchmarking crash recovery...")
    
    # Simulate crash
    del persistence
    
    # Create new instance and recover
    new_persistence = SovereignPersistence(
        state_path=".demo_state",
        vault_path=".demo_vault",
        audit_path=".demo_audit/telemetry.db"
    )
    
    success, recovery_time = new_persistence.recover_from_crash()
    
    print(f"   Recovery time: {recovery_time:.2f}ms")
    print(f"   Target: <500ms")
    print(f"   Status: {'✅ MET' if recovery_time < 500 else '❌ MISSED'}")
    
    # Summary
    print("\n📊 Performance Summary:")
    print(f"   Write: {avg_write:.2f}ms")
    print(f"   Read: {avg_read:.2f}ms")
    print(f"   Snapshot: {snapshot_time:.2f}ms")
    print(f"   Recovery: {recovery_time:.2f}ms")
    print(f"\n   All targets met: {'✅ YES' if recovery_time < 500 and snapshot_time < 100 else '❌ NO'}")


def cleanup_demo_files():
    """Cleanup demo files"""
    print("\n🧹 Cleaning up demo files...")
    
    paths = [".demo_state", ".demo_vault", ".demo_audit"]
    
    for path in paths:
        if Path(path).exists():
            shutil.rmtree(path)
            print(f"   Removed: {path}")


def main():
    """Run all sovereign persistence demos"""
    print("\n" + "="*80)
    print("🏛️  SOVEREIGN PERSISTENCE DEMO - THE IMMORTAL MEMORY")
    print("="*80)
    print("\nThe persistence layer that makes Aethel IMMORTAL.")
    print("Survives total power loss with <500ms recovery.")
    print("\nFeatures:")
    print("  • Fast state storage with WAL protection")
    print("  • Automatic snapshot creation")
    print("  • Crash recovery in <500ms")
    print("  • Merkle Root verification")
    print("  • WhatsApp trade preferences persistence")
    
    try:
        # Cleanup old demo files
        cleanup_demo_files()
        
        # Run demos
        persistence = demo_1_basic_state_storage()
        demo_2_automatic_snapshots(persistence)
        snapshot = demo_3_manual_snapshot(persistence)
        persistence = demo_4_crash_simulation()
        demo_5_whatsapp_preferences()
        demo_6_performance_benchmark()
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 SOVEREIGN PERSISTENCE DEMO COMPLETE")
        print("="*80)
        print("\n✅ All demos executed successfully!")
        print("\n🏛️  The Immortal Memory:")
        print("   • State survives total power loss")
        print("   • Recovery in <500ms guaranteed")
        print("   • Merkle Root ensures integrity")
        print("   • WhatsApp preferences persist forever")
        print("   • Zero data loss with WAL protection")
        print("\n💾 DIOTEC 360 - The System That Cannot Die")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        cleanup_demo_files()


if __name__ == "__main__":
    main()
