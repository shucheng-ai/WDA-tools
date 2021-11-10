import copy
class Box():
    def __init__ (self, point1 = [], point2 = []):
        self.point1 = copy.deepcopy(point1)
        self.point2 = copy.deepcopy(point2)
        pass
    def unpack (self):
        return(self.point1, self.point2)

    pass

class Box3D(Box):
    def drop (self, dimension):
        del self.point1[dimension]
        del self.point2[dimension]
        return (self)
    pass

class Point():
    pass

class Point3D():
    pass

