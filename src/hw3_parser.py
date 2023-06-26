import sys
import nltk
from nltk import word_tokenize


class Tree:
    def __init__(self, name, right=None, left=None, location=[0, 0]):
        self.name = name
        self.left = left
        self.right = right
        self.location = location

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.left is None:
            return '(' + str(self.name) + " " + str(self.right) + ')'  # at ' + str(self.location)
        if self.right is None:
            return '(' + str(self.name) + ") "  # at " + str(self.location)
        else:
            return '(' + str(self.name) + " " + str(self.right) + " " + str(
                self.left) + ')'  # at ' + str(self.location)

    def __iter__(self):
        pass

    def __getitem__(self, side):
        if side == "rhs":
            return self.right
        if side == "lhs":
            return self.left
        else:
            return self

    def get_loc(self):
        return self.location


grammar = nltk.data.load(sys.argv[1])
productions = grammar.productions()
non_lexical = []

for rule in productions:
    if rule.is_nonlexical():
        non_lexical.append(rule)

# TODO: check that this is the correct format
if not grammar.is_chomsky_normal_form:
    raise Exception("The provided grammar is not in CNF.")

with open(sys.argv[2], 'r', encoding='utf8') as d:
    data = []
    for line in d:
        data += line.strip().split("\n")

sentences = []
for sentence in data:
    sentences.append(word_tokenize(sentence))

def cyk(sentence):
    n = len(sentence)
    table = [[[] for i in range(n + 1)] for j in range(n)]

    # outermost loop, left-to-right through rows
    for j in range(1, n + 1):
        # find all the unary productions with given word on the RHS
        pos_productions = grammar.productions(rhs=sentence[j - 1])

        # if there are not, then we're dealing with words outside out lexicon and can't create a parse
        if not pos_productions:
            break

        rule = pos_productions[0]

        unit_tree = Tree(rule.lhs(), rule.rhs()[0], location=[j, j - 1])
        table[j - 1][j].append(rule.lhs())
        table[j - 1][j].append([])
        table[j - 1][j][1].append(unit_tree)

        # loop bottom-to-top through columns
        for i in range(j - 2, -1, -1):
            # break everything into sub-spans
            for k in range(i + 1, j):
                # for every A -> BC
                for rule in non_lexical:
                    # if B is in [i,k] and C is in [k,j]
                    if rule.rhs()[0] in table[i][k] and rule.rhs()[1] in table[k][j]:
                        # add A to [i,j]
                        table[i][j].append(rule.lhs())
                        table[i][j].append([])

                        for t in range(len(table[i][k][1])):
                            prod_tree = (Tree(rule.lhs(), table[i][k][1][t], table[k][j][1][t], location=[i, j]))
                            table[i][j][1].append(prod_tree)
    valid_parse = []
    if len(table[0][n]) == 0:
        return []
    for parse in table[0][n][1]:
        if str(parse)[1] == "S":
            valid_parse.append(parse)
            return valid_parse
        else:
            return []


with open(sys.argv[3], 'w', encoding='utf8') as g:
    for sentence in sentences:
        parses = cyk(sentence)
        untokenized = ' '.join(word for word in sentence)
        g.write(untokenized)
        g.write("\n")
        if len(parses) == 0:
            tnum = 0
        else:
            tnum = len(parses)
            for parse in parses:
                g.write(str(parse))
                g.write("\n")
        g.write("Number of parses: " + str(tnum) + "\n \n")