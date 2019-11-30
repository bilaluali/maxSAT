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

    # Create hard clauses
    for _,d in dependences.items():
        for clause in d:
            formula.add_clause([-vars.get(literal) for literal in clause],weight=wcnf.TOP_WEIGHT)

    for clause in conflicts.values():
        formula.add_clause([-vars.get(literal) for literal in clause],weight=wcnf.TOP_WEIGHT)

    # Solve formula
    opt,model = solver.solve(formula)
    formula.write_dimacs()

    print(model)

def get_key(val,dict):
    for k,v in dict.items():
         if val == v:
             return k

    return "key doesn't exist"


if __name__ == '__main__':

    solver = msat_runner.MaxSATRunner(sys.argv[1])
    instance=sys.argv[2]
    parse_instance(instance)
    software_package_upgrade(solver)
