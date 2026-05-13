"""
Benchmarking utility for measuring the performance of algorithms.
This module provides a function `run_benchmarks` that can be used to execute a given algorithm, measure its execution time, and save the results in a JSON file for later analysis. The results include the algorithm name, data size, elapsed time, and an optional search key.
The `run_benchmarks` function takes the following parameters:
- `algorithm`: A string representing the name of the algorithm being benchmarked.
- `dataSize`: An integer representing the size of the data being processed by the algorithm.
- `callback`: A callable that executes the algorithm and returns its result. This allows for flexibility

"""

import json
import time
import os

from typing import Callable, Any

def run_benchmarks(algorithm: str, dataSize: int, callback: Callable[[], list[dict[str, Any]]], search_key: str | None = None) -> list[dict[str, Any]]:
    """Run the benchmarks for the specified algorithm and data size."""
    results: dict[str, str | float | int | None] = {}
    start_time = time.time()
    print(f"Running benchmark for {algorithm} with data size {dataSize}...")
    print(f"Start time: {start_time}")
    result = callback()  # Call the provided callback to execute the algorithm

    end_time = time.time()
    time_diff = end_time - start_time
    elapsed_time = round(time_diff, 4)  # Round to 4 decimal places for better readability

    results = {
        "algorithm": algorithm,
        "data_size": dataSize,
        "elapsed_time": elapsed_time,
        "search_key": search_key,
    }
    
    print(f"Benchmark completed for {algorithm} with data size {dataSize}.")
    print(f"End time: {end_time}")
    print(f"Elapsed time: {elapsed_time}")
    #Save results, create folder benchmarks if it doesn't exist
    try:
        os.makedirs("benchmarks", exist_ok=True)
        pathname = f"benchmarks/{algorithm}_results.json"
        # Load existing results and append the new one
        all_results = []
        if os.path.exists(pathname):
            with open(pathname, "r") as f:
                all_results = json.load(f)
                if not isinstance(all_results, list):
                    all_results = [all_results]
        all_results.append(results) # type: ignore
        
        with open(pathname, "w") as f:
            json.dump(all_results, f, indent=4)
            print(f"Saved benchmark results to {pathname}")
    except IOError as e:
        print(f"Error saving benchmark results: {e}")
    finally:
        # Return the result of the algorithm execution
        return result


    
    
    
    


    