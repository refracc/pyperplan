#!/bin/bash

# Define the list of directories
directories=(
    airport depot freecell logistics movie openstacks pegsol satellite sokoban
    transport zenotravel blocks elevators gripper miconic parcprinter
    psr-small rovers scanalyzer tpp woodworking
)

# Semaphore limit for running scripts concurrently
max_concurrent_scripts=3
script_count=0

# Loop through each directory's script
for folder in "${directories[@]}"; do
    script_name="${folder}_process.sh"

    # Check if the script exists
    if [[ -f "$script_name" ]]; then
        echo "Running script: $script_name"
        rm -f "$script_name" &  # Run the script in the background
        ((script_count++))

        # Wait for any background job to finish if we reach the limit
        if [[ $script_count -ge $max_concurrent_scripts ]]; then
            wait -n  # Wait for any background job to finish
            ((script_count--))
        fi
    else
        echo "Script not found: $script_name"
    fi
done

# Wait for any remaining background processes to finish
wait

echo "All scripts have completed."
