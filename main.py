import os
import math
import pandas as pd

class Node:
    def __init__(self, letter='x', in_neighbor='None', duration=0, rank=-1) -> None:
        self.letter = letter
        self.in_neighbor = in_neighbor
        self.duration = duration
        self.rank = rank

    def __str__(self) -> str:
        return 'Node: {} | In Neigh: {} | Duration: {} | Rank: {}\n'.format(self.letter, self.in_neighbor, self.duration, self.rank)


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_output_file(file_name, string_to_write):
    with open('./outputs/{}_output.txt'.format(file_name), 'w') as f:
        f.write(string_to_write)
    print('\nOutput file created: {}_output.txt\n'.format(file_name))


def clean_line(line):
    for i in range(len(line)):
        line[i] = line[i].replace('\n', '')
    if line[-1] == '':
        line.pop()
    return line


def init_nodes(file_name):
    nodes = []
    try:
        with open(file_name, 'r') as f:
            for line in f:
                line = line.split(' ')
                line = clean_line(line)
                globals()['node_{}'.format(line[0])] = Node(
                    line[0], ('None', line[2:])[len(line) > 2], int(line[1]))
                nodes.append(globals()['node_{}'.format(line[0])])
    except FileNotFoundError:
        return 'File not found'
    return nodes


def standardize_nodes(nodes):
    # add alpha node as supersource
    for node in nodes:
        if node.in_neighbor == 'None':
            node.in_neighbor = ['a']

    # create node alpha
    node_a = Node('a', 'None', 0)
    nodes.insert(0, node_a)

    # create node omega
    omega = len(nodes)
    globals()['node_{}'.format(omega)] = Node(str(omega), ['None'], 0)
    nodes.append(globals()['node_{}'.format(omega)])

    # add omega to all nodes that don't have out neighbors
    for node1 in nodes:
        if node1.letter == omega:
            break
        has_out_neighbor = False
        for node2 in nodes:
            if node1.letter in node2.in_neighbor:
                has_out_neighbor = True
                break
        if not has_out_neighbor and node1.letter != str(omega):
            globals()['node_{}'.format(omega)
                      ].in_neighbor.append(node1.letter)

    globals()['node_{}'.format(omega)].in_neighbor.remove('None')
    return nodes


def display_adjacency_matrix(nodes):

    output = ""

    # Create a list of node letters in the order they appear in the nodes array
    node_letters = [node.letter for node in nodes]

    # Create an empty matrix with the same number of rows and columns as the nodes array
    matrix = [[' ' for _ in range(len(nodes))] for _ in range(len(nodes))]

    # Fill in the matrix based on the in_neighbor attribute of each node
    for i, node in enumerate(nodes):
        for neighbor_letter in node.in_neighbor:
            if neighbor_letter in node_letters:
                in_neighbor_index = node_letters.index(neighbor_letter)
                matrix[in_neighbor_index][i] = '1'

    # Print the matrix with formatted spaces and lines separating the rows and columns
    max_num_width = max(len(str(len(nodes))), len(max(node_letters, key=len)))
    line = '+' + '-' * (max_num_width + 1) + '+'
    header = ('| {:^{width}} | ' + ' | '.join(['{:^{width}}']*len(
        node_letters)) + ' |').format('', *node_letters, width=max_num_width)
    output += (header + '\n')
    output += (line + line.replace('-', '=') * len(node_letters) + '\n')
    for i, row in enumerate(matrix):
        row_label = node_letters[i].rjust(max_num_width)
        row_str = ' | '.join([str(x).ljust(max_num_width) for x in row])
        output += (('| {:^{width}} | ' + row_str +
              ' |').format(row_label, width=max_num_width)) + '\n'
        output += (line + line.replace('-', '=') * len(node_letters)) + '\n'
    return output

def reset_ranks(nodes):
    for node in nodes:
        node.rank = -1
    return nodes


def has_cycle(nodes):
    for node in nodes:
        if node.rank == -1:
            nodes = reset_ranks(nodes)
            return True
    return False


def has_negative_edge(nodes):
    for node in nodes:
        if node.duration < 0:
            return True
    return False


def check_rank_condition(nodes):
    for node in nodes:
        if node.in_neighbor == 'None':
            return False
    return True


