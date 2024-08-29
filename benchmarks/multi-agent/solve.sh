#!/bin/bash

# Define the landmark-cut function
landmark_cut(){
    ./downward/fast-downward.py --sas-file "$2-lmcut-astar.sas" --plan-file "$2-lmcut-astar.plan" $1 $2 \
                --search "astar(lmcut())"
}

# Base output directory containing the solved domains and problems
output_base_dir="output"

# Loop through each directory in the output directory
for dir in "$output_base_dir"/*; do
    # Ensure it is a directory
    if [ -d "$dir" ]; then
        domain_file="$dir/dom.pddl"

        # Check if the domain file exists
        if [ ! -f "$domain_file" ]; then
            echo "Domain file not found: $domain_file"
            continue
        fi

        # Get the problem files in the directory
        for problem_file in "$dir"/*.pddl; do
            # Skip the domain file
            if [[ "$problem_file" == "$domain_file" ]]; then
                continue
            fi

            # Extract the problem file name
            problem_name=$(basename "$problem_file" .pddl)

            # Run the landmark-cut function for Fast Downward
            echo "Solving $problem_file with Fast Downward using landmark-cut..."
            landmark_cut "$domain_file" "$problem_file"

            # Check if the plan was generated
            plan_output_file="$problem_file-lmcut-astar.plan"
            if [ -f "$plan_output_file" ]; then
                echo "Plan generated: $plan_output_file"
            else
                echo "Failed to generate plan for $problem_file"
            fi
        done
    fi
done

