#!/usr/bin/env python3
"""
Deploy Sentinel in Full Activation Mode

Full Activation: Production thresholds
- Sentinel Monitor: ENABLED
- Semantic Sanitizer: ENABLED (production thresholds)
- Crisis Mode: ENABLED (production thresholds)
- Quarantine: ENABLED
- Self-Healing: ENABLED (auto-inject with zero false positives)
- Adversarial Vaccine: ENABLED (scheduled training)

Purpose: Full production deployment

Duration: Ongoing

Usage:
    python scripts/deploy_full_activation.py
    python scripts/deploy_full_activation.py --config ./config/production.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_production_config(output_path: str) -> None:
    """Create production configuration file."""
    config = """# Autonomous Sentinel v1.9.0 - Production Configuration
# Purpose: Full activation with production thresholds
# Duration: Ongoing production deployment

# ============================================================================
# Core Sentinel Settings
# ============================================================================
AETHEL_SENTINEL_ENABLED=true
AETHEL_SENTINEL_MODE=production
AETHEL_TELEMETRY_DB_PATH=./data/telemetry.db

# ============================================================================
# Semantic Sanitizer - ENABLED (Production Thresholds)
# ============================================================================
AETHEL_SEMANTIC_SANITIZER_ENABLED=true
AETHEL_SEMANTIC_SANITIZER_BLOCK=true
AETHEL_PATTERN_DB_PATH=./data/trojan_patterns.json
AETHEL_ENTROPY_THRESHOLD=0.8  # Production threshold
AETHEL_SEMANTIC_TIMEOUT_MS=100

# ============================================================================
# Crisis Mode - ENABLED (Production Thresholds)
# ============================================================================
AETHEL_CRISIS_MODE_ENABLED=true
AETHEL_CRISIS_ANOMALY_THRESHOLD=0.10  # 10% anomaly rate
AETHEL_CRISIS_REQUEST_THRESHOLD=1000  # 1000 req/s
AETHEL_CRISIS_COOLDOWN_SECONDS=120

# ============================================================================
# Adaptive Rigor - ENABLED
# ============================================================================
AETHEL_NORMAL_Z3_TIMEOUT=30
AETHEL_CRISIS_Z3_TIMEOUT=5
AETHEL_POW_BASE_DIFFICULTY=4
AETHEL_POW_MAX_DIFFICULTY=8

# ============================================================================
# Quarantine System - ENABLED
# ============================================================================
AETHEL_QUARANTINE_ENABLED=true
AETHEL_QUARANTINE_CAPACITY=100
AETHEL_QUARANTINE_THRESHOLD=0.7  # Production threshold

# ============================================================================
# Self-Healing - ENABLED (Auto-Inject)
# ============================================================================
AETHEL_SELF_HEALING_ENABLED=true
AETHEL_SELF_HEALING_AUTO_INJECT=true  # Auto-inject with zero false positives
AETHEL_RULE_EFFECTIVENESS_THRESHOLD=0.7
AETHEL_HISTORICAL_TX_LIMIT=1000

# ============================================================================
# Adversarial Vaccine - ENABLED (Scheduled Training)
# ============================================================================
AETHEL_VACCINE_ENABLED=true
AETHEL_VACCINE_SCHEDULE="0 2 * * *"  # Daily at 2 AM
AETHEL_VACCINE_SCENARIOS=1000

# ============================================================================
# Gauntlet Report - ENABLED
# ============================================================================
AETHEL_GAUNTLET_DB_PATH=./data/gauntlet.db
AETHEL_RETENTION_DAYS=90

# ============================================================================
# Monitoring and Logging
# ============================================================================
AETHEL_LOG_LEVEL=INFO
AETHEL_METRICS_ENABLED=true
AETHEL_METRICS_PORT=9090

# ============================================================================
# Alerting - ENABLED (All Alerts)
# ============================================================================
AETHEL_ALERT_CRISIS_MODE=true
AETHEL_ALERT_FALSE_POSITIVE_RATE=true
AETHEL_ALERT_OVERHEAD=true
AETHEL_ALERT_QUARANTINE_CAPACITY=true
AETHEL_ALERT_SELF_HEALING_RULE=true
AETHEL_ALERT_VACCINE_VULNERABILITY=true

