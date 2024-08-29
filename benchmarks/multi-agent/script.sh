#!/bin/bash

# Define the directories to process
directories=("blocksworld" "depot" "driverlog" "elevators08" "logistics00" "rovers" "satellites" "sokoban" "taxi" "wireless" "woodworking08" "zenotravel")

# Base output directory
output_base_dir="output"

# Path to the serialize binary
serialize_bin="./universal-pddl-parser-multiagent/examples/serialize_cn/serialize.bin"

# Create the base output directory if it doesn't exist
mkdir -p "$output_base_dir"

# Loop through each directory
for dir in "${directories[@]}"; do
    domain_file="$dir/domain/domain.pddl"
    
    # Check if the domain file exists
    if [ ! -f "$domain_file" ]; then
        echo "Domain file not found: $domain_file"
        continue
    fi

    # Create a corresponding output directory
    output_dir="$output_base_dir/$dir"
    mkdir -p "$output_dir"

    # Get the problem files in the problems/ directory
    for problem_file in "$dir/problems"/*.pddl; do

        # Extract the problem file name and number (if any)
        problem_name=$(basename "$problem_file" .pddl)
        problem_number=$(echo "$problem_name" | grep -o '[0-9]\+')

        # Set the output filenames
        cl_domain="$output_dir/dom.pddl"
        if [[ -n "$problem_number" ]]; then
            cl_problem="$output_dir/p${problem_number}.pddl"
        else
            cl_problem="$output_dir/${problem_name}_out.pddl"
        fi

        # Run the command and check for segmentation faults
        if $serialize_bin "$domain_file" "$problem_file" > "$cl_domain" 2> "$cl_problem"; then
            echo "Processed $problem_file: $cl_domain, $cl_problem"
        else
            echo "Failed to process $problem_file due to an error (possibly segmentation fault)"
        fi

        # Add a 1-second delay between executions
        sleep 0.5
    done
done

