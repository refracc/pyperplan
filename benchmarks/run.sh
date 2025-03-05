#!/bin/bash

# Define directories
directories=(
    "parcprinter" "airport" "pegsol"
    "blocks" "psr-small" "depot"
    "rovers" "elevators" "satellite"
    "freecell" "scanalyzer" "gripper"
    "sokoban" "logistics" "tpp"
    "miconic" "transport" "movie"
    "woodworking" "zenotravel"
)

# Define heuristic configurations
heuristics=(
    "astar(lmcut())"
    "astar(ipdb())"
    "lazy_greedy([hff, hcea], preferred=[hff, hcea])"
    "lazy_greedy([hff], preferred=[hff])"
    "lazy_greedy([hcea], preferred=[hcea])"
)

# Output directory for results
output_dir="output"
mkdir -p "$output_dir"

downward_dir="downward"
if [ ! -d "$downward_dir" ]; then
    echo "🌱 Cloning Downward repository from GitHub..."
    git clone https://github.com/aibasel/downward.git "$downward_dir"

    # Change into the downward directory and run the build script
    echo "🔧 Installing Downward dependencies and building..."
    cd "$downward_dir"
    python3 build.py
    cd ..
else
    echo "✅ Downward repository already exists, skipping clone and build."
fi

# Function to run tasks for a directory
run_tasks_for_directory() {
    local dir="$1"
    echo "🌟 Processing directory: $dir 🌟"

    # Find all domain and task files in the directory
    domains=($dir/domain*.pddl)
    tasks=($dir/task*.pddl)

    if [ ${#domains[@]} -gt 0 ] && [ ${#tasks[@]} -gt 0 ]; then
        if [ ${#domains[@]} -eq 1 ]; then
            # If there is only 1 domain, pair it with all tasks in the directory
            for task_file in "${tasks[@]}" | head -n 10; do
                domain_file="${domains[0]}"  # Only one domain, so pick the first one
                for heuristic in "${heuristics[@]}"; do
                    # Define the output file path with directory name included
                    base_name=$(basename "$domain_file" .pddl)
                    task_name=$(basename "$task_file" .pddl)
                    heuristic_name=$(echo "$heuristic" | sed 's/[[:space:]]//g') # Remove spaces in heuristic name
                    output_file="$output_dir/$dir-$base_name-$task_name-$heuristic_name.txt"

                    echo "⚙️ Running domain: $domain_file, task: $task_file, heuristic: $heuristic..."

                    # Run the task and save output to the file, overwrite existing files
                    ./downward/fast-downward.py "$domain_file" "$task_file" --search "$heuristic" > "$output_file" 2>&1

                    echo "✅ Output saved to: $output_file"
                done
            done
        else
            # If there are multiple domains, pair each domain with its corresponding task
            num_domains=${#domains[@]}
            num_tasks=${#tasks[@]}

            if [ "$num_domains" -eq "$num_tasks" ]; then
                # If domains and tasks are the same count, run them in pairs
                for i in "${!domains[@]}" | head -n 10; do
                    domain_file="${domains[$i]}"
                    task_file="${tasks[$i]}"

                    for heuristic in "${heuristics[@]}"; do
                        # Define the output file path with directory name included
                        base_name=$(basename "$domain_file" .pddl)
                        task_name=$(basename "$task_file" .pddl)
                        heuristic_name=$(echo "$heuristic" | sed 's/[[:space:]]//g') # Remove spaces in heuristic name
                        output_file="$output_dir/$dir-$base_name-$task_name-$heuristic_name.txt"

                        echo "⚙️ Running domain: $domain_file, task: $task_file, heuristic: $heuristic..."

                        # Run the task and save output to the file, overwrite existing files
                        ./downward/fast-downward.py "$domain_file" "$task_file" --search "$heuristic" > "$output_file" 2>&1

                        echo "✅ Output saved to: $output_file"
                    done
                done
            else
                echo "❌ Mismatch between number of domains ($num_domains) and tasks ($num_tasks) in directory $dir"
            fi
        fi
    else
        echo "⚠️ No domain or task files found in directory $dir"
    fi
}

# Start processing directories asynchronously with a maximum of 3 at a time
export -f run_tasks_for_directory  # Make the function available for parallel execution

echo "🚀 Script execution started! Output will be saved in the $output_dir directory."

# Use GNU parallel to process up to 3 directories at the same time
parallel -j 3 run_tasks_for_directory ::: "${directories[@]}"

# Log completion message
echo "✅ All tasks completed. You can find the results in the $output_dir directory."

