#!/usr/bin/env python
"""Sequential test runner.

Runs each scenario on its own (with its own report) and then all scenarios
together in one sequential execution. After every execution it produces:

  * an Allure results directory  -> reports/allure-report/<stage>   (best effort)
  * a self-contained HTML report  -> reports/html/<stage>-report.html

Usage examples
--------------
    python run_tests.py                       # run every stage sequentially
    python run_tests.py --stages q1,q2        # run only Q1 and Q2
    python run_tests.py --stages all          # UI + API in one sequential run
    python run_tests.py --headed             # watch the browser
    python run_tests.py --no-allure-report   # skip `allure generate`

Stage names
-----------
    q1    UI Q1 - locked_out_user error
    q2    UI Q2 - standard_user full purchase journey
    q3    UI Q3 - performance_glitch_user sorted journey
    api   API  - ReqRes Q3/Q4/Q5/Q6/Q8
    all   All UI + API tests, run sequentially in one execution
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ALLURE_RESULTS_ROOT = os.path.join(ROOT, "allure-results")
HTML_REPORT_ROOT = os.path.join(ROOT, "reports", "html")
ALLURE_REPORT_ROOT = os.path.join(ROOT, "reports", "allure-report")

STAGES = {
    "q1": ("Q1 - Locked out user error", ["ui/tests/test_q1_locked_out_user.py"]),
    "q2": ("Q2 - Standard user purchase journey", ["ui/tests/test_q2_standard_user.py"]),
    "q3": ("Q3 - Performance glitch user journey", ["ui/tests/test_q3_performance_glitch_user.py"]),
    "api": ("API - ReqRes Q3/Q4/Q5/Q6/Q8", ["api/tests"]),
    "all": ("All scenarios (UI + API) sequentially", ["ui/tests", "api/tests"]),
}

DEFAULT_ORDER = ["q1", "q2", "q3", "api", "all"]


def find_allure() -> str | None:
    """Locate the Allure command-line binary, if installed."""
    for name in ("allure", "allure.bat", "allure.cmd"):
        path = shutil.which(name)
        if path:
            return path
    home = os.environ.get("ALLURE_HOME")
    if home:
        for name in ("allure.bat", "allure.cmd", "allure"):
            candidate = os.path.join(home, "bin", name)
            if os.path.exists(candidate):
                return candidate
    return None


def run_pytest(stage: str, targets: list[str], args: argparse.Namespace) -> int:
    allure_dir = os.path.join(ALLURE_RESULTS_ROOT, stage)
    html_report = os.path.join(HTML_REPORT_ROOT, f"{stage}-report.html")

    shutil.rmtree(allure_dir, ignore_errors=True)
    os.makedirs(allure_dir, exist_ok=True)
    os.makedirs(HTML_REPORT_ROOT, exist_ok=True)

    cmd = [
        sys.executable, "-m", "pytest", *targets,
        f"--alluredir={allure_dir}",
        f"--html={html_report}",
        "--self-contained-html",
    ]
    if args.headed:
        cmd.append("--headed")
    if args.browser:
        cmd += ["--browser", args.browser]

    print("\n" + "=" * 70)
    print(f"RUNNING STAGE: {stage} - {STAGES[stage][0]}")
    print("=" * 70)
    print("$ " + " ".join(cmd))

    result = subprocess.run(cmd, cwd=ROOT)
    print(f"\nHTML report : {html_report}")
    print(f"Allure data : {allure_dir}")
    return result.returncode


def generate_allure_report(stage: str) -> None:
    allure = find_allure()
    if not allure:
        print("Allure CLI not found - skipping the Allure HTML report "
              "(install it and re-run, or use the HTML report above).")
        return

    allure_dir = os.path.join(ALLURE_RESULTS_ROOT, stage)
    out_dir = os.path.join(ALLURE_REPORT_ROOT, stage)
    cmd = [allure, "generate", allure_dir, "-o", out_dir, "--clean"]
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT)
    print(f"Allure report: {os.path.join(out_dir, 'index.html')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the assessment test suites sequentially.")
    parser.add_argument(
        "--stages",
        default=",".join(DEFAULT_ORDER),
        help=f"Comma separated stages to run, or 'all_stages'. Default: {','.join(DEFAULT_ORDER)}",
    )
    parser.add_argument("--headed", action="store_true", help="Run UI tests with a visible browser.")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "edge"],
                        help="Browser for UI tests (default: chrome).")
    parser.add_argument("--no-allure-report", action="store_true",
                        help="Skip the `allure generate` step (still produces Allure results).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.stages.strip().lower() in {"all_stages", "everything", "all-stages"}:
        selected = list(DEFAULT_ORDER)
    else:
        selected = [s.strip() for s in args.stages.split(",") if s.strip()]

    unknown = [s for s in selected if s not in STAGES]
    if unknown:
        print(f"Unknown stage(s): {unknown}. Valid: {list(STAGES)}")
        return 2

    summary = []
    for stage in selected:
        _, targets = STAGES[stage]
        code = run_pytest(stage, targets, args)
        if not args.no_allure_report:
            generate_allure_report(stage)
        summary.append((stage, "PASS" if code == 0 else "FAIL"))

    print("\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    for stage, status in summary:
        print(f"  {stage:<6} -> {status}")
    print("=" * 70)

    return 0 if all(s == "PASS" for _, s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
