#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m tools.gen_sample examples/sample_responses.json
python3 -m vqe examples/sample_responses.json --out-dir examples
python3 -m unittest discover -s tests
