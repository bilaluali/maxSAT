#!/usr/bin/env python3
# -*- coding: utf -*-

# pylint: disable=missing-docstring

from __future__ import absolute_import, print_function

import io
import itertools
import sys


TOP_WEIGHT = 0


class WCNFException(Exception):
    """Invalid MaxSAT operation."""


class WCNFFormula(object):

    def __init__(self):
        self.num_vars = 0
        self.hard = []  # Item format: [literals]
        self.soft = []  # Item format: (weight, [literals])
        self._sum_soft_weights = 0
        self.header = []

    @property
    def num_clauses(self):
        """Number of clauses in the formula (soft + hard)."""
        return len(self.hard) + len(self.soft)

    @property
    def top_weight(self):
        """Formula top weight."""
        return self._sum_soft_weights + 1

    def clean(self):
        self.__init__()

    def add_clauses(self, clauses, weight=TOP_WEIGHT):
        """Adds the given set of clauses, having each one the specified weight.

        :param clauses: Iterable filled with sets of literals.
        :type clauses: list[list[int]]
        :param weight: Weight applied to all the clauses, as in add_clause().
        :type weight: int
        """
        for clause in clauses:
            self.add_clause(clause, weight)

    def add_clause(self, literals, weight):
        """Adds the given literals as a new clause with the specified weight.

        :param literals: Clause literals
        :type literals: list[int]
        :param weight: Clause weight, less than 1 means infinity.
        :type weight: int
        """
        self._check_literals(literals)
        self._add_clause(literals, weight)

    def extend_vars(self, how_many):
        """Extends the number of used variables.
        """
        if how_many < 0:
            raise ValueError("Cannot be extended a negative quantity")
        self.num_vars += how_many

    def new_var(self):
        """Returns the next free variable of this formula.

        :return: The next free variable (>1).
        :rtype: int
        """
        self.num_vars += 1
        return self.num_vars #Retorna el "id" de la var.

    def is_13wpm(self, strict=False):
        """Tests if the formula is in 1,3-WPM format."""
        soft_ok = all(len(c) == 1 for _, c in self.soft)
        hard_ok = all(len(c) == 3 or len(c) < 3 and not strict
                      for c in self.hard)
        return soft_ok and hard_ok

    def to_13wpm(self):
        """Generates a new formula that is the 1,3-WPM equivalent to self.
        Notation:
        • bm (reification_vars), Cm(self soft plus bi and self hard clauses).
        • wi,Ci (current weight and clause), li (current literal of Ci).
        • zi and bi are reification variables. """
        formula13 = WCNFFormula()
        bm,Cm = {},[]

        # new_var() returns next id available, so var1 (form) is var1 (self)
        for _ in range(self.num_vars): formula13.new_var()

        # Reification variables for each soft clause.
        for wi,Ci in self.soft:
            bi = formula13.new_var()
            bm[bi] = (wi,Ci)
            formula13.add_clause([-bi],wi) #Soft clauses
            Cm.append([li for li in Ci] + [bi])

        # Getting each hard clause.
        Cm += [Ci for Ci in self.hard]

        # Clauses to 1,3-WPM format
        for Ci in Cm:
            if len(Ci) == 3: formula13.add_clause(Ci,0)
            else:
                for Ci_13 in self._clause_to13(Ci,formula13):
                    formula13.add_clause(Ci_13,0)

        return formula13

    def _clause_to13(self,Ci,form):
        """Tests if size is less than 3. Then add randomly a
        element of clause. Calls _parse_to13 otherwise."""
        if len(Ci) < 3:
            return [Ci + [Ci[0] for _ in range(3-len(Ci))]]
        else:
            return self._parse_to13([],Ci,form)


    def _parse_to13(self,C,Ci,form):
        """Parses recursivly a clause Ci with size greater than 3
        in subclauses of length 3."""
        if len(Ci) == 3:
            return C + [Ci]
        else:
            zi = form.new_var()
            return self._parse_to13(C+[Ci[0:2]+[zi]], [-zi]+Ci[2:], form)

    def sum_soft_weights(self):
        return self._sum_soft_weights

    def write_dimacs(self, stream=sys.stdout):
        """Writes the formula in DIMACS format into the specified stream.

        :param stream: A writable stream object.
        """
        for line in self.header:
            print("c", line, file=stream)

        top = self.top_weight
        print("p wcnf", self.num_vars, self.num_clauses, top, file=stream)

        print("c ===== Hard Clauses =====", file=stream)
        for clause in self.hard:
            print(top, " ".join(str(l) for l in clause), "0", file=stream)

        print("c ===== Soft Clauses (Sum weights: {0}) ====="
              .format(self._sum_soft_weights), file=stream)
        for weight, clause in self.soft:
            print(weight, " ".join(str(l) for l in clause), "0", file=stream)

    def write_dimacs_file(self, file_path):
        """Writes the formula in DIMACS format into the specified file.

        :param file_path: Path to a writable file.
        """
        with open(file_path, 'w') as stream:
            self.write_dimacs(stream)

    def _add_clause(self, literals, weight):
        if weight < 1:
            self.hard.append(literals)
        else:
            self.soft.append((weight, literals))
            self._sum_soft_weights += weight

    def _check_literals(self, literals):
        for var in map(abs, literals):
            if var == 0:
                raise WCNFException("Clause cannot contain variable 0")
            elif self.num_vars < var:
                raise WCNFException("Clause contains variable {0}, not defined"
                                    " by new_var()".format(var))

    def __str__(self):
        stream = io.StringIO()
        self.write_dimacs(stream=stream)
        output = stream.getvalue()
        stream.close()
        return output


