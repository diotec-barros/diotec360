"""
Benchmark Script: Semantic Sanitizer Latency Analysis

This script measures the performance of the Semantic Sanitizer components:
1. AST parsing latency
2. Entropy calculation latency
3. Pattern matching latency
4. Overall analysis latency

Target: Analysis should complete within 100ms per transaction

Validates: Requirements 10.2
Property 52: Semantic analysis latency
"""

import time
import json
import statistics
from typing import List, Dict, Any
from pathlib import Path

from aethel.core.semantic_sanitizer import SemanticSanitizer


# Test code samples of varying complexity
TEST_SAMPLES = {
    "simple": """
def transfer(from_account, to_account, amount):
    if amount > 0:
        from_account.balance -= amount
        to_account.balance += amount
    return True
""",
    
    "medium": """
def process_batch(transactions):
    results = []
    for tx in transactions:
        if tx.amount > 0 and tx.from_account.balance >= tx.amount:
            tx.from_account.balance -= tx.amount
            tx.to_account.balance += tx.amount
            results.append({"status": "success", "tx_id": tx.id})
        else:
            results.append({"status": "failed", "tx_id": tx.id})
    return results
""",
    
    "complex": """
def recursive_validator(state, depth=0):
    if depth > 100:
        return False
    
    if state.is_valid():
        return True
    
    for child in state.children:
        if recursive_validator(child, depth + 1):
            return True
    
    return False

def nested_processor(data):
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested = {}
            for k, v in value.items():
                if isinstance(v, list):
                    processed = []
                    for item in v:
                        if isinstance(item, dict):
                            processed.append({k: v for k, v in item.items() if v is not None})
                        else:
                            processed.append(item)
                    nested[k] = processed
                else:
                    nested[k] = v
            result[key] = nested
        else:
            result[key] = value
    return result
""",
    
    "high_entropy": """
def xf7g2k(a9b3c, d4e5f):
    z8y7x = []
    for i1j2k in range(a9b3c):
        m3n4o = d4e5f * i1j2k
        p5q6r = m3n4o + i1j2k
        s7t8u = p5q6r ** 2
        z8y7x.append(s7t8u)
    return z8y7x
""",
    
    "malicious_infinite_loop": """
def attack():
    while True:
        balance -= 1
""",
    
    "malicious_recursion": """
def recursive_bomb(n):
    return recursive_bomb(n + 1)
""",
    
    "large_function": """
def large_processor(data):
    step1 = data.get("field1", 0)
    step2 = data.get("field2", 0)
    step3 = data.get("field3", 0)
    step4 = data.get("field4", 0)
    step5 = data.get("field5", 0)
    
    if step1 > 0:
        result1 = step1 * 2
    else:
        result1 = 0
    
    if step2 > 0:
        result2 = step2 * 3
    else:
        result2 = 0
    
    if step3 > 0:
        result3 = step3 * 4
    else:
        result3 = 0
    
    if step4 > 0:
        result4 = step4 * 5
    else:
        result4 = 0
    
    if step5 > 0:
        result5 = step5 * 6
    else:
        result5 = 0
    
    total = result1 + result2 + result3 + result4 + result5
    
    if total > 100:
        return {"status": "high", "value": total}
    elif total > 50:
        return {"status": "medium", "value": total}
    else:
        return {"status": "low", "value": total}
"""
}


def benchmark_ast_parsing(sanitizer: SemanticSanitizer, iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark AST parsing performance
    
    Args:
        sanitizer: Semantic Sanitizer instance
        iterations: Number of iterations per sample
    
    Returns:
        Benchmark results
    """
    print("\n=== Benchmarking AST Parsing ===")
    results = {}
    
    for name, code in TEST_SAMPLES.items():
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                sanitizer._parse_ast(code)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"Error parsing {name}: {e}")
                continue
        
        if times:
            results[name] = {
                "mean_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "iterations": len(times)
            }
            
            print(f"{name:30s}: {results[name]['mean_ms']:6.3f}ms (median: {results[name]['median_ms']:6.3f}ms)")
    
    return results


def benchmark_entropy_calculation(sanitizer: SemanticSanitizer, iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark entropy calculation performance
    
    Args:
        sanitizer: Semantic Sanitizer instance
        iterations: Number of iterations per sample
    
    Returns:
        Benchmark results
    """
    print("\n=== Benchmarking Entropy Calculation ===")
    results = {}
    
    for name, code in TEST_SAMPLES.items():
        times = []
        
        # Pre-parse AST
        try:
            ast_tree = sanitizer._parse_ast(code)
        except:
            continue
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                sanitizer._calculate_entropy(ast_tree, code)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"Error calculating entropy for {name}: {e}")
                continue
        
        if times:
            results[name] = {
                "mean_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "iterations": len(times)
            }
            
            print(f"{name:30s}: {results[name]['mean_ms']:6.3f}ms (median: {results[name]['median_ms']:6.3f}ms)")
    
    return results