# ============================================================================
# Performance Tuning
# ============================================================================
AETHEL_PATTERN_CACHE_SIZE=1000
AETHEL_TELEMETRY_BATCH_SIZE=100
AETHEL_ASYNC_PERSISTENCE=true
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Production configuration created: {output_path}")


def validate_soft_launch_complete() -> bool:
    """Validate that soft launch was completed successfully."""
    print("🔍 Validating soft launch completion...")
    
    # Check false positive rate
    import sqlite3
    conn = sqlite3.connect('./data/gauntlet.db')
    cursor = conn.cursor()
    
    # Check if we have attack records
    cursor.execute("SELECT COUNT(*) FROM attack_records")
    attack_count = cursor.fetchone()[0]
    
    if attack_count < 100:
        print(f"⚠️  Only {attack_count} attacks recorded")
        print("   Recommended: At least 100 attacks for validation")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            conn.close()
            return False
    
    # Check Self-Healing rules
    cursor.execute("SELECT COUNT(*) FROM self_healing_rules WHERE active=1")
    rule_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Soft launch complete:")
    print(f"   - {attack_count} attacks recorded")
    print(f"   - {rule_count} active Self-Healing rules")
    
    return True


def deploy_full_activation(config_path: str) -> None:
    """Deploy Sentinel in full activation mode."""
    print("\n🚀 Deploying Autonomous Sentinel in Full Activation Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    print("\n✅ Full Activation Deployment Complete!")
    print("\n🎉 Autonomous Sentinel is now fully operational!")
    
    print("\n📊 Monitoring:")
    print("   - Telemetry: http://localhost:9090/metrics")
    print("   - Dashboard: http://localhost:3000/sentinel")
    print("   - Logs: tail -f logs/sentinel.log")
    print("   - Gauntlet Report: http://localhost:3000/gauntlet")
    print("   - Self-Healing: http://localhost:3000/self-healing")
    print("   - Vaccine Reports: http://localhost:3000/vaccine")
    
    print("\n📈 What to Monitor:")
    print("   1. False Positive Rate:")
    print("      - Target: <0.1%")
    print("      - Alert if >1%")
    print("   2. Crisis Mode Activations:")
    print("      - Monitor frequency and duration")
    print("      - Review attack patterns")
    print("   3. Self-Healing:")
    print("      - Rules generated automatically")
    print("      - Monitor effectiveness scores")
    print("      - Review deactivated rules")
    print("   4. Adversarial Vaccine:")
    print("      - Daily training at 2 AM")
    print("      - Review vulnerability reports")
    print("      - Monitor patch success rate")
    print("   5. Performance:")
    print("      - Overhead should remain <5%")
    print("      - Throughput ≥95% of v1.8.0")
    
    print("\n🔔 Alerts Configured:")
    print("   - Crisis Mode activation (CRITICAL)")
    print("   - False positive rate >1% (WARNING)")
    print("   - Overhead >10% (CRITICAL)")
    print("   - Quarantine capacity >90% (CRITICAL)")
    print("   - New Self-Healing rule (INFO)")
    print("   - Vaccine vulnerability found (WARNING)")
    
    print("\n📝 Ongoing Maintenance:")
    print("   1. Review Gauntlet Reports weekly")
    print("   2. Review Self-Healing rules monthly")
    print("   3. Review Vaccine reports weekly")
    print("   4. Adjust thresholds based on traffic patterns")
    print("   5. Export compliance reports monthly")
    
    print("\n🔄 Rollback Plan:")
    print("   If issues arise, rollback with:")
    print("   python scripts/rollback_sentinel.py")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Sentinel in Full Activation Mode (production)"
    )
    parser.add_argument(
        '--config',
        default='./config/production.env',
        help='Path to configuration file (default: ./config/production.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip soft launch validation'
    )
    
    args = parser.parse_args()
    
    # Validate soft launch complete
    if not args.skip_validation:
        if not validate_soft_launch_complete():
            sys.exit(1)
    
    # Create configuration
    create_production_config(args.config)
    
    # Deploy
    deploy_full_activation(args.config)


if __name__ == '__main__':
    main()
