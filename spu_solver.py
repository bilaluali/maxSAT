import argparse
import msat_runner,wcnf
from sys import exit
from instance import Instance

spu_instance = Instance()

def parse_instance(path):
    """Parse the input file, using Instance class."""
    global spu_instance
    with open(path) as f:
        for l in f:
            line = l.strip('\n').split()
            spu_instance.add_elem(line[0],line[1:])

    f.close()

def software_package_upgrade(solver):
    """ Notation: pi (package i), xi (variable representing pi)
    • D (dependeces conjunction of pi), d (disjunction of packages pj)
    • C (conflicts conjuction of pi), c(packages pj)
    • X (set of variables representing the packages)
    """

    formula = wcnf.WCNFFormula()
    X={} # pi -> xi. Will ease apply solution to our domain.

    _,packages,dependences,conflicts = spu_instance.get_instance()

    # Create soft clauses
    for pi in packages:
        X[pi] = formula.new_var() #xi
        formula.add_clause([X[pi]],weight=1)

    # Create hard clauses (dependences)
    for pi,D in dependences.items():
        for d in D:
            hard_clause=[-X[pi]]
            hard_clause.extend([X[pj] for pj in d]) # -xi V xj (pj ∈ d)
            formula.add_clause(hard_clause,weight=wcnf.TOP_WEIGHT)

    # Create hard clauses (conflicts)
    for pi,C in conflicts.items():
        for pj in C: # ᴧ pj ∈ C
            formula.add_clause([-X[pi],-X[pj]],weight=wcnf.TOP_WEIGHT)

    # Solve formula
    opt,model = solver.solve(formula)
    formula.write_dimacs()

    # Negative variables, represent packages cannot be installed.
    return X, opt, [n for n in model if n < 0]

def format_solution(vars,num_packs,cannot_install):
    """Formats the standard  output"""
    print("================ SOLUTION =================")
    print("o"," ",num_packs)
    packs = [get_key(abs(p),vars) for p in cannot_install]
    packs.sort() # Sorting ascendingly
    print("v"," ",', '.join(packs))

    pass

def get_key(val,dict):
    """Get any key by value. Notice values will be the
    identifiers returned by formula.new_var(), append
    they will be unique. So we can do it."""
    for k,v in dict.items():
         if val == v:
             return k

    return "key doesn't exist"

def main(argv=None):
    args = parse_command_line_arguments(argv)

    solver = msat_runner.MaxSATRunner(args.solver)
    instance_path = args.instance

    parse_instance(instance_path)

    vars,num_packs,cannot_install = software_package_upgrade(solver)
    format_solution(vars,num_packs,cannot_install)

def parse_command_line_arguments(argv=None):
    """Reused from graph.py"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("solver", help="Path to the MaxSAT solver.")

    parser.add_argument("instance", help="Path to the file that descrives the"
                                      " input instance.")

    return parser.parse_args(args=argv)

if __name__ == '__main__':
    exit(main())
