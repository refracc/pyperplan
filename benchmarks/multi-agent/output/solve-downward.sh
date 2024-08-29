#!/bin/bash

# Define the directories to process
directories=("blocksworld") #"depot" "driverlog" "elevators08" "logistics00" "rovers" "satellites" "sokoban" "taxi" "wireless" "woodworking08" "zenotravel")

# Function to execute the landmark_cut command
landmark_cut() {
    domain_file="$1"
    problem_file="$2"
    ../downward/fast-downward.py --sas-file "${problem_file}-lmcut-astar.sas" --plan-file "${problem_file}-lmcut-astar.plan" "$domain_file" "$problem_file" --search "astar(lmcut())"
}

# Loop through each directory
for dir in "${directories[@]}"; do
    domain_file="$dir/dom.pddl"
    
    # Check if the domain file exists
    if [ ! -f "$domain_file" ]; then
        echo "Domain file not found: $domain_file"
        continue
    fi

    # Get the problem files in the directory (excluding the domain file)
    for problem_file in "$dir"/*.pddl; do
        if [ "$problem_file" == "$domain_file" ]; then
            continue
        fi

        # Execute the landmark_cut function
        if landmark_cut "$domain_file" "$problem_file"; then
            echo "Processed $problem_file with domain $domain_file"
        else
            echo "Failed to process $problem_file with domain $domain_file"
        fi
    done
done

