#!/bin/bash

# Define the directories to process
directories=("blocksworld" "depot" "driverlog" "elevators08" "logistics00" "rovers" "satellites" "sokoban" "taxi" "wireless" "woodworking08" "zenotravel")

# Path to the ENHSP jar
enhsp_jar="./enhsp.jar"

# Function to execute the ENHSP solver
solve_with_enhsp() {
    domain_file="$1"
    problem_file="$2"
    output_file="${problem_file%.pddl}-enhsp.plan"
    java -jar "$enhsp_jar" -o "$domain_file" -f "$problem_file" > "$output_file"
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

        # Execute the solve_with_enhsp function
        if solve_with_enhsp "$domain_file" "$problem_file"; then
            echo "Processed $problem_file with domain $domain_file"
        else
            echo "Failed to process $problem_file with domain $domain_file"
        fi
    done
done
