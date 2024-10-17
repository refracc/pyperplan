import os
import re
import csv

# Directory containing the output text files
output_dir = './task_outputs'
# CSV file to save the extracted information
csv_file = 'extracted_information.csv'

# Prepare a list to hold the extracted data
extracted_data = []

# Regular expressions to match the relevant lines in the log
domain_regex = re.compile(r'Parsing Domain .+/benchmarks/(?P<domain>[^/]+)/domain\.pddl')
problem_regex = re.compile(r'Parsing Problem .+/benchmarks/.+/task(?P<problem>\d+)\.pddl')
predicates_regex = re.compile(r'(?P<count>\d+) Predicates parsed')
actions_regex = re.compile(r'(?P<count>\d+) Actions parsed')
objects_regex = re.compile(r'(?P<count>\d+) Objects parsed')
constants_regex = re.compile(r'(?P<count>\d+) Constants parsed')
variables_regex = re.compile(r'(?P<count>\d+) Variables created')
operators_regex = re.compile(r'(?P<count>\d+) Operators created')
initial_h_regex = re.compile(r'Initial h value: (?P<initial_h>[\d\.]+)')
best_h_regex = re.compile(r'Found new best h: (?P<best_h>[\d\.]+) after (?P<expansions>\d+) expansions')
nodes_expanded_regex = re.compile(r'(?P<count>\d+) Nodes expanded')
plan_length_regex = re.compile(r'Plan length: (?P<count>\d+)')
search_method_regex = re.compile(r'using search: (?P<search_method>.+)')
heuristic_regex = re.compile(r'using heuristic: (?P<heuristic>.+)')

# Loop through each .txt file in the output directory
for filename in os.listdir(output_dir):
    if filename.endswith('.txt'):
        file_path = os.path.join(output_dir, filename)
        
        # Only process files longer than 4 bytes
        if os.path.getsize(file_path) > 4:
            domain_name = ''
            problem_name = ''
            initial_h = ''
            last_best_h = ''
            nodes_expanded = ''
            plan_length = ''
            predicates_count = ''
            actions_count = ''
            objects_count = ''
            constants_count = ''
            variables_count = ''
            operators_count = ''
            search_method = ''
            heuristic = ''
            
            with open(file_path, 'r') as file:
                for line in file:
                    # Extract domain and problem names
                    domain_match = domain_regex.search(line)
                    if domain_match:
                        domain_name = domain_match.group('domain')  # Get only the domain name
                        
                    problem_match = problem_regex.search(line)
                    if problem_match:
                        problem_name = f'task{problem_match.group("problem").zfill(2)}'  # Zero-padded task number

                    # Extract counts and values
                    predicates_match = predicates_regex.search(line)
                    if predicates_match:
                        predicates_count = predicates_match.group('count')
                        
                    actions_match = actions_regex.search(line)
                    if actions_match:
                        actions_count = actions_match.group('count')
                        
                    objects_match = objects_regex.search(line)
                    if objects_match:
                        objects_count = objects_match.group('count')
                        
                    constants_match = constants_regex.search(line)
                    if constants_match:
                        constants_count = constants_match.group('count')
                        
                    variables_match = variables_regex.search(line)
                    if variables_match:
                        variables_count = variables_match.group('count')
                        
                    operators_match = operators_regex.search(line)
                    if operators_match:
                        operators_count = operators_match.group('count')
                        
                    initial_h_match = initial_h_regex.search(line)
                    if initial_h_match:
                        initial_h = initial_h_match.group('initial_h')
                        
                    best_h_match = best_h_regex.search(line)
                    if best_h_match:
                        last_best_h = best_h_match.group('expansions')  # Use only the number of expansions
                        
                    nodes_expanded_match = nodes_expanded_regex.search(line)
                    if nodes_expanded_match:
                        nodes_expanded = nodes_expanded_match.group('count')
                        
                    plan_length_match = plan_length_regex.search(line)
                    if plan_length_match:
                        plan_length = plan_length_match.group('count')

                    # Extract search method and heuristic
                    search_method_match = search_method_regex.search(line)
                    if search_method_match:
                        search_method = search_method_match.group('search_method')
                    
                    heuristic_match = heuristic_regex.search(line)
                    if heuristic_match:
                        heuristic = heuristic_match.group('heuristic')

            # Check if the last 10 columns are empty
            last_columns_empty = all([
                not predicates_count, not actions_count, not objects_count, 
                not constants_count, not variables_count, not operators_count, 
                not initial_h, not last_best_h, not nodes_expanded, not plan_length
            ])

            # Only add to the extracted data if there's meaningful information
            if domain_name and problem_name and not last_columns_empty:
                extracted_data.append([
                    domain_name,
                    problem_name,
                    search_method,
                    heuristic,
                    predicates_count,
                    actions_count,
                    objects_count,
                    constants_count,
                    variables_count,
                    operators_count,
                    initial_h,
                    last_best_h,
                    nodes_expanded,
                    plan_length
                ])

# Write extracted data to CSV
if extracted_data:
    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([
            'Domain Name', 'Problem Name', 'Search Method', 'Heuristic',
            'Predicates', 'Actions', 'Objects', 'Constants',
            'Variables', 'Operators', 'Initial h Value', 'Last Best h Value',
            'Nodes Expanded', 'Plan Length'
        ])  # Header
        csv_writer.writerows(extracted_data)

print(f'Extracted information saved to: {csv_file}')

