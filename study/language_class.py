#=========================================================================
#                  output         and        input
#=========================================================================

class MyClass:
    """A simple example class"""
    i = 12345
    def f(self):
        return 'hello world'

class Complex:
def __init__(self, realpart, imagpart):
    self.r = realpart
    self.i = imagpart

x = Complex(3.0, -4.5)
>>> x.r, x.i
(3.0, -4.5)