# Module functions
################################################################################

def load_from_file(path, strict=False):
    with open(path, 'r') as stream:
        return load_from_stream(stream, strict)


def load_from_stream(stream, strict=False):
    reader = ((l.strip(), l_no) for l_no, l in enumerate(stream, start=1))
    reader = ((l, l_no) for l, l_no in reader if l and not l.startswith("c"))
    f_type, n_clauses, n_vars, top = None, -1, -1, -1

    formula = WCNFFormula()

    def get_clause(values):
        return (values[0], values[1:]) if top > 0 else (1, values)

    for l, l_no in reader:
        v = l.split()
        if v[0] == 'p' and f_type is None:
            if 4 <= len(v) <= 5:
                f_type = v[1]
                if v[1] == 'cnf':
                    n_vars, n_clauses = int(v[2]), int(v[3])
                elif v[1] == 'wcnf':
                    n_vars, n_clauses, top = int(v[2]), int(v[3]), int(v[4])
                else:
                    raise WCNFException("Invalid formula type: " + v[1])
            else:
                raise WCNFException("Invalid number of elements at line {0}"
                                    .format(l_no))
        elif f_type is not None:
            values = [int(e) for e in v]
            raw_clauses = [list(g) for k, g in
                           itertools.groupby(values, lambda x: x == 0)
                           if not k]

            for r_clause in raw_clauses:
                w, c = get_clause(r_clause)
                if not c:
                    raise WCNFException("Clause without literals at line {0}"
                                        .format(l_no))

                highest_var = max(abs(l) for l in c)
                while formula.num_vars < highest_var:
                    formula.new_var()
                formula.add_clause(c, TOP_WEIGHT if w == top else w)
        else:
            raise WCNFException("Clause found before preamble")

    if strict and formula.num_vars != n_vars:
        raise ValueError("incorrect number of variables (preamble: {},"
                         " found: {})".format(n_vars, formula.num_vars))
    if strict and formula.num_clauses != n_clauses:
        raise ValueError("incorrect number of clauses (preamble: {},"
                         " found: {})".format(n_clauses, formula.num_clauses))

    return formula


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Read formula
        formula = load_from_file(sys.argv[1], strict=True)
        # Convert to 1-3 WPMS
        formula_1_3 = formula.to_13wpm()
        # Check formula
        print("Is formula in 1-3 WPMS:", formula_1_3.is_13wpm(strict=True))
        # Store new formula
        formula_1_3.write_dimacs_file(sys.argv[2])
        print("- New 1-3 WPMS formula written to", sys.argv[2])
    else:
        # Wrong number of arguments
        print("Usage: {} <in DIMACS> <out 1-3 wpms DIMACS>".format(sys.argv[0]))
