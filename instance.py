import sys

class PackageNotFoundException(Exception):
    """Raised when a package is not defined in valid packages"""
    pass

class UnexpectedPackagesException(Exception):
    """Raised when number of packages defined in 'p', is different
        with len of 'list'"""
    pass

class Instance:

    def __init__(self):
        self.p = 0      #num_packages
        self.n = []  #packages
        self.d = {}     #dependencies
        self.c = {}     #conflicts

    def add_elem(self,typ,value):
        """" Function to generalize each add function and consequently
        ease the addition. """
        if   typ == 'p': self.set_pkgs(value[-1])
        elif typ == 'n': self.add_pkg(value[0])
        elif typ == 'd': self.add_dependency(value[0],value[1:])
        elif typ == 'c': self.add_conflict(value[0],value[1])

    def set_pkgs(self,num_packages):
        self.p = num_packages

    def add_pkg(self,elem):
        self.n.append(elem)

    def add_dependency(self,pkg,value):
        """ Notice d myapp gcc, d myapp python2 python3 is
        gcc ∧ (python2 ∨ python3) so we need a list of lists.
        The list represents the conjunctions and the list the
        disjunctions"""

        if pkg not in self.get_pkgs():
            raise PackageNotFoundException(pkg)

        self.d.setdefault(pkg,[]).append(value)

    def add_conflict(self,pkg,value):
        """Each element of the key list represent a conjunction"""

        if pkg not in self.get_pkgs():
            raise PackageNotFoundException(pkg)

        self.c.setdefault(pkg,[]).append(value)

    def get_pkgs(self):
        return self.n

    def get_dependency(self,pkg):
        return self.d.get(pkg)

    def get_conflict(self,pkg):
        return self.c.get(pkg)

    def get_instance(self):
        if int(self.p) != len(self.n):
            raise UnexpectedPackagesException("Expected {} given {}".format(self.p,len(self.n)))

        return self.p,self.n,self.d,self.c
