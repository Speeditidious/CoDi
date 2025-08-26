#!/bin/bash
source scripts/env.sh

python generation.py --data-file $DATA_FILE_PATH --out-dir $GEN_DIR \
    --planner-agent-base-model gpt-4o-2024-11-20 --director-agent-base-model gemini-2.0-flash --character-agent-base-model gemini-2.0-flash --editor-agent-base-model gemini-2.0-flash