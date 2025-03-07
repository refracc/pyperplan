import os
import re
import csv
from collections import defaultdict

def parse_log_file(file_path):
    data = defaultdict(lambda: None)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic file information
    data['filename'] = os.path.basename(file_path)
    
    # Translator information
    translator_cmd_match = re.search(
        r'translate\.py (\S+)/domain\.pddl (\S+)/(\S+)\.pddl', content)
    if translator_cmd_match:
        data['domain'] = os.path.basename(translator_cmd_match.group(1))
        instance_with_ext = translator_cmd_match.group(3)
        data['instance'] = os.path.splitext(instance_with_ext)[0]

    # Search information
    search_cmd_match = re.search(r"--search '([^']*)'", content)
    if search_cmd_match:
        data['heuristic'] = search_cmd_match.group(1)

    # Detailed translation metrics
    time_patterns = {
        'parsing': r'Parsing: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'normalizing_task': r'Normalizing task... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'instantiating': r'Instantiating: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'datalog_generation': r'Generating Datalog program... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'datalog_normalization': r'Normalizing Datalog program: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'model_preparation': r'Preparing model... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'model_computation': r'Computing model... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'completing_instantiation': r'Completing instantiation... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'invariants_finding': r'Finding invariants: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'groups_instantiating': r'Instantiating groups... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'fact_groups_computation': r'Computing fact groups: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'translating_task': r'Translating task: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'unreachable_propositions': r'Detecting unreachable propositions: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'reordering_variables': r'Reordering and filtering variables: \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]',
        'writing_output': r'Writing output... \[([\d.]+)s CPU, ([\d.]+)s wall-clock\]'
    }

    for key, pattern in time_patterns.items():
        match = re.search(pattern, content)
        if match:
            data[f'{key}_cpu'] = float(match.group(1))
            data[f'{key}_wall'] = float(match.group(2))

    # Translator statistics
    translator_stats = {
        'relevant_atoms': r'(\d+) relevant atoms',
        'auxiliary_atoms': r'(\d+) auxiliary atoms',
        'final_queue_length': r'(\d+) final queue length',
        'total_queue_pushes': r'(\d+) total queue pushes',
        'rules_generated': r'Generated (\d+) rules',
        'initial_invariants': r'(\d+) initial candidates',
        'uncovered_facts': r'(\d+) uncovered facts',
        'effect_conditions_simplified': r'(\d+) effect conditions simplified',
        'implied_preconditions_added': r'(\d+) implied preconditions added',
        'propositions_removed': r'(\d+) propositions removed',
        'variables_necessary': r'(\d+) of \d+ variables necessary',
        'mutex_groups_necessary': r'(\d+) of \d+ mutex groups necessary',
        'operators_necessary': r'(\d+) of \d+ operators necessary',
        'translator_variables': r'Translator variables: (\d+)',
        'translator_derived_variables': r'Translator derived variables: (\d+)',
        'translator_facts': r'Translator facts: (\d+)',
        'translator_goal_facts': r'Translator goal facts: (\d+)',
        'translator_mutex_groups': r'Translator mutex groups: (\d+)',
        'translator_total_mutex_size': r'Translator total mutex groups size: (\d+)',
        'translator_operators': r'Translator operators: (\d+)',
        'translator_axioms': r'Translator axioms: (\d+)',
        'translator_task_size': r'Translator task size: (\d+)',
        'translator_peak_mem': r'Translator peak memory: (\d+) KB'
    }

    for key, pattern in translator_stats.items():
        match = re.search(pattern, content)
        if match:
            data[key] = int(match.group(1))

    # Search and planner statistics
    search_stats = {
        'search_peak_mem': r'Peak memory: (\d+) KB',
        'search_exit_code': r'search exit code: (\d+)',
        'planner_time': r'Planner time: ([\d.]+)s',
        'total_translator_time': r'Done! \[([\d.]+)s CPU, [\d.]+s wall-clock\]'
    }

    for key, pattern in search_stats.items():
        match = re.search(pattern, content)
        if match:
            value = float(match.group(1)) if 'time' in key else int(match.group(1))
            data[key] = value

    return dict(data)

def main():
    directory = './output'  # Change to your log directory
    output_csv = 'collected.csv'

    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    all_data = [parse_log_file(os.path.join(directory, f)) for f in txt_files]

    if all_data:
        # Collect all unique keys from all files
        all_keys = set().union(*(d.keys() for d in all_data))
        sorted_keys = sorted(all_keys)

        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
            writer.writeheader()
            writer.writerows(all_data)
        print(f"Extracted {len(all_data)} files to {output_csv}")
    else:
        print("No log files found.")

if __name__ == '__main__':
    main()