def benchmark_pattern_matching(sanitizer: SemanticSanitizer, iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark pattern matching performance
    
    Args:
        sanitizer: Semantic Sanitizer instance
        iterations: Number of iterations per sample
    
    Returns:
        Benchmark results
    """
    print("\n=== Benchmarking Pattern Matching ===")
    results = {}
    
    for name, code in TEST_SAMPLES.items():
        times = []
        
        # Pre-parse AST
        try:
            ast_tree = sanitizer._parse_ast(code)
        except:
            continue
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                sanitizer._detect_patterns(ast_tree, code)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"Error detecting patterns for {name}: {e}")
                continue
        
        if times:
            results[name] = {
                "mean_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "iterations": len(times)
            }
            
            print(f"{name:30s}: {results[name]['mean_ms']:6.3f}ms (median: {results[name]['median_ms']:6.3f}ms)")
    
    return results


def benchmark_overall_analysis(sanitizer: SemanticSanitizer, iterations: int = 100) -> Dict[str, Any]:
    """
    Benchmark overall analysis performance (end-to-end)
    
    Args:
        sanitizer: Semantic Sanitizer instance
        iterations: Number of iterations per sample
    
    Returns:
        Benchmark results
    """
    print("\n=== Benchmarking Overall Analysis (End-to-End) ===")
    results = {}
    
    for name, code in TEST_SAMPLES.items():
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                sanitizer.analyze(code)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"Error analyzing {name}: {e}")
                continue
        
        if times:
            results[name] = {
                "mean_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "iterations": len(times),
                "meets_target": statistics.mean(times) < 100.0  # Target: <100ms
            }
            
            status = "✓ PASS" if results[name]['meets_target'] else "✗ FAIL"
            print(f"{name:30s}: {results[name]['mean_ms']:6.3f}ms (median: {results[name]['median_ms']:6.3f}ms) {status}")
    
    return results


def analyze_bottlenecks(ast_results: Dict, entropy_results: Dict, 
                       pattern_results: Dict, overall_results: Dict) -> Dict[str, Any]:
    """
    Analyze which component is the bottleneck
    
    Args:
        ast_results: AST parsing benchmark results
        entropy_results: Entropy calculation benchmark results
        pattern_results: Pattern matching benchmark results
        overall_results: Overall analysis benchmark results
    
    Returns:
        Bottleneck analysis
    """
    print("\n=== Bottleneck Analysis ===")
    
    analysis = {}
    
    for name in TEST_SAMPLES.keys():
        if name not in overall_results:
            continue
        
        ast_time = ast_results.get(name, {}).get("mean_ms", 0)
        entropy_time = entropy_results.get(name, {}).get("mean_ms", 0)
        pattern_time = pattern_results.get(name, {}).get("mean_ms", 0)
        overall_time = overall_results[name]["mean_ms"]
        
        # Calculate component percentages
        total_measured = ast_time + entropy_time + pattern_time
        overhead = overall_time - total_measured
        
        analysis[name] = {
            "overall_ms": overall_time,
            "ast_parsing_ms": ast_time,
            "entropy_calc_ms": entropy_time,
            "pattern_match_ms": pattern_time,
            "overhead_ms": overhead,
            "ast_percent": (ast_time / overall_time * 100) if overall_time > 0 else 0,
            "entropy_percent": (entropy_time / overall_time * 100) if overall_time > 0 else 0,
            "pattern_percent": (pattern_time / overall_time * 100) if overall_time > 0 else 0,
            "overhead_percent": (overhead / overall_time * 100) if overall_time > 0 else 0
        }
        
        print(f"\n{name}:")
        print(f"  Overall:        {overall_time:6.3f}ms (100.0%)")
        print(f"  AST Parsing:    {ast_time:6.3f}ms ({analysis[name]['ast_percent']:5.1f}%)")
        print(f"  Entropy Calc:   {entropy_time:6.3f}ms ({analysis[name]['entropy_percent']:5.1f}%)")
        print(f"  Pattern Match:  {pattern_time:6.3f}ms ({analysis[name]['pattern_percent']:5.1f}%)")
        print(f"  Overhead:       {overhead:6.3f}ms ({analysis[name]['overhead_percent']:5.1f}%)")
    
    return analysis


def generate_summary(overall_results: Dict[str, Any], bottleneck_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary report
    
    Args:
        overall_results: Overall analysis benchmark results
        bottleneck_analysis: Bottleneck analysis results
    
    Returns:
        Summary report
    """
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    # Calculate aggregate statistics
    all_times = [r["mean_ms"] for r in overall_results.values()]
    passing = sum(1 for r in overall_results.values() if r["meets_target"])
    total = len(overall_results)
    
    summary = {
        "target_latency_ms": 100.0,
        "tests_passing": passing,
        "tests_total": total,
        "pass_rate_percent": (passing / total * 100) if total > 0 else 0,
        "mean_latency_ms": statistics.mean(all_times) if all_times else 0,
        "median_latency_ms": statistics.median(all_times) if all_times else 0,
        "max_latency_ms": max(all_times) if all_times else 0,
        "min_latency_ms": min(all_times) if all_times else 0,
        "meets_requirement": all(r["meets_target"] for r in overall_results.values())
    }
    
    print(f"\nTarget Latency:     {summary['target_latency_ms']:.1f}ms")
    print(f"Tests Passing:      {summary['tests_passing']}/{summary['tests_total']} ({summary['pass_rate_percent']:.1f}%)")
    print(f"Mean Latency:       {summary['mean_latency_ms']:.3f}ms")
    print(f"Median Latency:     {summary['median_latency_ms']:.3f}ms")
    print(f"Min Latency:        {summary['min_latency_ms']:.3f}ms")
    print(f"Max Latency:        {summary['max_latency_ms']:.3f}ms")
    
    if summary['meets_requirement']:
        print("\n✓ REQUIREMENT MET: All samples analyzed within 100ms")
    else:
        print("\n✗ REQUIREMENT NOT MET: Some samples exceed 100ms")
        print("\nSamples exceeding target:")
        for name, result in overall_results.items():
            if not result["meets_target"]:
                print(f"  - {name}: {result['mean_ms']:.3f}ms")
    
    # Identify primary bottleneck across all samples
    bottleneck_components = {"ast": 0, "entropy": 0, "pattern": 0, "overhead": 0}
    for analysis in bottleneck_analysis.values():
        max_component = max(
            [("ast", analysis["ast_percent"]),
             ("entropy", analysis["entropy_percent"]),
             ("pattern", analysis["pattern_percent"]),
             ("overhead", analysis["overhead_percent"])],
            key=lambda x: x[1]
        )
        bottleneck_components[max_component[0]] += 1
    
    primary_bottleneck = max(bottleneck_components.items(), key=lambda x: x[1])
    
    print(f"\nPrimary Bottleneck: {primary_bottleneck[0].upper()} ({primary_bottleneck[1]}/{total} samples)")
    
    summary["primary_bottleneck"] = primary_bottleneck[0]
    summary["bottleneck_count"] = primary_bottleneck[1]
    
    return summary


def save_results(results: Dict[str, Any], output_path: str = "benchmark_semantic_sanitizer_results.json"):
    """
    Save benchmark results to JSON file
    
    Args:
        results: Complete benchmark results
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")


def main():
    """Run complete benchmark suite"""
    print("="*70)
    print("SEMANTIC SANITIZER LATENCY BENCHMARK")
    print("="*70)
    print(f"\nTarget: Analysis should complete within 100ms")
    print(f"Iterations per sample: 100")
    print(f"Test samples: {len(TEST_SAMPLES)}")
    
    # Initialize sanitizer
    sanitizer = SemanticSanitizer(pattern_db_path="data/trojan_patterns.json")
    
    # Run benchmarks
    ast_results = benchmark_ast_parsing(sanitizer, iterations=100)
    entropy_results = benchmark_entropy_calculation(sanitizer, iterations=100)
    pattern_results = benchmark_pattern_matching(sanitizer, iterations=100)
    overall_results = benchmark_overall_analysis(sanitizer, iterations=100)
    
    # Analyze bottlenecks
    bottleneck_analysis = analyze_bottlenecks(ast_results, entropy_results, 
                                              pattern_results, overall_results)
    
    # Generate summary
    summary = generate_summary(overall_results, bottleneck_analysis)
    
    # Save results
    results = {
        "summary": summary,
        "ast_parsing": ast_results,
        "entropy_calculation": entropy_results,
        "pattern_matching": pattern_results,
        "overall_analysis": overall_results,
        "bottleneck_analysis": bottleneck_analysis,
        "timestamp": time.time()
    }
    
    save_results(results)
    
    print("\n" + "="*70)
    print("BENCHMARK COMPLETE")
    print("="*70)
    
    return summary["meets_requirement"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
