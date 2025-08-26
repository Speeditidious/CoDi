#!/bin/bash
source scripts/env.sh

python score_stat.py --out-dir $STAT_DIR \
    --gen-data-file ./outputs/generation/gen_d_gemini-2.0-flash_c_gemini-2.0-flash.json \
    --eval-data-file ./outputs/evaluation/eval_d_gemini-2.0-flash_c_gemini-2.0-flash.json \