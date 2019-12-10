from logging import warning

class PackageNotFoundException(Exception):
    """Raised when a package is not defined in valid packages"""
    pass

class UnexpectedPackagesException(Exception):
    """Raised when number of packages defined in 'p', is different
        with len of 'list'"""
    pass

class Instance:

    def __init__(self):
        self.p = 0      # num_packages
        self.n = set()  # packages
        self.d = {}     # dependencies
        self.c = {}     # conflicts
        self._reps = [] # private: control when either error or warning..

    def add_elem(self,typ,value):
        """" Function to generalize each add function and consequently
        ease the addition. """
        if   typ == 'p': self.set_pkgs(value[-1])
        elif typ == 'n': self.add_pkg(value)
        elif typ == 'd': self.add_dependency(value[0],value[1:])
        elif typ == 'c': self.add_conflict(value[0],value[1:])
        else: warning("Not a valid type '{}'".format(typ))

    def set_pkgs(self,num_packages):
        if int(num_packages) < 0:
            raise ValueError("Number of packages shoud be positive")

        self.p = int(num_packages)

    def add_pkg(self,value):
        if len(value) != 1:
            raise UnexpectedPackagesException("Package description: expected 1 given {}: {}"
                                                        .format(len(value), ",".join(value)))
        if value[0] in self.n:
            self._reps.append(value[0])
        self.n.add(value[0])

    def add_dependency(self,pkg,value):
        """ Notice d myapp gcc, d myapp python2 python3 is
        gcc ∧ (python2 ∨ python3) so we need a list of lists.
        The list represents the conjunctions between lists and
        the each elements of lists the disjunctions"""

        if pkg not in self.get_pkgs():
            raise PackageNotFoundException(pkg)

        self.d.setdefault(pkg,[]).append(value) #Append list.

    def add_conflict(self,pkg,value):
        """Each element of the key list represent a conjunction"""
        if len(value) != 1:
            raise UnexpectedPackagesException("Conflict description: expected 1 given {}: {}"
                                                            .format(len(value),",".join(value)))
        if pkg not in self.get_pkgs():
            raise PackageNotFoundException(pkg)

        self.c.setdefault(pkg,[]).append(value[0])

    def get_pkgs(self):
        return self.n

    def get_dependency(self,pkg):
        try: return self.d[pkg]
        except KeyError: raise PackageNotFoundException(pkg)

    def get_conflict(self,pkg):
        try: return self.d[pkg]
        except KeyError: raise PackageNotFoundException(pkg)

    def get_instance(self):
        # Error control
        if self.p != len(self.n):
            if self.p == len(self.n) + len(self._reps):
                warning("Packages '{}' appear multiple times".format(",".join(set(self._reps))))
            else:
                raise UnexpectedPackagesException(("Expected {} packages given {}")
                                                    .format(self.p, len(self.n)+len(self._reps)))
        return self.p,self.n,self.d,self.c
