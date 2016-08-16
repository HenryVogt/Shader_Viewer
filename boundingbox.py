__author__ = 'Henry Vogt'


class BoundingBox(object):

    def __init__(self, minp, maxp):
        self.minPoint = minp
        self.maxPoint = maxp
        self.xMin = self.minPoint[0]
        self.yMin = self.minPoint[1]
        self.zMin = self.minPoint[2]
        self.xMax = self.maxPoint[0]
        self.yMax = self.maxPoint[1]
        self.zMax = self.maxPoint[2]

    def getLx(self):
        return self.xMax-self.xMin

    def getLy(self):
        return self.yMax-self.yMin

    def getLz(self):
        return self.zMax-self.zMin

    def getCenter(self):
        return [(self.xMin+self.xMax)*0.5, (self.yMin+self.yMax)*0.5, (self.zMin+self.zMax)*0.5]

    def getL(self):
        return max(self.getLx(), self.getLy(), self.getLz())

    def getScale(self):
        return 2/self.getL()

    def __repr__(self):
        return "BoundingBox(%s,%s)" % (self.minPoint, self.maxPoint)