def get_ranks(nodes, copy_nodes):
    step = 0
    while(not check_rank_condition(copy_nodes)):
        letters_to_remove = []
        if len(copy_nodes) == 0:
            return nodes
        for c_node in copy_nodes:
            if c_node.in_neighbor == 'None':
                for node2 in nodes:
                    if c_node.letter == node2.letter:
                        node2.rank = step
                letters_to_remove.append(c_node.letter)
        for letter in letters_to_remove:
            for node in copy_nodes:
                if letter in node.in_neighbor:
                    node.in_neighbor.remove(letter)
                if node.in_neighbor == []:
                    node.in_neighbor = 'None'
            copy_nodes = [node for node in copy_nodes if node.letter != letter]

        step += 1
    return nodes


def is_scheduling_graph(file_name, nodes):
    copy_nodes = init_nodes('./assets/{}.txt'.format(file_name))
    copy_nodes = standardize_nodes(copy_nodes)
    nodes = get_ranks(nodes, copy_nodes)
    res = []

    if has_cycle(nodes):
        res.append(1)
    if has_negative_edge(nodes):
        res.append(2)
    return ([0], res)[len(res) > 0]


def compute_earliest_dates(nodes):
    sorted_rank = sorted(nodes, key=lambda x: x.rank)
    dict_earliest_date = {node.letter: 0 for node in sorted_rank}
    for node in sorted_rank:
        if node.in_neighbor == 'None':
            dict_earliest_date[node.letter] = 0
        else:

            # get max_earliest_date between all neighbors
            max_earliest_date = 0
            for neighbor in node.in_neighbor:

                # get neighbor duration
                neighbor_duration = 0
                for node2 in nodes:
                    if node2.letter == neighbor:
                        neighbor_duration = node2.duration
                        break

                # compare with max_earliest_date
                if dict_earliest_date[neighbor] + neighbor_duration > max_earliest_date:
                    max_earliest_date = dict_earliest_date[neighbor] + \
                        neighbor_duration

            # found max_earliest_date, assign to dict_earliest_date
            dict_earliest_date[node.letter] = max_earliest_date

    return dict_earliest_date

def get_successors(nodes, node_letter):
    successors = []
    for node in nodes:
        if node_letter in node.in_neighbor:
            successors.append(node.letter)
    if successors == []:
        successors = 'None'
    return successors

def get_all_latest_dates(successors, dict_latest_date, node):
    all_latest_dates = []
    if successors == 'None':
        all_latest_dates.append(dict_latest_date[node.letter])
    else:
        for successor in successors:
            all_latest_dates.append(dict_latest_date[successor] - node.duration)
    return all_latest_dates

def compute_latest_dates(nodes, earliest_dates):
    sorted_rank = sorted(nodes, key=lambda x: x.rank, reverse=True)
    dict_latest_date = {node.letter: 0 for node in sorted_rank}
    for node in sorted_rank:
        successors = get_successors(nodes, node.letter)
        if successors == 'None':
            dict_latest_date[node.letter] = earliest_dates[node.letter]
        else:
            all_latest_dates = get_all_latest_dates(
                successors, dict_latest_date, node)
            dict_latest_date[node.letter] = min(all_latest_dates)
    
    dict_latest_date = {k: dict_latest_date[k] for k in earliest_dates}
    return dict_latest_date

def compute_total_float(nodes, earliest_dates, latest_dates):
    dict_total_float = {node.letter: 0 for node in nodes}
    for node in nodes:
        dict_total_float[node.letter] = latest_dates[node.letter] - earliest_dates[node.letter]
    return dict_total_float

def compupte_free_float(nodes, earliest_dates, latest_dates):
    # get the free float of each node
    dict_free_float = {node.letter: 0 for node in nodes}
    for node in nodes:
        successors = get_successors(nodes, node.letter)
        # get minimum earliest date of successors
        if successors == 'None':
            dict_free_float[node.letter] = 0
        else:
            all_successors_earliest_dates = [earliest_dates[successor] for successor in successors]
            dict_free_float[node.letter] = min(all_successors_earliest_dates) - earliest_dates[node.letter] - node.duration
    return dict_free_float



def compute_critical_path(nodes, earliest_dates, latest_dates):
    critical_path = []
    for node in nodes:
        if earliest_dates[node.letter] == latest_dates[node.letter]:
            critical_path.append(node.letter)
    critical_path = sorted(critical_path, key=lambda x: [node.rank for node in nodes if node.letter == x][0])
    return critical_path

