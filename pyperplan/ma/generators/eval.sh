#!/bin/bash

# Directory containing JSON files
dir="./experiment_data"

# Output CSV file
output_file="data.csv"

# CSV header
echo "problem_id,num_agents,total_time_ms,total_plan_length,total_nodes_expanded,total_heuristic_calls,total_applicable_actions,total_nodes_generated,total_objects,avg_time_per_agent,avg_plan_length_per_agent,avg_nodes_expanded_per_agent,avg_heuristic_calls_per_agent,avg_applicable_actions_per_agent,avg_nodes_generated_per_agent" > "$output_file"

# Iterate over JSON files in the directory
for file in "$dir"/*.json; do
  if [ -f "$file" ]; then
    problem_id=$(jq -r '.problem_id' "$file")
    num_agents=$(jq -r '.num_agents' "$file")
    total_time=$(jq '[.agents[].metrics.time_taken_ms] | add' "$file")
    total_plan_length=$(jq '[.agents[].metrics.plan_length] | add' "$file")
    total_nodes_expanded=$(jq '[.agents[].metrics.nodes_expanded] | add' "$file")
    total_heuristic_calls=$(jq '[.agents[].metrics.heuristic_calls] | add' "$file")
    total_applicable_actions=$(jq '[.agents[].metrics.applicable_actions_count] | add' "$file")
    total_nodes_generated=$(jq '[.agents[].metrics.nodes_generated] | add' "$file")
    total_objects=$(jq '.objects | length' "$file")

    # Calculate averages per agent
    avg_time_per_agent=$(echo "$total_time / $num_agents" | bc -l)
    avg_plan_length_per_agent=$(echo "$total_plan_length / $num_agents" | bc -l)
    avg_nodes_expanded_per_agent=$(echo "$total_nodes_expanded / $num_agents" | bc -l)
    avg_heuristic_calls_per_agent=$(echo "$total_heuristic_calls / $num_agents" | bc -l)
    avg_applicable_actions_per_agent=$(echo "$total_applicable_actions / $num_agents" | bc -l)
    avg_nodes_generated_per_agent=$(echo "$total_nodes_generated / $num_agents" | bc -l)

    # Append data to CSV
    echo "$problem_id,$num_agents,$total_time,$total_plan_length,$total_nodes_expanded,$total_heuristic_calls,$total_applicable_actions,$total_nodes_generated,$total_objects,$avg_time_per_agent,$avg_plan_length_per_agent,$avg_nodes_expanded_per_agent,$avg_heuristic_calls_per_agent,$avg_applicable_actions_per_agent,$avg_nodes_generated_per_agent" >> "$output_file"
  fi
done

echo "CSV file created: $output_file"
