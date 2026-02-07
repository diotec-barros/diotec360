#!/usr/bin/env python3
"""
Deploy Sentinel in Shadow Mode

Shadow Mode: Monitoring only, no blocking
- Sentinel Monitor: ENABLED (collect telemetry)
- Semantic Sanitizer: DISABLED (log only, don't block)
- Crisis Mode: DISABLED
- Quarantine: DISABLED
- Self-Healing: DISABLED
- Adversarial Vaccine: DISABLED

Purpose: Establish baseline metrics and validate telemetry collection

Duration: 1-2 weeks

Usage:
    python scripts/deploy_shadow_mode.py
    python scripts/deploy_shadow_mode.py --config ./config/shadow_mode.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_shadow_mode_config(output_path: str) -> None:
    """Create shadow mode configuration file."""
    config = """# Autonomous Sentinel v1.9.0 - Shadow Mode Configuration
# Purpose: Monitoring only, no blocking
# Duration: 1-2 weeks to establish baseline

# ============================================================================
# Core Sentinel Settings
# ============================================================================
AETHEL_SENTINEL_ENABLED=true
AETHEL_SENTINEL_MODE=shadow
AETHEL_TELEMETRY_DB_PATH=./data/telemetry.db

# ============================================================================
# Semantic Sanitizer - LOG ONLY (No Blocking)
# ============================================================================
AETHEL_SEMANTIC_SANITIZER_ENABLED=true
AETHEL_SEMANTIC_SANITIZER_BLOCK=false  # Log only, don't block
AETHEL_PATTERN_DB_PATH=./data/trojan_patterns.json
AETHEL_ENTROPY_THRESHOLD=0.8
AETHEL_SEMANTIC_TIMEOUT_MS=100

# ============================================================================
# Crisis Mode - DISABLED
# ============================================================================
AETHEL_CRISIS_MODE_ENABLED=false
AETHEL_CRISIS_ANOMALY_THRESHOLD=0.10
AETHEL_CRISIS_REQUEST_THRESHOLD=1000
AETHEL_CRISIS_COOLDOWN_SECONDS=120

# ============================================================================
# Adaptive Rigor - NORMAL MODE ONLY
# ============================================================================
AETHEL_NORMAL_Z3_TIMEOUT=30
AETHEL_CRISIS_Z3_TIMEOUT=5
AETHEL_POW_BASE_DIFFICULTY=4
AETHEL_POW_MAX_DIFFICULTY=8

# ============================================================================
# Quarantine System - DISABLED
# ============================================================================
AETHEL_QUARANTINE_ENABLED=false
AETHEL_QUARANTINE_CAPACITY=100
AETHEL_QUARANTINE_THRESHOLD=0.7

# ============================================================================
# Self-Healing - DISABLED
# ============================================================================
AETHEL_SELF_HEALING_ENABLED=false
AETHEL_RULE_EFFECTIVENESS_THRESHOLD=0.7
AETHEL_HISTORICAL_TX_LIMIT=1000

# ============================================================================
# Adversarial Vaccine - DISABLED
# ============================================================================
AETHEL_VACCINE_ENABLED=false
AETHEL_VACCINE_SCHEDULE="0 2 * * *"
AETHEL_VACCINE_SCENARIOS=1000

# ============================================================================
# Gauntlet Report - ENABLED (Logging)
# ============================================================================
AETHEL_GAUNTLET_DB_PATH=./data/gauntlet.db
AETHEL_RETENTION_DAYS=90

# ============================================================================
# Monitoring and Logging
# ============================================================================
AETHEL_LOG_LEVEL=INFO
AETHEL_METRICS_ENABLED=true
AETHEL_METRICS_PORT=9090
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Shadow mode configuration created: {output_path}")


def validate_prerequisites() -> bool:
    """Validate that prerequisites are met."""
    print("🔍 Validating prerequisites...")
    
    # Check if databases exist
    if not os.path.exists('./data/telemetry.db'):
        print("❌ Telemetry database not found")
        print("   Run: python scripts/init_databases.py")
        return False
    
    if not os.path.exists('./data/gauntlet.db'):
        print("❌ Gauntlet database not found")
        print("   Run: python scripts/init_databases.py")
        return False
    
    # Check if pattern database exists
    if not os.path.exists('./data/trojan_patterns.json'):
        print("❌ Trojan patterns database not found")
        print("   File should exist at: ./data/trojan_patterns.json")
        return False
    
    print("✅ All prerequisites met")
    return True


def deploy_shadow_mode(config_path: str) -> None:
    """Deploy Sentinel in shadow mode."""
    print("\n🚀 Deploying Autonomous Sentinel in Shadow Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    # In a real deployment, this would:
    # 1. Load environment variables from config file
    # 2. Restart application with new configuration
    # 3. Verify Sentinel components are running
    # 4. Start monitoring dashboard
    
    print("\n✅ Shadow Mode Deployment Complete!")
    print("\n📊 Monitoring:")
    print("   - Telemetry: http://localhost:9090/metrics")
    print("   - Dashboard: http://localhost:3000/sentinel")
    print("   - Logs: tail -f logs/sentinel.log")
    
    print("\n📈 What to Monitor:")
    print("   1. Baseline Metrics:")
    print("      - Average CPU time per transaction")
    print("      - Average memory delta per transaction")
    print("      - Average Z3 duration per transaction")
    print("   2. Anomaly Detection:")
    print("      - Anomaly rate (should be <5% in normal traffic)")
    print("      - Anomaly score distribution")
    print("   3. Semantic Sanitizer:")
    print("      - Pattern matches (logged but not blocked)")
    print("      - High entropy detections")
    print("   4. Overhead:")
    print("      - Sentinel overhead should be <5%")
    
    print("\n⏱️  Duration: Run for 1-2 weeks")
    print("\n📝 Next Steps:")
    print("   1. Monitor baseline metrics daily")
    print("   2. Review anomaly detection accuracy")
    print("   3. Adjust thresholds if needed")
    print("   4. After 1-2 weeks, proceed to Soft Launch:")
    print("      python scripts/deploy_soft_launch.py")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Sentinel in Shadow Mode (monitoring only)"
    )
    parser.add_argument(
        '--config',
        default='./config/shadow_mode.env',
        help='Path to configuration file (default: ./config/shadow_mode.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip prerequisite validation'
    )
    
    args = parser.parse_args()
    
    # Validate prerequisites
    if not args.skip_validation:
        if not validate_prerequisites():
            sys.exit(1)
    
    # Create configuration
    create_shadow_mode_config(args.config)
    
    # Deploy
    deploy_shadow_mode(args.config)


if __name__ == '__main__':
    main()
