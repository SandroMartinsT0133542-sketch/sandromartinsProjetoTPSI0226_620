# Benchmarks Directory

The `benchmarks/` directory stores performance measurements from sorting algorithm runs. Each file contains a history of execution times for a specific sorting algorithm across different data sizes and fields.

---

## Overview

Benchmark files are created automatically when sorting records via the CLI or API. The `run_benchmarks()` utility in the utils module records:

- Algorithm name
- Data size (number of records processed)
- Execution time in seconds
- Field being sorted

**Files**:

- `bubble_results.json` – Bubble sort benchmark runs
- `insertion_results.json` – Insertion sort benchmark runs
- `merge_results.json` – Merge sort benchmark runs

---

## File Structure

Each JSON file contains an array of benchmark run objects:

```json
[
  {
    "algorithm": "bubble",
    "data_size": 15000,
    "elapsed_time": 7.9052,
    "search_key": "body_fat_pct"
  },
  {
    "algorithm": "bubble",
    "data_size": 15000,
    "elapsed_time": 8.1234,
    "search_key": "weight_kg"
  },
  {
    "algorithm": "bubble",
    "data_size": 1000,
    "elapsed_time": 0.0342,
    "search_key": "record_date"
  }
]
```

### Field Definitions

| Field          | Type   | Purpose                                | Example                              |
| -------------- | ------ | -------------------------------------- | ------------------------------------ |
| `algorithm`    | string | Name of sorting algorithm              | `"bubble"`, `"insertion"`, `"merge"` |
| `data_size`    | int    | Number of records processed            | `1000`, `15000`, `100000`            |
| `elapsed_time` | float  | Execution time in seconds (4 decimals) | `7.9052`, `0.0342`, `125.6789`       |
| `search_key`   | string | Field that was sorted (for context)    | `"weight_kg"`, `"body_fat_pct"`      |

---

## How Benchmarks Are Generated

### Manual CLI Usage

When using the CLI to sort records:

```
> Enter action: sort
> Enter field: weight
> Select algorithm: bubble
> Sort by ascending or descending? (a/d): a

Running benchmark for bubble with data size 15000...
Benchmark completed for bubble with data size 15000.
Elapsed time: 7.9052

Saved benchmark results to benchmarks/bubble_results.json
```

### Programmatic Usage

```python
from utils.benchmark import run_benchmarks
from algorithms.sorting import bubble_sort

records = [...]  # 15000 records

result = run_benchmarks(
    algorithm="bubble",
    dataSize=len(records),
    callback=lambda: bubble_sort(records, field="weight_kg", descending=False),
    search_key="weight_kg"
)

# Automatically appends to benchmarks/bubble_results.json
```

### Automatic Appending

Each benchmark run is **appended** to the existing JSON file:

1. Read existing results from file (if exists)
2. Append new result to list
3. Write entire list back to file

This preserves a complete history of all benchmark runs.

---

## Performance Analysis

### Expected Results

Based on algorithm complexity:

| Algorithm     | 1K Records | 10K Records | 100K Records | Notes                     |
| ------------- | ---------- | ----------- | ------------ | ------------------------- |
| **Bubble**    | ~0.001s    | ~0.1s       | ~10s+        | O(n²)                     |
| **Insertion** | ~0.001s    | ~0.08s      | ~8s+         | O(n²), faster than bubble |
| **Merge**     | ~0.0005s   | ~0.006s     | ~0.06s       | O(n log n), consistent    |

**Key Insights**:

- Merge sort is dramatically faster for large datasets
- Insertion sort beats bubble sort (fewer comparisons)
- All three degrade at O(n²) scale for small data
- Performance ratios grow exponentially as data size increases

### Reading Benchmark Results

```bash
# View all bubble sort benchmarks (pretty-printed)
python -c "
import json
with open('benchmarks/bubble_results.json') as f:
    data = json.load(f)
    for run in data:
        print(f\"{run['data_size']:>6} records | {run['elapsed_time']:>8.4f}s | {run['search_key']}\")
"

# Output:
# 15000 records |   7.9052s | body_fat_pct
# 15000 records |   8.1234s | weight_kg
#  1000 records |   0.0342s | record_date
```

---

## Use Cases

### 1. Algorithm Selection

When deciding which sorting algorithm to use:

```python
# Historical data shows:
# Bubble (1000 records): 0.003s
# Insertion (1000 records): 0.002s
# Merge (1000 records): 0.001s
# → Use merge for best performance

# For real-time sorting (<100 records):
# All three are <1ms, so choose insertion for simplicity
```

### 2. Performance Regression Detection

Track if changes to the sorting code make it slower:

```bash
# Before code change
$ python scripts/populate.py --count 10000
$ # Sort via CLI → generates benchmark

# After code change
$ python scripts/populate.py --count 10000
$ # Sort via CLI → generates benchmark

# Compare elapsed_time values
# If new time is 2x old time → potential regression
```

### 3. Scalability Testing

Generate benchmarks with increasing dataset sizes:

