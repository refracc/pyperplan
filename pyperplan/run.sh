#!/bin/bash

# Define directories to search through
directories=(
    airport depot freecell logistics movie openstacks pegsol satellite sokoban
    transport zenotravel blocks elevators gripper miconic parcprinter
    psr-small rovers scanalyzer tpp woodworking
)

# Base directory for benchmarks
benchmark_base="../benchmarks"

# Output directory for results
output_dir="./task_outputs"
mkdir -p "$output_dir"

# Heuristics and search methods
heuristics=("hadd" "hff" "hmax" "hsa" "lmcut" "landmark" "blind")
search_methods=("astar" "wastar" "gbf" "bfs" "ehs" "ids" "sat")

# Function to process a directory
process_directory() {
    local folder="$1"
    echo "Processing directory: $folder"

    # Check for 'domain.pddl'
    domain_file="$benchmark_base/$folder/domain.pddl"

    # Initialize arrays for task and domain files
    task_files=()
    domain_files=()

    # Collect taskXX.pddl files
    for task in "$benchmark_base/$folder/task"??.pddl; do
        if [[ -f "$task" ]]; then
            task_files+=("$task")
        fi
    done

    # Collect domainXX.pddl files
    for domain in "$benchmark_base/$folder/domain"??.pddl; do
        if [[ -f "$domain" ]]; then
            domain_files+=("$domain")
        fi
    done

    # Check for 'domain.pddl' and 'taskXX.pddl'
    if [[ -f "$domain_file" && ${#task_files[@]} -gt 0 ]]; then
        for task_file in "${task_files[@]}"; do
            task_num=$(basename "$task_file" | sed 's/task//;s/.pddl//')

            # Run for each heuristic and search method
            for heuristic in "${heuristics[@]}"; do
                for search_method in "${search_methods[@]}"; do
                    output_file="${output_dir}/${folder}_output_task${task_num}_h${heuristic}_s${search_method}.txt"
                    echo "Running: ./__main__.py -l debug -H $heuristic -s $search_method $domain_file $task_file"
                    ./__main__.py -l debug -H "$heuristic" -s "$search_method" "$domain_file" "$task_file" > "$output_file"
                    echo "Output saved to: $output_file"
                done
            done
        done
    else
        echo "Skipping: No valid files for 'domain.pddl' and 'taskXX.pddl' in $folder"
    fi

    # Check for 'domainXX.pddl' and 'taskXX.pddl'
    if [[ ${#domain_files[@]} -gt 0 && ${#task_files[@]} -gt 0 ]]; then
        for domain_file in "${domain_files[@]}"; do
            domain_num=$(basename "$domain_file" | sed 's/domain//;s/.pddl//')
            for task_file in "${task_files[@]}"; do
                task_num=$(basename "$task_file" | sed 's/task//;s/.pddl//')

                # Run for each heuristic and search method
                for heuristic in "${heuristics[@]}"; do
                    for search_method in "${search_methods[@]}"; do
                        output_file="${output_dir}/${folder}_output_domain${domain_num}_task${task_num}_h${heuristic}_s${search_method}.txt"
                        echo "Running: ./__main__.py -l debug -H $heuristic -s $search_method $domain_file $task_file"
                        ./__main__.py -l debug -H "$heuristic" -s "$search_method" "$domain_file" "$task_file" > "$output_file"
                        echo "Output saved to: $output_file"
                    done
                done
            done
        done
    else
        echo "Skipping: No valid files for 'domainXX.pddl' and 'taskXX.pddl' in $folder"
    fi
}

# Semaphore limit for directories
max_concurrent_dirs=5
dir_count=0

# Loop through each directory
for folder in "${directories[@]}"; do
    process_directory "$folder" &  # Run the directory processing in the background
    ((dir_count++))

    # Wait for directories to finish if we reach the limit
    if [[ $dir_count -ge $max_concurrent_dirs ]]; then
        wait -n  # Wait for any background job to finish
        ((dir_count--))
    fi
done

# Wait for any remaining background processes to finish
wait

echo "Processing complete. All outputs saved in: $output_dir"

