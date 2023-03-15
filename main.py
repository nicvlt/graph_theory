import os


class Node:
    def __init__(self, letter='x', in_neighbor='None', duration=0, rank=-1) -> None:
        self.letter = letter
        self.in_neighbor = in_neighbor
        self.duration = duration
        self.rank = rank

    def __str__(self) -> str:
        return 'Node: {} | In Neigh: {} | Duration: {} | Rank: {}'.format(self.letter, self.in_neighbor, self.duration, self.rank)


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


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

    print('\n\nAdjacency Matrix:\n\n')

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
    print(header)
    print(line + line.replace('-', '=') * len(node_letters))
    for i, row in enumerate(matrix):
        row_label = node_letters[i].rjust(max_num_width)
        row_str = ' | '.join([str(x).ljust(max_num_width) for x in row])
        print(('| {:^{width}} | ' + row_str +
              ' |').format(row_label, width=max_num_width))
        print(line + line.replace('-', '=') * len(node_letters))


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


def main():

    clear_terminal()

    print('\n\n\nWELCOME !\n\n\n')

    play = True
    while play:

        file_name = input('Enter file name: ')

        nodes = init_nodes('./assets/{}.txt'.format(file_name))
        if nodes == 'File not found':
            print('File not found')
            continue
        nodes = standardize_nodes(nodes)
        display_adjacency_matrix(nodes)

        if 0 in is_scheduling_graph(file_name, nodes):
            print('\n\nThis is a scheduling graph\n\n')
            for node in nodes:
                print(node.__str__())
        else:
            print('\n\nThis is not a scheduling graph :')
            if 1 in is_scheduling_graph(file_name, nodes):
                print('- There is a cycle in the graph.')
            if 2 in is_scheduling_graph(file_name, nodes):
                print('- There is a negative edge in the graph.')
            print('\n\n')

        play = input('Do you want to continue? (y/n): ') == 'y'
        clear_terminal()


main()
