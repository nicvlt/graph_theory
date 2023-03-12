class Node:
    def __init__(self, letter='x', in_neighbor='None', duration=0) -> None:
        self.letter = letter
        self.in_neighbor = in_neighbor
        self.duration = duration

    def __str__(self) -> str:
        return 'Node: {} | In Neigh: {} | Duration: {}'.format(self.letter, self.in_neighbor, self.duration)


def clean_line(line):
    for i in range(len(line)):
        line[i] = line[i].replace('\n', '')
    return line


def init_nodes(file_name):
    nodes = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.split(' ')
            line = clean_line(line)
            globals()['node_{}'.format(line[0])] = Node(
                line[0], ('None', line[2:])[len(line) > 2], line[1])
            nodes.append(globals()['node_{}'.format(line[0])])
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
    omega = len(nodes)+1
    globals()['node_{}'.format(omega)] = Node(omega, ['None'], 0)
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
        if not has_out_neighbor:
            globals()['node_{}'.format(omega)
                      ].in_neighbor.append(node1.letter)

    globals()['node_{}'.format(omega)].in_neighbor.remove('None')
    return nodes


def main():
    file_name = input('Enter file name: ')
    nodes = init_nodes('./assets/{}.txt'.format(file_name))
    nodes = standardize_nodes(nodes)
    for node in nodes:
        print(node.__str__())


main()
