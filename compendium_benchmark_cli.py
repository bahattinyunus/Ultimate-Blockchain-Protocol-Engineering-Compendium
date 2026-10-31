#!/usr/bin/env python3
"""
Ultimate Blockchain & Protocol Engineering Compendium - Unified Benchmark & Verification CLI
Discovers, benchmarks, and verifies all cryptographic, consensus, VM, rollup, and MEV simulators.
"""

import argparse
import glob
import os
import subprocess
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_benchmark(filter_pattern: str = ""):
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}⚡ ULTIMATE BLOCKCHAIN & PROTOCOL ENGINEERING COMPENDIUM BENCHMARK CLI ⚡{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")

    all_scripts = sorted(glob.glob("modules/**/*.py", recursive=True))
    if filter_pattern:
        scripts = [s for s in all_scripts if filter_pattern.lower() in s.lower()]
    else:
        scripts = all_scripts

    print(f"{BOLD}Discovered {len(scripts)} protocol simulation engines across 15 engineering modules.{RESET}\n")

    results = []
    total_start = time.perf_counter()

    for idx, script in enumerate(scripts, 1):
        rel_path = os.path.relpath(script)
        parts = rel_path.split(os.sep)
        module_name = parts[1] if len(parts) > 1 else "root"
        script_name = parts[-1]

        print(f"[{idx:02d}/{len(scripts):02d}] Running {BOLD}{script_name}{RESET} ({module_name})... ", end="", flush=True)

        start_time = time.perf_counter()
        proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if proc.returncode == 0:
            print(f"{GREEN}{BOLD}PASS{RESET} ({elapsed_ms:6.1f} ms)")
            results.append((module_name, script_name, "PASS", elapsed_ms, None))
        else:
            print(f"{RED}{BOLD}FAIL{RESET} ({elapsed_ms:6.1f} ms)")
            results.append((module_name, script_name, "FAIL", elapsed_ms, proc.stderr))

    total_time = (time.perf_counter() - total_start) * 1000.0

    # Summary Table
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{'MODULE / CATEGORY':<35} | {'SIMULATION SCRIPT':<32} | {'RESULT':<6} | {'TIME'}{RESET}")
    print(f"{'-'*80}")
    passed_count = sum(1 for r in results if r[2] == "PASS")

    for mod, scr, res, ms, _ in results:
        res_color = GREEN if res == "PASS" else RED
        print(f"{mod:<35} | {scr:<32} | {res_color}{res:<6}{RESET} | {ms:6.1f} ms")

    print(f"{'='*80}")
    print(f"{BOLD}Total Protocol Suites: {len(results)} | Passed: {GREEN}{passed_count}{RESET} | Failed: {RED if (len(results) - passed_count) > 0 else GREEN}{len(results) - passed_count}{RESET} | Total Execution: {total_time:.1f} ms{RESET}\n")

    if passed_count < len(results):
        print(f"{RED}{BOLD}Errors detected in the following simulations:{RESET}")
        for mod, scr, res, ms, err in results:
            if res == "FAIL":
                print(f"\n--- {scr} ({mod}) ---")
                print(err)
        sys.exit(1)
    else:
        print(f"{GREEN}{BOLD}✨ ALL PROTOCOL ENGINEERING SIMULATORS VERIFIED WITH ZERO ERRORS! ✨{RESET}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blockchain Protocol Engineering Benchmark CLI")
    parser.add_argument("--filter", "-f", default="", help="Filter scripts by name or module substring")
    args = parser.parse_args()

    run_benchmark(args.filter)