```bash
# Small dataset
python scripts/populate.py --count 1000
python src/main.py  # Sort records

# Medium dataset
python scripts/populate.py --count 10000
python src/main.py  # Sort records

# Large dataset
python scripts/populate.py --count 50000
python src/main.py  # Sort records

# Analyze growth rate in benchmarks/*.json
```

### 4. Field-Specific Performance

Different fields may sort at different speeds:

```json
// Same algorithm, same data size, different fields:
{"algorithm": "merge", "data_size": 10000, "elapsed_time": 0.0061, "search_key": "record_id"},
{"algorithm": "merge", "data_size": 10000, "elapsed_time": 0.0063, "search_key": "weight_kg"},
{"algorithm": "merge", "data_size": 10000, "elapsed_time": 0.0215, "search_key": "notes"}
```

The `notes` field is slower (string comparison vs numeric).

---

## Benchmark File Growth

Over time, each JSON file will grow as more sorting operations occur:

```
benchmarks/
├── bubble_results.json      (1 KB initially, grows with each run)
├── insertion_results.json
└── merge_results.json
```

### Management

If benchmark files grow too large:

```bash
# Clear a specific benchmark file
echo "[]" > benchmarks/bubble_results.json

# Clear all benchmarks
for f in benchmarks/*_results.json; do echo "[]" > "$f"; done

# Archive old benchmarks
cp benchmarks/bubble_results.json benchmarks/bubble_results_2026-05-14.json
echo "[]" > benchmarks/bubble_results.json
```

---

## Integration with Service Layer

The `progress_service.sort_records()` function automatically benchmarks:

```python
# In progress_service.py
def sort_records(field: str, algorithm: str, descending: bool = False, records: list[Record] | None = None) -> list[Record]:
    # ...
    if algorithm == "bubble":
        return run_benchmarks(
            "bubble",
            len(sort_space),
            lambda: bubble_sort(sort_space, field=sort_field, descending=descending),
            search_key=sort_field
        )
    # ...
```

**Transparent Benchmarking**:

- User requests sort
- Function runs algorithm
- Results are automatically recorded
- User gets sorted data (unaware of benchmarking)

---

## Data Privacy Note

Benchmark files contain **no user data**—only:

- Algorithm names
- Record counts
- Execution times
- Field names

Personal fitness data is never logged to benchmarks.

---

## Analysis Tools

### Simple Python Script

```python
import json
from pathlib import Path

def analyze_benchmark(filename):
    with open(filename) as f:
        runs = json.load(f)

    if not runs:
        print(f"No data in {filename}")
        return

    print(f"\n=== {filename} ===")
    print(f"Total runs: {len(runs)}")

    times = [run["elapsed_time"] for run in runs]
    sizes = [run["data_size"] for run in runs]

    print(f"Min time: {min(times):.4f}s")
    print(f"Max time: {max(times):.4f}s")
    print(f"Avg time: {sum(times) / len(times):.4f}s")
    print(f"Data sizes: {min(sizes)}-{max(sizes)} records")

for filename in ["benchmarks/bubble_results.json",
                 "benchmarks/insertion_results.json",
                 "benchmarks/merge_results.json"]:
    if Path(filename).exists():
        analyze_benchmark(filename)
```

### Run the Analysis

```bash
python << 'EOF'
# (paste above script)
EOF

# Output example:
# === benchmarks/bubble_results.json ===
# Total runs: 3
# Min time: 0.0342s
# Max time: 8.1234s
# Avg time: 5.3876s
# Data sizes: 1000-15000 records
```

---

## Expected vs Actual Performance

### Bubble Sort (O(n²))

```
Expected: 1000 → 10000 = 100x slower → ~100s
Actual: 1000 → 10000 = ~81x slower → ~8.1s
```

Discrepancy due to:

- CPU cache efficiency
- Modern processor optimizations
- Python interpreter variability

### Merge Sort (O(n log n))

```
Expected: 1000 → 10000 = ~3.3x slower
Actual: 1000 → 10000 = ~3.1x slower
```

Much more consistent with theoretical prediction.

---

## Troubleshooting

### Benchmark Files Not Created

**Problem**: After sorting, no benchmark file appears.

**Solutions**:

1. Check `benchmarks/` directory permissions (must be writable)
2. Check disk space (unlikely, but possible)
3. Look for error message in CLI output
4. Verify `run_benchmarks()` is being called

### Unusual Timing Values

**Problem**: One benchmark run is much slower than others (same data size).

**Causes**:

- Other processes running (system load)
- Disk I/O blocking
- Python garbage collection paused during sort
- Thermal throttling (CPU too hot)

**Normal Variation**: ±10% is expected; >30% suggests external factors.

---

## Notes

- Benchmark times include algorithm execution only (not I/O, not UI)
- Times are in seconds, rounded to 4 decimal places
- Benchmark runs are **cumulative** (appended, not replaced)
- No automatic cleanup of old benchmark data
- Can be safely deleted/reset without affecting application
