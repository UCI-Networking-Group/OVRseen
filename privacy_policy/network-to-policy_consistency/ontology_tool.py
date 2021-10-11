#!/usr/bin/env python3

import shlex
import shutil
import sys

import networkx as nx


def validate_ontology(graph):
    roots = [n for n in graph.nodes if graph.in_degree(n) == 0]

    if len(roots) > 1:
        print('Error: more than one roots or orphan nodes exist', file=sys.stderr)
        return False

    if list(nx.simple_cycles(graph)):
        print('Error: loop found', file=sys.stderr)
        return False

    return True


def validate_and_write(graph, path):
    if validate_ontology(graph):
        shutil.copy(graph_file, path + '.bak')
        nx.write_gml(graph, path)


graph_file, action, *args = sys.argv[1:]
graph = nx.read_gml(graph_file)

root, = [n for n in graph.nodes if graph.in_degree(n) == 0]
if not validate_ontology(graph):
    exit(-1)

if action == 'query':
    node, = args

    if node in graph:
        paths = nx.all_simple_paths(graph, root, node)
        for path in paths:
            print(' <- '.join(reversed(path)))

        print("children:", ", ".join([dest for _, dest in graph.edges(node)]))
    else:
        print('Node', shlex.quote(node), 'not found', file=sys.stderr)
elif action == 'add':
    new_node, link_to = args

    if new_node in graph.nodes:
        print('Node', shlex.quote(new_node), 'already exists', file=sys.stderr)
    elif link_to not in graph.nodes:
        print('Node', shlex.quote(link_to), 'not found', file=sys.stderr)
    else:
        graph.add_edge(link_to, new_node)
        validate_and_write(graph, graph_file)
elif action == 'remove':
    to_remove, = args
    graph.remove_node(to_remove)
    validate_and_write(graph, graph_file)
elif action == 'link':
    u, v = args

    for node in u, v:
        if node not in graph.nodes:
            print('Node', shlex.quote(node), 'does not exist', file=sys.stderr)
            exit(-1)

    graph.add_edge(u, v)
    validate_and_write(graph, graph_file)
elif action == 'unlink':
    u, v = args
    graph.remove_edge(u, v)
    validate_and_write(graph, graph_file)
