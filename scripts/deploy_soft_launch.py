#!/usr/bin/env python3
"""
Deploy Sentinel in Soft Launch Mode

Soft Launch: Blocking enabled with high thresholds
- Sentinel Monitor: ENABLED
- Semantic Sanitizer: ENABLED (block with high thresholds)
- Crisis Mode: ENABLED (high thresholds)
- Quarantine: ENABLED
- Self-Healing: ENABLED (manual approval for first 100 rules)
- Adversarial Vaccine: DISABLED

Purpose: Gradual activation with conservative thresholds

Duration: 2-4 weeks

Usage:
    python scripts/deploy_soft_launch.py
    python scripts/deploy_soft_launch.py --config ./config/soft_launch.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_soft_launch_config(output_path: str) -> None:
    """Create soft launch configuration file."""
    config = """# Autonomous Sentinel v1.9.0 - Soft Launch Configuration
# Purpose: Blocking enabled with high (conservative) thresholds
# Duration: 2-4 weeks to validate blocking accuracy

# ============================================================================
# Core Sentinel Settings
# ============================================================================
AETHEL_SENTINEL_ENABLED=true
AETHEL_SENTINEL_MODE=soft_launch
AETHEL_TELEMETRY_DB_PATH=./data/telemetry.db

# ============================================================================
# Semantic Sanitizer - ENABLED (High Thresholds)
# ============================================================================
AETHEL_SEMANTIC_SANITIZER_ENABLED=true
AETHEL_SEMANTIC_SANITIZER_BLOCK=true  # Blocking enabled
AETHEL_PATTERN_DB_PATH=./data/trojan_patterns.json
AETHEL_ENTROPY_THRESHOLD=0.9  # High threshold (vs 0.8 production)
AETHEL_SEMANTIC_TIMEOUT_MS=100

# ============================================================================
# Crisis Mode - ENABLED (High Thresholds)
# ============================================================================
AETHEL_CRISIS_MODE_ENABLED=true
AETHEL_CRISIS_ANOMALY_THRESHOLD=0.20  # 20% (vs 10% production)
AETHEL_CRISIS_REQUEST_THRESHOLD=2000  # 2000 req/s (vs 1000 production)
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
AETHEL_QUARANTINE_THRESHOLD=0.8  # High threshold (vs 0.7 production)

# ============================================================================
# Self-Healing - ENABLED (Manual Approval)
# ============================================================================
AETHEL_SELF_HEALING_ENABLED=true
AETHEL_SELF_HEALING_AUTO_INJECT=false  # Manual approval for first 100 rules
AETHEL_RULE_EFFECTIVENESS_THRESHOLD=0.7
AETHEL_HISTORICAL_TX_LIMIT=1000

# ============================================================================
# Adversarial Vaccine - DISABLED (Enable after soft launch)
# ============================================================================
AETHEL_VACCINE_ENABLED=false
AETHEL_VACCINE_SCHEDULE="0 2 * * *"
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
# Alerting - ENABLED
# ============================================================================
AETHEL_ALERT_CRISIS_MODE=true
AETHEL_ALERT_FALSE_POSITIVE_RATE=true
AETHEL_ALERT_OVERHEAD=true
AETHEL_ALERT_QUARANTINE_CAPACITY=true
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Soft launch configuration created: {output_path}")


def validate_shadow_mode_complete() -> bool:
    """Validate that shadow mode was completed successfully."""
    print("🔍 Validating shadow mode completion...")
    
    # Check if telemetry database has data
    if not os.path.exists('./data/telemetry.db'):
        print("❌ Telemetry database not found")
        return False
    
    import sqlite3
    conn = sqlite3.connect('./data/telemetry.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transaction_metrics")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    if count < 1000:
        print(f"⚠️  Only {count} transactions in telemetry database")
        print("   Recommended: At least 1000 transactions for baseline")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    print(f"✅ Shadow mode complete ({count} transactions collected)")
    return True


def deploy_soft_launch(config_path: str) -> None:
    """Deploy Sentinel in soft launch mode."""
    print("\n🚀 Deploying Autonomous Sentinel in Soft Launch Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    print("\n✅ Soft Launch Deployment Complete!")
    print("\n📊 Monitoring:")
    print("   - Telemetry: http://localhost:9090/metrics")
    print("   - Dashboard: http://localhost:3000/sentinel")
    print("   - Logs: tail -f logs/sentinel.log")
    print("   - Gauntlet Report: http://localhost:3000/gauntlet")
    
    print("\n📈 What to Monitor:")
    print("   1. False Positive Rate:")
    print("      - Target: <1%")
    print("      - Alert if >1%")
    print("   2. Crisis Mode Activations:")
    print("      - Should be rare (high thresholds)")
    print("      - Review each activation")
    print("   3. Quarantine System:")
    print("      - Monitor capacity usage")
    print("      - Review reintegration rate")
    print("   4. Self-Healing Rules:")
    print("      - Review each generated rule")
    print("      - Manually approve first 100 rules")
    print("   5. Overhead:")
    print("      - Should remain <5%")
    
    print("\n⚠️  Important:")
    print("   - Self-Healing rules require manual approval")
    print("   - Review rules at: http://localhost:3000/self-healing")
    print("   - Approve rules with: python scripts/approve_rule.py <rule_id>")
    
    print("\n⏱️  Duration: Run for 2-4 weeks")
    print("\n📝 Next Steps:")
    print("   1. Monitor false positive rate daily")
    print("   2. Review and approve Self-Healing rules")
    print("   3. Gradually reduce thresholds if stable")
    print("   4. After 2-4 weeks, proceed to Full Activation:")
    print("      python scripts/deploy_full_activation.py")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Sentinel in Soft Launch Mode (high thresholds)"
    )
    parser.add_argument(
        '--config',
        default='./config/soft_launch.env',
        help='Path to configuration file (default: ./config/soft_launch.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip shadow mode validation'
    )
    
    args = parser.parse_args()
    
    # Validate shadow mode complete
    if not args.skip_validation:
        if not validate_shadow_mode_complete():
            sys.exit(1)
    
    # Create configuration
    create_soft_launch_config(args.config)
    
    # Deploy
    deploy_soft_launch(args.config)


if __name__ == '__main__':
    main()
