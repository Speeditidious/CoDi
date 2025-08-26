#!/bin/bash
source scripts/env.sh

python score_evaluation.py --out-dir $EVAL_DIR --out-dir-stat $STAT_DIR \
    --evaluate-story-quality-ab \
    --data-file-b $DATA_FILE_PATH \
    --data-file ./outputs/generation/gen_d_gemini-2.0-flash_c_gemini-2.0-flash.json \
    --evaluator-agent-base-model gemini-1.5-pro