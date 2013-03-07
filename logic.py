#!/usr/bin/env python2

import re
T, F = True, False

########################################
# Class defs

class Expression:
    def wrap(self):
        if isinstance(self, Var) or isinstance(self, Not):
            return '%s' % self

        return '(%s)' % self

class Var(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def evaluate(self, var_map):
        return var_map[self.name]

# Operators

class Operator(Expression):
    def __init__(self, p, q=None):
        self.p = p
        self.q = q

    def evaluate(self, var_map):
        p = self.p.evaluate(var_map)

        if self.q is None:
            return self.__class__.eval(p)

        q = self.q.evaluate(var_map)
        return self.__eval__(p, q)

    def get_strs(self):
        return (self.p.wrap(), self.q.wrap())

class Not(Operator):
    def __str__(self):
        return '~%s' % self.p.wrap()

    @staticmethod
    def eval(p):
        return not p

class And(Operator):
    def __str__(self):
        return '%s ^ %s' % self.get_strs()

    def __eval__(self, p, q):
        return p and q

class Or(Operator):
    def __str__(self):
        return '%s v %s' % self.get_strs()

    def __eval__(self, p, q):
        return p or q

class Xor(Operator):
    def __str__(self):
        return '%s xor %s' % self.get_strs()

    def __eval__(self, p, q):
        return not p is q

class IfThen(Operator):
    def __str__(self):
        return '%s -> %s' % self.get_strs()

    def __eval__(self, p, q):
        return not p or q

class IfAndOnlyIf(Operator):
    def __str__(self):
        return '%s <-> %s' % self.get_strs()

    def __eval__(self, p, q):
        return p is q

########################################
# Parsing
# ...ugh

LEXER = re.compile(r'[a-z]+|[~\^()]|->|<->|(?<= )(?:v|xor)(?= )')

def tokenize(statement):
    return LEXER.findall(statement)

def nest(tokens):
    tokz = []
    nested = []
    depth = 0

    for tok in tokens:
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
            if depth == 0:
                tokz.append(nested)
                nested = []
                continue

        if depth >= 1:
            nested.append(tok)
        else:
            tokz.append(tok)


    print tokz


print(tokenize('~(p v q) ^ q'))


########################################
# Truth table

def find_var_names(statement):
    if statement is None:
        return []

    if isinstance(statement, Var):
        return [statement.name]

    var_names = find_var_names(statement.p)
    var_names.extend(v for v in find_var_names(statement.q) if v not in var_names)
    return sorted(var_names)

def value_permutations(n_vars):
    if n_vars == 1:
        return [[T], [F]]

    perms = []
    sub_perms = value_permutations(n_vars - 1)

    for value in (T, F):
        for sub_perm in sub_perms:
            perms.append([value] + sub_perm)

    return perms

def tt_row(cells):
    cells = map(lambda x: 'T' if x is T else x, cells)
    cells = map(lambda x: 'F' if x is F else x, cells)
    print ' | '.join(map(str, cells))

def truth_table(statement):
    if isinstance(statement, str):
        statement = parse(statement)

    var_names = find_var_names(statement)
    tt_row(var_names + [statement])

    for perm in value_permutations(len(var_names)):
        var_map = dict(zip(var_names, perm))
        tt_row(perm + [statement.evaluate(var_map)])

    print


########################################
# Example usage

p, q, r, s = Var('p'), Var('q'), Var('r'), Var('s')

truth_table(p)
truth_table(Not(p))
truth_table(And(p, q))
truth_table(Or(p, q))
truth_table(Xor(p, q))
truth_table(IfThen(p, q))
truth_table(IfAndOnlyIf(p, q))
truth_table(IfThen(And(p, Not(r)), IfAndOnlyIf(q, Or(Xor(p, r), IfThen(r, s)))))

########################################
# Todo:
# - get parsing working D: (remember: order of ops)
# - statement class..probably
# - sexy error messages
# - improve truth tables..multi-char variables
# - appropriate bracketing when pretty printing
# - argument valid/invalid
# - state whether tautology/contradiction/neither
# - extra operators, extra symbols
# - show working steps?..
# - CLI
