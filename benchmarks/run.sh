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

    echo "🔧 Installing Downward dependencies and building..."
    cd "$downward_dir"
    python3 build.py
    cd ..
else
    echo "✅ Downward repository already exists, skipping clone and build."
fi

run_tasks_for_directory() {
    local dir="$1"
    echo "🌟 Processing directory: $dir 🌟"

    mapfile -t domains < <(find "$dir" -maxdepth 1 -name 'domain*.pddl' | sort)
    mapfile -t tasks < <(find "$dir" -maxdepth 1 -name 'task*.pddl' | sort)

    if [ ${#domains[@]} -gt 0 ] && [ ${#tasks[@]} -gt 0 ]; then
        if [ ${#domains[@]} -eq 1 ]; then
            for task_file in "${tasks[@]:0:10}"; do
                domain_file="${domains[0]}"
                for heuristic in "${heuristics[@]}"; do
                    base_name=$(basename "$domain_file" .pddl)
                    task_name=$(basename "$task_file" .pddl)
                    heuristic_name=$(echo "$heuristic" | sed 's/[[:space:]]//g')
                    output_file="$output_dir/$dir-$base_name-$task_name-$heuristic_name.txt"
                    sas_file="$output_dir/$dir-$base_name-$task_name-$heuristic_name-output.sas"

                    # Create a unique directory for each task
                    task_output_dir="$output_dir/$dir-$base_name-$task_name-$heuristic_name"
                    mkdir -p "$task_output_dir"

                    echo "⚙️ Running domain: $domain_file, task: $task_file, heuristic: $heuristic..."
                    ./downward/fast-downward.py "$domain_file" "$task_file" --search "$heuristic" --sas-file "$sas_file" > "$output_file" 2>&1 &
                done
            done
        fi
        wait
    else
        echo "⚠️ No domain or task files found in directory $dir"
    fi
}

# Parallel execution in batches of 3
echo "🚀 Starting parallel execution..."

parallel_jobs=()

for dir in "${directories[@]}"; do
    run_tasks_for_directory "$dir" &
    parallel_jobs+=("$!")

    if [ ${#parallel_jobs[@]} -eq 3 ]; then
        wait "${parallel_jobs[@]}"
        parallel_jobs=()
    fi
done

wait "${parallel_jobs[@]}"
