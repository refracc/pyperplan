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

# Collect statistics
input_directory="$output_dir"
output_file="./collected.csv"

# Define CSV header with all possible stats
header="File,Domain,Problem,Heuristic,Translator rules,Relevant atoms,Auxiliary atoms,Final queue length,Total queue pushes,Translator variables,Translator derived variables,Translator facts,Translator goal facts,Translator mutex groups,Translator total mutex groups size,Translator operators,Translator axioms,Translator task size,Translator peak memory,Search time,Total time,Canonical PDB heuristic number of patterns,Canonical PDB heuristic total PDB size,Canonical PDB heuristic computation time,Hill climbing iterations,Hill climbing generated patterns,Hill climbing rejected patterns,Hill climbing maximum PDB size,Hill climbing time,Hill climbing pattern collection generator number of patterns,Hill climbing pattern collection generator total PDB size,Hill climbing pattern collection generator computation time,Dominance pruning pruned pattern cliques,Dominance pruning pruned PDBs,Dominance pruning time,Successor generator peak memory difference,Successor generator creation time,Variables,FactPairs,Bytes per state"
echo "$header" > "$output_file"

for file in "$input_directory"/*.txt; do
    filename=$(basename "$file")
    domain=$(echo "$filename" | cut -d'-' -f1)
    problem=$(echo "$filename" | grep -oP '(?<=domain)[^\-]+' | cut -d'0' -f2)
    heuristic=$(echo "$filename" | grep -oP '(?<=astar\().*?(?=\))')

    # Extract all possible stats
    translator_rules=$(grep -oP 'Generated \d+ rules' "$file" | grep -oP '\d+' || echo "N/A")
    relevant_atoms=$(grep -oP '\d+ relevant atoms' "$file" | grep -oP '\d+' || echo "N/A")
    auxiliary_atoms=$(grep -oP '\d+ auxiliary atoms' "$file" | grep -oP '\d+' || echo "N/A")
    final_queue_length=$(grep -oP '\d+ final queue length' "$file" | grep -oP '\d+' || echo "N/A")
    total_queue_pushes=$(grep -oP '\d+ total queue pushes' "$file" | grep -oP '\d+' || echo "N/A")
    translator_variables=$(grep -oP 'Translator variables: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_derived_variables=$(grep -oP 'Translator derived variables: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_facts=$(grep -oP 'Translator facts: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_goal_facts=$(grep -oP 'Translator goal facts: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_mutex_groups=$(grep -oP 'Translator mutex groups: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_total_mutex_groups_size=$(grep -oP 'Translator total mutex groups size: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_operators=$(grep -oP 'Translator operators: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_axioms=$(grep -oP 'Translator axioms: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_task_size=$(grep -oP 'Translator task size: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    translator_peak_memory=$(grep -oP 'Translator peak memory: \d+ KB' "$file" | grep -oP '\d+' || echo "N/A")
    search_time=$(grep -oP 'Search time: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    total_time=$(grep -oP 'Total time: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    canonical_pdb_patterns=$(grep -oP 'Canonical PDB heuristic number of patterns: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    canonical_pdb_size=$(grep -oP 'Canonical PDB heuristic total PDB size: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    canonical_pdb_time=$(grep -oP 'Canonical PDB heuristic computation time: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    hill_climbing_iterations=$(grep -oP 'Hill climbing iterations: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_generated_patterns=$(grep -oP 'Hill climbing generated patterns: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_rejected_patterns=$(grep -oP 'Hill climbing rejected patterns: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_max_pdb_size=$(grep -oP 'Hill climbing maximum PDB size: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_time=$(grep -oP 'Hill climbing time: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    hill_climbing_pattern_collection_patterns=$(grep -oP 'hill climbing pattern collection generator number of patterns: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_pattern_collection_size=$(grep -oP 'hill climbing pattern collection generator total PDB size: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    hill_climbing_pattern_collection_time=$(grep -oP 'hill climbing pattern collection generator computation time: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    dominance_pruning_pattern_cliques=$(grep -oP 'Pruned \d+ of \d+ pattern cliques' "$file" | grep -oP '\d+' || echo "N/A")
    dominance_pruning_pdbs=$(grep -oP 'Pruned \d+ of \d+ PDBs' "$file" | grep -oP '\d+' || echo "N/A")
    dominance_pruning_time=$(grep -oP 'Dominance pruning took [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    successor_generator_memory=$(grep -oP 'peak memory difference for successor generator creation: \d+ KB' "$file" | grep -oP '\d+' || echo "N/A")
    successor_generator_time=$(grep -oP 'time for successor generation creation: [\d\.]+s' "$file" | grep -oP '[\d\.]+' || echo "N/A")
    variables=$(grep -oP 'Variables: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    fact_pairs=$(grep -oP 'FactPairs: \d+' "$file" | grep -oP '\d+' || echo "N/A")
    bytes_per_state=$(grep -oP 'Bytes per state: \d+' "$file" | grep -oP '\d+' || echo "N/A")

    # Append all stats to the CSV file
    echo "$filename,$domain,$problem,$heuristic,$translator_rules,$relevant_atoms,$auxiliary_atoms,$final_queue_length,$total_queue_pushes,$translator_variables,$translator_derived_variables,$translator_facts,$translator_goal_facts,$translator_mutex_groups,$translator_total_mutex_groups_size,$translator_operators,$translator_axioms,$translator_task_size,$translator_peak_memory,$search_time,$total_time,$canonical_pdb_patterns,$canonical_pdb_size,$canonical_pdb_time,$hill_climbing_iterations,$hill_climbing_generated_patterns,$hill_climbing_rejected_patterns,$hill_climbing_max_pdb_size,$hill_climbing_time,$hill_climbing_pattern_collection_patterns,$hill_climbing_pattern_collection_size,$hill_climbing_pattern_collection_time,$dominance_pruning_pattern_cliques,$dominance_pruning_pdbs,$dominance_pruning_time,$successor_generator_memory,$successor_generator_time,$variables,$fact_pairs,$bytes_per_state" >> "$output_file"
done

echo "✅ All tasks completed and statistics collected."
