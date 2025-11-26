"""
COMP-5700 Exercise 15: Pairwise Testing
Author: Jacob Murrah
Date: 12/2/2025
"""

from collections import OrderedDict
from allpairspy import AllPairs

from pathlib import Path
import subprocess
import json

CPPCHECK_FLAGS = OrderedDict(
    {
        "enable": [
            "all",
            "warning",
            "style",
            "performance",
            "portability",
            "information",
            "unusedFunction",
            "missingInclude",
        ],
        "std": ["c89", "c99", "c11", "c++03", "c++11", "c++14", "c++17", "c++20"],
        "platform": [
            "unix32",
            "unix64",
            "win32A",
            "win32W",
            "win64",
            "avr6",
            "elbrus-e1cp",
            "pic8",
            "pic8-enhanced",
            "pic16",
            "mips32",
            "native",
            "unspecified",
        ],
    }
)
RESULTS_DIR = Path("cppcheck-results")


def run_cppcheck_case(id, pair) -> dict[str, str]:
    command = [
        "cppcheck",
        "--enable=" + pair.enable,
        "--std=" + pair.std,
        "--platform=" + pair.platform,
        "HPC-Compiler-Fuzzers",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    record = {
        "id": id,
        "flags": pair,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / f"pair_{id}.txt").write_text(
        "\n".join(
            [
                f"CASE {id}",
                f"Command : {' '.join(command)}",
                f"Return  : {completed.returncode}",
                "--- STDOUT ---",
                completed.stdout.strip(),
                "--- STDERR ---",
                completed.stderr.strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )

    return record


if __name__ == "__main__":
    print("PAIRWISE:")
    for i, pairs in enumerate(AllPairs(CPPCHECK_FLAGS)):
        print("{:2d}: {}".format(i, pairs))

    all_records = []
    for i, pair in enumerate(AllPairs(CPPCHECK_FLAGS)):
        record = run_cppcheck_case(i, pair)
        all_records.append(record)

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(all_records, indent=2), encoding="utf-8")
    print(f"\nRecorded {len(all_records)} executions in '{RESULTS_DIR}'.")
    print(f"Summary JSON written to '{summary_path}'.")
