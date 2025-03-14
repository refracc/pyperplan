#!/bin/bash

dir="./experiment_data"
output_file="data.csv"

echo "problem_id,domain,num_agents,total_time_ms,total_plan_length,total_nodes_expanded,total_heuristic_calls,total_applicable_actions,total_nodes_generated,total_objects,translator_variables,translator_derived_variables,translator_facts,translator_goal_facts,translator_operators,translator_axioms,translator_task_size,avg_time_per_agent,avg_plan_length_per_agent,avg_nodes_expanded_per_agent,avg_heuristic_calls_per_agent,avg_applicable_actions_per_agent,avg_nodes_generated_per_agent" > "$output_file"

for file in "$dir"/*.json; do
  if [ -f "$file" ]; then
    # Existing metrics
    problem_id=$(jq -r '.problem_id' "$file")
    domain=$(jq -r '.domain' "$file")
    num_agents=$(jq -r '.num_agents' "$file")
    total_time=$(jq '[.agents[].metrics.time_taken_ms] | add' "$file")
    total_plan_length=$(jq '[.agents[].metrics.plan_length] | add' "$file")
    total_nodes_expanded=$(jq '[.agents[].metrics.nodes_expanded] | add' "$file")
    total_heuristic_calls=$(jq '[.agents[].metrics.heuristic_calls] | add' "$file")
    total_applicable_actions=$(jq '[.agents[].metrics.applicable_actions_count] | add' "$file")
    total_nodes_generated=$(jq '[.agents[].metrics.nodes_generated] | add' "$file")
    total_objects=$(jq '.num_locations' "$file")

    # New translator metrics
    translator_variables=$(jq -r '.translator_variables' "$file")
    translator_derived_variables=$(jq -r '.translator_derived_variables' "$file")
    translator_facts=$(jq -r '.translator_facts' "$file")
    translator_goal_facts=$(jq -r '.goal_facts' "$file")
    translator_operators=$(jq -r '.translator_operators' "$file")
    translator_axioms=$(jq -r '.translator_axioms' "$file")
    translator_task_size=$(jq -r '.translator_task_size' "$file")

    # Calculate averages
    avg_time_per_agent=$(echo "$total_time / $num_agents" | bc -l)
    avg_plan_length_per_agent=$(echo "$total_plan_length / $num_agents" | bc -l)
    avg_nodes_expanded_per_agent=$(echo "$total_nodes_expanded / $num_agents" | bc -l)
    avg_heuristic_calls_per_agent=$(echo "$total_heuristic_calls / $num_agents" | bc -l)
    avg_applicable_actions_per_agent=$(echo "$total_applicable_actions / $num_agents" | bc -l)
    avg_nodes_generated_per_agent=$(echo "$total_nodes_generated / $num_agents" | bc -l)

    # post-grounding stats (actions etc.)

    # Append all data to CSV
    echo "$problem_id,$domain,$num_agents,$total_time,$total_plan_length,$total_nodes_expanded,$total_heuristic_calls,$total_applicable_actions,$total_nodes_generated,$total_objects,$translator_variables,$translator_derived_variables,$translator_facts,$translator_goal_facts,$translator_operators,$translator_axioms,$translator_task_size,$avg_time_per_agent,$avg_plan_length_per_agent,$avg_nodes_expanded_per_agent,$avg_heuristic_calls_per_agent,$avg_applicable_actions_per_agent,$avg_nodes_generated_per_agent" >> "$output_file"
  fi
done

echo "CSV file created: $output_file"