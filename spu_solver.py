import sys
from instance import Instance

spu = Instance()

def parse_input_file(filename):

    global spu

    with open(filename) as f:
        for l in f:
            line = l.strip('\n').split()
            spu.add_elem(line[0],line[1:])

    f.close()

    print(spu.get_all())

if __name__ == '__main__':
    parse_input_file(sys.argv[1])