def get_all_paths(nodes_dict, start_node):
    # Initialize an empty list to store all possible paths
    all_paths = []

    # Define a recursive function to traverse the graph and find all paths
    def traverse(node, path):
        # If we've reached the final node, append the current path to all_paths
        if nodes_dict[node] == 'None':
            all_paths.append(path)
        # Otherwise, traverse each of the current node's successors
        else:
            for successor in nodes_dict[node]:
                traverse(successor, path + [successor])

    # Call the traverse function starting from the start_node
    traverse(start_node, [start_node])

    return all_paths


def get_all_critical_paths(nodes, earliest_dates, latest_dates):
    # get the nodes with total float = 0
    critical_nodes = []
    for node in nodes:
        if earliest_dates[node.letter] == latest_dates[node.letter]:
            critical_nodes.append(node.letter)
    
    dict_successors = {}
    # get the critical successors of each node
    for node in nodes:
        successors = get_successors(nodes, node.letter)
        if successors == 'None':
            dict_successors[node.letter] = 'None'
        else:
            critical_successors = []
            for successor in successors:
                if earliest_dates[successor] == latest_dates[successor]:
                    critical_successors.append(successor)
            if critical_successors == []:
                dict_successors[node.letter] = 'None'
            else:
                dict_successors[node.letter] = critical_successors
    

    # get all paths from the start node to the end node
    all_paths = get_all_paths(dict_successors, 'a')

    last_node = critical_nodes[-1]

    # compare the duration of each path with the earliest date of last_node
    # if the duration of the path is equal to the earliest date of last_node, then the path is a critical path
    critical_paths = []
    for path in all_paths:
        duration = 0
        for node in path:
            for node2 in nodes:
                if node2.letter == node:
                    duration += node2.duration
        if duration == earliest_dates[last_node]:
            critical_paths.append(path)    

    return critical_paths

    




def main():
    clear_terminal()
    print('\n\n\nWELCOME !\n\n\n')
    play = True
    while play:

        # Initialize the string that will be the output file
        output = ''

        # Initialize the nodes array with text file input
        file_name = input('Enter file name: ')
        nodes = init_nodes('./assets/{}.txt'.format(file_name))
        if nodes == 'File not found':
            print('\nFile not found\n')
            continue

        # Standardize the nodes array
        nodes = standardize_nodes(nodes)

        # Display the adjacency matrix
        output += '\nAdjacency Matrix:\n\n'
        output += display_adjacency_matrix(nodes)

        # Check if the graph is a scheduling graph & compute ranks
        if 0 in is_scheduling_graph(file_name, nodes):
            output += ('\nThis is a scheduling graph.\n\n')
            output += ('Ranks: ') + '\n'
            for node in nodes:
                output += (node.__str__())
            output += ('\n\n')

            # Compute earliest dates
            earliest_dates = compute_earliest_dates(nodes)
            df_earliest_dates = pd.DataFrame.from_dict(earliest_dates, orient='index', columns=[' '])
            output += 'Earliest dates: ' + '\n'
            output += str(df_earliest_dates)
            output += ('\n\n')

            # Compute latest dates
            latest_dates = compute_latest_dates(nodes, earliest_dates)
            df_latest_dates = pd.DataFrame.from_dict(latest_dates, orient='index', columns=[' '])
            output += 'Latest dates: ' + '\n'
            output += str(df_latest_dates)
            output += ('\n\n')

            # Compute free float
            free_float = compupte_free_float(nodes, earliest_dates, latest_dates)
            df_free_float = pd.DataFrame.from_dict(free_float, orient='index', columns=[' '])
            output += 'Free float: ' + '\n'
            output += str(df_free_float)
            output += ('\n\n')

            # Compute total float
            total_float = compute_total_float(nodes, earliest_dates, latest_dates)
            df_total_float = pd.DataFrame.from_dict(total_float, orient='index', columns=[' '])
            output += 'Total float: ' + '\n'
            output += str(df_total_float)
            output += ('\n\n')

            # Compute critical path
            critical_path = get_all_critical_paths(nodes, earliest_dates, latest_dates)
            output += ('\n\nCritical path:') + '\n'
            for path in critical_path:
                output += (str(path)) + '\n'

        else:
            output +=('\n\nThis is not a scheduling graph :') + '\n'
            if 1 in is_scheduling_graph(file_name, nodes):
                output +=('- There is a cycle in the graph.') + '\n'
            if 2 in is_scheduling_graph(file_name, nodes):
                output +=('- There is a negative edge in the graph.')+ '\n' 
        create_output_file(file_name, output)

        # Ask the user if he wants to continue
        play = input('Do you want to continue? (y/n): ') == 'y'
        clear_terminal()


main()
