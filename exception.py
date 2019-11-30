
class PackageNotFoundException(Exception):
    """Raised when a package is not defined in valid packages"""
    pass

class UnexpectedPackagesException(Exception):
    """Raised when number of packages defined in 'p', is different
        with len of 'list'"""
    pass
