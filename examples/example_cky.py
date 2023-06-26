#!/usr/bin/env python3
"""
Basic Python CKY parser implementation.

Note that the root symbol is defined at
the top of the file.

Last mod: 10/16/19 Shane Steinert-Threlkeld
"""
import nltk
from nltk.grammar import CFG, Production, Nonterminal
from nltk.tree import Tree

import itertools
from collections import defaultdict
import argparse


def build_prod_index(grammar):
    """
    NLTK's grammar lookup index only indexes the first element
    for the RHS of rules. This method allows lookup for all the
    symbols of the RHS.

    :type grammar: CFG
    """
    production_index = defaultdict(set)
    for production in grammar.productions(): # type: Production
        production_index[tuple(production.rhs())].add(production)
    return production_index


def build_chart(grammar, words):
    """
    Given a grammar and the input words, build the chart and populate
    with backpointers.

    :type grammar: CFG
    :type words: list[str]
    """
    # Initialize the chart as an (N+1) x (N+1) matrix, where each cell is an empty set.
    chart = [[set([]) for i in range(len(words)+1)] for j in range(len(words)+1)]

    production_index = build_prod_index(grammar)

    # -- 1) Start filling in cells left-to-right...
    for j, word in enumerate(words):
        j += 1
        # find all rules for the current word
        for prod in production_index[(word,)]:
            chart[j - 1][j].add((prod.lhs(), word))

        # -- 2) ...bottom-to-top
        for i in range(j - 2, -1, -1):

            # -- 3) Move the pivot index
            for k in range(i + 1, j):
                # Look up the left and right children
                # for the given i, k, j indices.
                left_pointers = chart[i][k]
                right_pointers = chart[k][j]

                # Pull just the symbols out of the backpointers, and form
                # as a set so as not to create duplicates.
                left_symbols = set([left_point[0] for left_point in left_pointers])
                right_symbols = set([right_pointer[0] for right_pointer in right_pointers])

                # Get the cartesian product (all possible ordered pairs from the sets)
                # of possible right hand sides...
                for rhs in itertools.product(left_symbols, right_symbols):

                    # ...and see if there is a rule in our grammar to derive the pair.
                    for prod in production_index[rhs]:

                        # If so, form a backpointer and store it in the chart.
                        back = prod.lhs(), k, rhs[0], rhs[1]
                        if back not in chart[i][j]:
                            chart[i][j].add(back)
    return chart


# -------------------------------------------
# Reconstruct the trees from backpointers.
# -------------------------------------------

def get_trees(cky_chart, words, root_symbol ='TOP'):
    return _get_trees(0, len(words), Nonterminal(root_symbol), cky_chart)

def _get_trees(i, j, nonterminal, cky_chart):
    """
    Helper function for converting backpointers to a tree

    :type nonterminal: Nonterminal
    :rtype: list[Tree]
    """

    # If we are at a leaf, return the preterminal -> terminal tree.
    trees = []
    for entry in [e for e in cky_chart[i][j] if e[0] == nonterminal]:
        # If we're at a preterminal, the backpointer will just
        # be the word.
        if isinstance(entry[1], str):
            return ['({} {})'.format(nonterminal.symbol(), entry[1])]
        nonterminal, k, left_child, right_child = entry
        left_subtrees = _get_trees(i, k, left_child, cky_chart)
        right_subtrees = _get_trees(k, j, right_child, cky_chart)
        for tree_l in left_subtrees:
            for tree_r in right_subtrees:
                trees.append('({} {} {})'.format(nonterminal.symbol(), tree_l, tree_r))

    return trees


def tokenize_sent(sent):
    """
    Splitting the word tokenizer out just to ensure good modularity.

    :param sent:
    :return:
    """
    return nltk.word_tokenize(sent)

def get_parses(grammar, sent, root_symbol='TOP'):
    """
    Run the parser

    :param words:
    :return:
    """
    words = tokenize_sent(sent)
    cky_chart = build_chart(grammar, words)
    return get_trees(cky_chart, words, root_symbol=root_symbol)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('grammarfile', help='Path to the CFG file to load.')
    p.add_argument('sentfile', help='Path to the sentences to parse.')
    p.add_argument('outfile', help='Path to the ')

    args = p.parse_args()

    grammar = nltk.load(args.grammarfile, 'cfg')
    root = str(grammar.start())

    with open(args.sentfile, 'r') as sent_f:
        with open(args.outfile, 'w') as out_f:
            for sent in sent_f:
                out_f.write(sent.strip() + '\n')

                # Skip blank lines
                if not sent.strip():
                    continue

                # Retrieve all the trees for the parse
                trees = get_parses(grammar, sent, root_symbol=root)
                for tree in trees:  # type: # Tree
                    out_f.write(tree + '\n')
                out_f.write('Number of parses: {}\n\n'.format(len(trees)))
