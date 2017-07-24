from enum import Enum, unique
from osgeo import gdal
import numpy as np


# ---------------------------- DataTypeEnum ---------------------------- #
@unique
class DataTypeEnum(Enum):
    FACTOR = 1
    CONTINUOUS = 2


# ---------------------------- Description ---------------------------- #
class Description:

    width = 0
    height = 0
    xmin = 0
    ymin = 0
    xmax = 999999
    ymax = 999999
    cellSize = 10
    noDataValue = -9999


# ---------------------------- EnvDataset ---------------------------- #
class EnvDataset:

    desc = Description()
    layers = []
    envUnits = []

    def addLayer(self, newLayer):

        self.layers.append(newLayer)
        self.refreshDesc()
        self.refreashEnvUnits()

    def refreashEnvUnits(self):

        self.envUnits = []
        if len(self.layers) <= 0:
            return
        pixelCount = self.desc.width * self.desc.height
        for i in range(pixelCount):
            e = EnvUnit()
            e.isCal = True
            for j in range(len(self.layers)):
                layer = self.layers[j]
                envValue = layer.envData[i]
                e.envValues.append(envValue)
                e.dataTypes.append(layer.dataType)
                if envValue == self.layers[j].noDataValue:
                    e.isCal = False

            self.envUnits.append(e)


    def refreshDesc(self):

        if len(self.layers) <= 0:
            return
        else:
            gdalDs = self.layers[0].gdalDs
            geoTransform = gdalDs.GetGeoTransform()
            self.desc.noDataValue = gdalDs.GetRasterBand(1).GetNoDataValue()
            self.desc.width = gdalDs.RasterXSize
            self.desc.height = gdalDs.RasterYSize
            self.desc.cellSize = geoTransform[1]
            self.desc.xmin = geoTransform[0]
            self.desc.ymin = geoTransform[3] - self.desc.cellSize * self.desc.height
            self.desc.xmax = self.desc.xmin + self.desc.cellSize * self.desc.width
            self.desc.ymax = geoTransform[3]

    def getEnvUnitByRowCol(self, row, col):

        if row < 0 or row >= self.desc.height or col < 0 or col >= self.desc.width:
            return None
        else:
            return self.envUnits[row * self.desc.width + col]

    def getEnvUnitByXY(self, x, y):

        if x < self.desc.xmin or x > self.desc.xmax or y < self.desc.ymin or y > self.desc.ymax:
            return None
        else:
            irow = (self.desc.ymax - y) / self.desc.cellSize
            icol = (x - self.desc.xmin) / self.desc.cellSize
            return self.envUnits[irow * self.desc.width + icol]


# ---------------------------- EnvLayer ---------------------------- #
class EnvLayer:

    def __init__(self, filename, dataType):

        self.filename = filename
        self.gdalDs = gdal.Open(filename, gdal.GA_ReadOnly)
        self.xSize = self.gdalDs.RasterXSize
        self.ySize = self.gdalDs.RasterYSize
        self.noDataValue = self.gdalDs.GetRasterBand(1).GetNoDataValue()
        self.dataType = dataType
        self.envData = self.gdalDs.GetRasterBand(1).ReadAsArray(0, 0, self.xSize, self.ySize, self.xSize, self.ySize)
        self.envData = self.envData.flatten()
        self.calStat()

    def calStat(self):

        ix = np.where(self.envData != self.noDataValue)
        envData_without_noDataValue = self.envData[ix]
        self.maxValue = np.max(envData_without_noDataValue)
        self.minValue = np.min(envData_without_noDataValue)


# ---------------------------- EnvUnit ---------------------------- #
class EnvUnit:
    isCal = True
    targetValue = 0.0
    envValues = []
    dataTypes = []

    def __init__(self):
        self.isCal = True
        self.targetValue = 0.0
        self.envValues = []
        self.dataTypes = []