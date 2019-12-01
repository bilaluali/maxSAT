import sys
import msat_runner
import wcnf
from instance import Instance

spu = Instance()

def parse_instance(filename):
    """Parse the input file, using Instance class."""
    global spu
    with open(filename) as f:
        for l in f:
            line = l.strip('\n').split()
            spu.add_elem(line[0],line[1:])

    f.close()

def software_package_upgrade(solver):

    formula = wcnf.WCNFFormula()
    vars={} # Key(package),value(variable assigned)

    _,packages,dependences,conflicts = spu.get_instance()

    # Create soft clauses
    for pack in packages:
        vars[pack] = formula.new_var()
        formula.add_clause([vars[pack]],weight=1)

    # Create hard clauses (dependences)
    for pi,D in dependences.items():
        for d in D:
            hard_clause=[-vars[pi]]
            hard_clause.extend([vars[pj] for pj in d])
            formula.add_clause(hard_clause,weight=wcnf.TOP_WEIGHT)

    # Create hard clauses (conflicts)
    for pi,C in conflicts.items():
        for pj in C:
            formula.add_clause([-vars[pi],-vars[pj]],weight=wcnf.TOP_WEIGHT)

    # Solve formula
    opt,model = solver.solve(formula)
    formula.write_dimacs()

    # Negative variables, represent packages cannot be installed.
    return vars,opt,[n for n in model if n < 0]


def print_solution(vars,opt,cannot_install):
    """Formats the standard  output"""
    print("================ SOLUTION =================")
    print("o"," ",opt)
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


if __name__ == '__main__':

    solver = msat_runner.MaxSATRunner(sys.argv[1])
    instance=sys.argv[2]
    parse_instance(instance)
    vars,num_packs,cannot_install = software_package_upgrade(solver)
    print_solution(vars,num_packs,cannot_install)
