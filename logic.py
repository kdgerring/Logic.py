#!/usr/bin/env python2

import re

########################################
# Class defs

class Expression:
    def is_tautology(self):
        truth = TruthTable(self)
        values = map(lambda v: v[1], truth.values)
        return all(values)

    def is_contradiction(self):
        truth = TruthTable(self)
        values = map(lambda v: v[1], truth.values)
        return not any(values)

def wrap(expression):
    if isinstance(expression, (Unconditional, Var, Not)):
        return '%s' % expression

    return '(%s)' % expression

## Unconditionals

class Unconditional(Expression):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __str__(self):
        return self.symbol

    def get_names(self):
        return []

    def evaluate(self, _=None):
        return self.value

T = Unconditional('T', True)
F = Unconditional('F', False)

## Variables

class Var(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_names(self):
        return [self.name]

    def evaluate(self, var_map):
        return var_map[self.name]

## Not operation

class Not(Expression):
    def __init__(self, p):
        self.p = p
        self.q = None

    def __str__(self):
        return '~%s' % wrap(self.p)

    def get_names(self):
        return self.p.get_names()

    def evaluate(self, var_map):
        p = self.p.evaluate(var_map)
        return not p

## All other operations

def operator(symbol, rule):
    class Operation(Expression):
        def __init__(self, p, q):
            self.p = p
            self.q = q

        def __str__(self):
            p = self.p if isinstance(self.p, Operation) else wrap(self.p)
            q = self.q if isinstance(self.q, Operation) else wrap(self.q)

            return '%s %s %s' % (p, symbol, q)

        def get_names(self):
            p_names = self.p.get_names()
            q_names = self.q.get_names()
            q_names = filter(lambda n: n not in p_names, q_names)
            return sorted(p_names + q_names)

        def evaluate(self, var_map):
            p = self.p.evaluate(var_map)
            q = self.q.evaluate(var_map)
            return rule(p, q)

    return Operation

And           = operator('^',    lambda p, q: p and q)
Or            = operator('v',    lambda p, q: p or q)
Xor           = operator('XOR',  lambda p, q: not p is q)
Nand          = operator('NAND', lambda p, q: not (p and q))
Nor           = operator('NOR',  lambda p, q: not (p or q))
Xnor          = operator('XNOR', lambda p, q: p is q)
Conditional   = operator('->',   lambda p, q: not p or q)
Biconditional = operator('<->',  lambda p, q: p is q)


'''

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


#print(tokenize('~(p v q) ^ q'))
'''

########################################
# Truth table

def bool_permutations(n):
    if n == 1:
        return ((True,), (False,))

    perms = []
    sub_perms = bool_permutations(n - 1)

    for value in (True, False):
        for perm in sub_perms:
            perms.append((value,) + perm)

    return tuple(perms)

class TruthTable:
    def __init__(self, expression):
        self.expression = expression
        self.values = []
        self.build()

    def __str__(self):
        def row(cells):
            cells = map(lambda x: 'FT'[x] if isinstance(x, bool) else x, cells)
            cells = map(str, cells)
            return ' | '.join(cells) + '\n'

        names = self.expression.get_names()
        output = row(names + [self.expression])

        for perm in bool_permutations(len(names)):
            var_map = dict(zip(names, perm))
            value = self.expression.evaluate(var_map)
            output += row(perm + (value,))

        return output

    def build(self):
        names = self.expression.get_names()
        n_vars = len(names)

        for perm in bool_permutations(n_vars):
            var_map = dict(zip(names, perm))
            value = self.expression.evaluate(var_map)
            self.values.append((perm, value))

########################################
# Arguments

class Argument:
    def __init__(self, propositions, implication):
        self.propositions = propositions
        self.implication = implication

    def is_valid(self):
        def join_props(props):
            if len(props) == 2:
                return And(props[0], props[1])

            return And(props[0], join_props(props[1:]))

        p = join_props(self.propositions)
        q = self.implication

        return Conditional(p, q).is_tautology()

########################################
# Example usage

p, q, r, s = Var('p'), Var('q'), Var('r'), Var('s')

exp1 = Or(Var('x'), Or(Var('y'), Or(T, F)))
print TruthTable(exp1)
print exp1.is_tautology()

a = Var('a')
b = Var('b')

print Argument((Conditional(a, b), a, a, a), b).is_valid()

print
print
print TruthTable(And(Not(Var('x')), And(Or(Or(Var('y'), Var('q')), Var('z')), Not(Not(Var('w'))))))

########################################
# Todo:
# - unit tests!!
# - get parsing working D: (remember: order of ops)
# - show working steps?
# - CLI + GUI
# - simplifier
# - circuit diagram
