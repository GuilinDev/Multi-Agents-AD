#!/usr/bin/env bash
# CareLoop Multi-Model Ablation Experiments
# 4 models × 3 shifts = 12 runs
# Results saved to simulation/evaluation/experiments/

set -euo pipefail

PROJECT_DIR="/home/guilinzhang/allProjects/memowell-ai"
API_DIR="$PROJECT_DIR/api"
RESULTS_DIR="$PROJECT_DIR/simulation/evaluation/experiments"
API_LOG="/tmp/careloop-api.log"
EXPERIMENT_LOG="$RESULTS_DIR/experiment_log.txt"

MODELS=(
    "nemotron-3-nano:30b"
    "qwen3.5:27b"
    "deepseek-r1:32b"
    "mistral-small3.2:24b"
)

MODEL_SLUGS=(
    "nemotron"
    "qwen35"
    "deepseek-r1"
    "mistral"
)

SHIFTS=("day" "evening" "night")

mkdir -p "$RESULTS_DIR"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$EXPERIMENT_LOG"
}

start_api() {
    local model="$1"
    # Kill any existing API
    pkill -f "python3.*main.py" 2>/dev/null || true
    sleep 2

    cd "$API_DIR"
    LLM_PROVIDER=ollama LLM_MODEL="$model" nohup python3 -u main.py > "$API_LOG" 2>&1 &
    local api_pid=$!
    echo "$api_pid"

    # Wait for API to be ready
    for i in {1..15}; do
        if curl -s http://localhost:8000/api/health | grep -q '"ok"'; then
            log "API ready (PID=$api_pid, model=$model)"
            return 0
        fi
        sleep 2
    done
    log "ERROR: API failed to start for model=$model"
    return 1
}

run_single() {
    local model="$1"
    local model_slug="$2"
    local shift="$3"
    local run_id="${model_slug}_${shift}"
    local output_dir="$RESULTS_DIR/$run_id"
    local report_file="$output_dir/report.json"
    local sim_log="$output_dir/simulation.log"

    mkdir -p "$output_dir"

    # Check if already completed
    if [[ -f "$report_file" ]]; then
        log "SKIP: $run_id already completed"
        return 0
    fi

    log "START: $run_id (model=$model, shift=$shift)"
    local start_time=$(date +%s)

    # Run simulation
    cd "$PROJECT_DIR"
    LLM_PROVIDER=ollama LLM_MODEL="$model" \
        python3 -u -m simulation.run_simulation \
        --shift "$shift" \
        --api-url http://localhost:8000 \
        > "$sim_log" 2>&1

    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$(( end_time - start_time ))

    if [[ $exit_code -eq 0 ]]; then
        # Copy the latest report
        local latest="$PROJECT_DIR/simulation/evaluation/latest_report.json"
        if [[ -f "$latest" ]]; then
            cp "$latest" "$report_file"
        fi
        log "DONE: $run_id — ${duration}s ($(( duration / 60 ))m)"
    else
        log "FAIL: $run_id — exit=$exit_code after ${duration}s"
    fi

    # Save API log for this run
    cp "$API_LOG" "$output_dir/api.log" 2>/dev/null || true

    # Save metadata
    cat > "$output_dir/metadata.json" << EOF
{
    "model": "$model",
    "model_slug": "$model_slug",
    "shift": "$shift",
    "run_id": "$run_id",
    "duration_seconds": $duration,
    "exit_code": $exit_code,
    "timestamp": "$(date -Iseconds)",
    "ollama_version": "$(ollama --version 2>/dev/null || echo unknown)"
}
EOF
}

# ============================================================
# MAIN
# ============================================================

log "=========================================="
log "CARELOOP ABLATION EXPERIMENTS — START"
log "Models: ${MODELS[*]}"
log "Shifts: ${SHIFTS[*]}"
log "Total runs: $(( ${#MODELS[@]} * ${#SHIFTS[@]} ))"
log "=========================================="

total_start=$(date +%s)
completed=0
failed=0

for i in "${!MODELS[@]}"; do
    model="${MODELS[$i]}"
    slug="${MODEL_SLUGS[$i]}"

    log "--- Loading model: $model ---"

    # Start API with this model
    if ! start_api "$model"; then
        log "FATAL: Cannot start API for $model, skipping"
        failed=$(( failed + 3 ))
        continue
    fi

    # Warm up the model with a dummy request
    log "Warming up $model..."
    curl -s http://localhost:11434/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":10}" \
        > /dev/null 2>&1 || true
    sleep 2

    for shift in "${SHIFTS[@]}"; do
        run_single "$model" "$slug" "$shift"
        if [[ $? -eq 0 ]]; then
            completed=$(( completed + 1 ))
        else
            failed=$(( failed + 1 ))
        fi

        # Brief pause between runs
        sleep 5
    done

    log "--- Completed all shifts for $model ---"
done

total_end=$(date +%s)
total_duration=$(( total_end - total_start ))

log "=========================================="
log "EXPERIMENTS COMPLETE"
log "Completed: $completed / $(( ${#MODELS[@]} * ${#SHIFTS[@]} ))"
log "Failed: $failed"
log "Total time: ${total_duration}s ($(( total_duration / 60 ))m)"
log "Results: $RESULTS_DIR"
log "=========================================="

# Generate summary
log "Generating summary..."
cd "$PROJECT_DIR"
python3 -c "
import json, os, glob

results_dir = '$RESULTS_DIR'
summary = []
for d in sorted(glob.glob(f'{results_dir}/*/metadata.json')):
    with open(d) as f:
        meta = json.load(f)
    report_path = os.path.join(os.path.dirname(d), 'report.json')
    if os.path.exists(report_path):
        with open(report_path) as f:
            report = json.load(f)
        meta['avg_score'] = report.get('avg_score', 0)
        meta['total_events'] = report.get('total_events', 0)
        meta['issues_count'] = len(report.get('issues', []))
    summary.append(meta)

with open(f'{results_dir}/summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('Model | Shift | Duration | Avg Score | Events | Issues')
print('-' * 65)
for s in summary:
    print(f\"{s['model_slug']:>10} | {s['shift']:>7} | {s['duration_seconds']:>6}s | {s.get('avg_score','N/A'):>9} | {s.get('total_events','N/A'):>6} | {s.get('issues_count','N/A'):>6}\")
" >> "$EXPERIMENT_LOG" 2>&1

log "All done. Check $RESULTS_DIR for results."
