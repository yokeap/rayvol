import pandas as pd
import cv2
import numpy as np
from skimage.morphology import skeletonize
from . import mathTools
from . import segmentation
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plot
# import plotly.graph_objects as go

plot.style.use('seaborn-darkgrid')

debug = False

# Reconstruct 3D of Object from shadow,
# height of object is calculated from range of shadow,
# all of edges of images is transform to real world coordinate,
# - finding pseudo skeleton (centroid) of object image
# - detect edges by perform column scanning and transform to real world coordinate,
# -


class reconstruct:
    def __init__(self, scale, config):
        self.homographyMatrix = np.array(config["homographyMatrix"])
        self.posVirlightIMG = np.array(config["virLightPosImg"]) * scale
        self.posVirlightWorld = np.array(config["virLightPos"])
        self.ptCloudRaw = 4
        self.objVolume = 0
        # self.ptCloudSectionLeft = np.array((height, 3))
        # self.ptCloudSectionRight = np.array((height, 3))

        self.scale = scale

    def skeleton(self, imgBin):
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        done = False
        size = np.size(imgBin)
        skel = np.zeros_like(imgBin)
        eroded = np.zeros_like(imgBin)
        temp = np.zeros_like(imgBin)
        imgOriginal = imgBin.copy()
        while(not done):
            # eroded = cv2.erode(imgOriginal, element)
            # temp = cv2.dilate(eroded, element)
            # temp = cv2.subtract(imgOriginal, temp)
            # skel = cv2.bitwise_or(skel, temp)
            # imgOriginal, eroded = eroded, imgOriginal
            cv2.erode(imgOriginal, element, eroded)
            cv2.dilate(eroded, element, temp)
            cv2.subtract(imgOriginal, temp, temp)
            cv2.bitwise_or(skel, temp, skel)
            imgOriginal, eroded = eroded, imgOriginal

            # zeros = size - cv2.countNonZero(imgBin)
            # if zeros == size:
            #     done = True
            if cv2.countNonZero(imgOriginal) == 0:
                return skel

    def reconstruct(self, imgSource, imgObj, imgShadowOnObj, imgShadow, posCrop):
        height, width, channel = imgSource.shape
        self.ptCloudSectionLeft = np.empty((height, 3))
        self.ptCloudSectionRight = np.empty((height, 3))
        self.ptCloudObjHeightUpper = np.empty((height, 3))
        self.ptCloudObjHeightLower = np.empty((height, 3))
        self.loop = 0
        # imgSkeleton = skeletonize(imgObj, method='lee')
        # imgSkeleton = self.skeleton(imgObj)
        imgSkeleton = imgShadowOnObj
        # imgHeight, imgWidth, channel = imgSource.shape
        imgHeight = posCrop[0][1] + posCrop[0][3]
        imgWidth = posCrop[0][0] + posCrop[0][2]
        # print("imgHeight = ", imgHeight)
        # print("imgWidth = ", imgWidth)
        debug = False
        if debug == True:
            cv2.imshow("Skeleton image", imgSkeleton)
        # scaning input binary image to detect the object edge
        # variable declaration
        self.edgeObjUpper = []
        self.edgeObjUpperWorld = []
        self.edgeObjMiddle = []
        self.edgeObjMiddleWorld = []
        self.edgeObjLower = []
        self.edgeObjLowerWorld = []
        self.edgesShadowUpper = []
        self.edgesShadowUpperWorld = []
        self.edgesShadowLower = []
        self.edgesShadowLowerWorld = []
        # self.ptCloudObjHeightUpper=[]
        self.heightShadow = np.empty(imgHeight)

        # scan for all (object: upper, middle and lower edge; shadow lower edge)
        for x in range(posCrop[0][0], posCrop[0][0] + posCrop[0][2]):
            flagObjUpperEdge = False
            flagObjMiddleEdge = False
            flagObjLowerEdge = False
            flagShadowLowerEdge = False
            flagShadowUpperEdge = False
            # for uppper edges
            for y in range(posCrop[0][1], posCrop[0][1] + posCrop[0][3]):
                pixObjVal = imgObj.item(y - posCrop[0][1], x - posCrop[0][0])
                pixSkeletonVal = imgSkeleton.item(
                    y - posCrop[0][1], x - posCrop[0][0])
                # pixShadowVal = imgShadow.item(y, x)
                # xx, yy is origianl position before cropped
                # upper edges detection
                # xx = x + posCrop[0][0]
                # yy = y + posCrop[0][1]
                if flagObjUpperEdge == False and pixObjVal > 0:
                    flagObjUpperEdge = True
                    # save x y coordinate with homogeneous coordiate
                    # edgeObjUpper.append(np.array([x, y, 1]))
                    # edgeObjUpperWorld.append(mathTools.homographyTransform(
                    #     homographyMatrix, [x, y, 1], 0.2))]
                    posUpper = [x, y, 1]
                    posUpperWorld = mathTools.homographyTransform(
                        self.homographyMatrix, posUpper, self.scale)
                    self.edgeObjUpper.append(np.array(posUpper))
                    self.edgeObjUpperWorld.append(posUpperWorld)
                    self.ptCloudSectionLeft[self.loop, :] = posUpperWorld
                    # #  centroid edges (from skeleton image), then lower edges (object image) and then lower edges of shadow (max shadow distance)
                if flagObjMiddleEdge == False and flagObjUpperEdge == True and pixSkeletonVal > 0:
                    flagObjMiddleEdge = True
                    posCentroid = [x, y, 1]
                    posCentroidWorld = mathTools.homographyTransform(
                        self.homographyMatrix, posCentroid, self.scale)
                    self.edgeObjMiddle.append(np.array(posCentroid))
                    self.edgeObjMiddleWorld.append(posCentroidWorld)
                    self.ptCloudObjHeightUpper[self.loop, :] = posCentroidWorld
                    self.ptCloudObjHeightLower[self.loop, :] = posCentroidWorld
                    # compute unit vector from centroid position (direction vector related with virtual light position)
                    centroid2LightUnitVector = mathTools.unitVector2D(
                        [x, y], self.posVirlightIMG[0:2])
                    # scanning to find the maximum shadow distance (shadow lowest edge) with respect with centroid
                    # using unit vector for direction reference then interpolate from centroid position until found the maximum shadow edge
                    flagShadowLowerEdge = False
                    flagShadowUpperEdge = False
                    for s in range(0, imgHeight):
                        posSampling = np.array(
                            [float(x), float(y)]) + s*centroid2LightUnitVector
                        # print(posSampling)
                        if(posSampling[0] > imgWidth):
                            posSampling[0] = imgWidth - 1
                            # print("break")
                            # print(posSampling[0])
                            # break
                        if(posSampling[1] > imgHeight):
                            posSampling[1] = imgHeight - 1
                            # print("break")
                            # print(posSampling[1])
                            # break
                        imgShadowValCompensateCrop = imgShadow.item(
                            int(posSampling[1] - posCrop[0][1]), int(posSampling[0] - posCrop[0][0]))
                        if flagShadowLowerEdge == False and imgShadowValCompensateCrop > 0:
                            flagShadowLowerEdge = True
                            # add 1.0 as homogeneous coordinate
                            posShadowLower = [
                                posSampling[0], posSampling[1], 1.0]
                            posShadowLowerWorld = mathTools.homographyTransform(
                                self.homographyMatrix, posShadowLower, self.scale)
                            self.edgesShadowLower.append(
                                np.array(posShadowLower))
                            self.edgesShadowLowerWorld.append(
                                posShadowLowerWorld)
                            # self.ptCloudSectionRight[loop,
                            #                          :] = posShadowLowerWorld
                        if flagShadowLowerEdge == True and flagShadowUpperEdge == False and imgShadowValCompensateCrop < 1:
                            flagShadowUpperEdge = True
                            posShadowUpper = [
                                posSampling[0], posSampling[1], 1.0]
                            posShadowUpperWorld = mathTools.homographyTransform(
                                self.homographyMatrix, posShadowUpper, self.scale)
                            self.edgesShadowUpper.append(
                                np.array(posShadowUpper))
                            self.edgesShadowUpperWorld.append(
                                posShadowUpperWorld)
                            skeletonHeight = mathTools.calHeightFromShadow(
                                posShadowUpper, posCentroid, posShadowUpperWorld, posCentroidWorld, self.posVirlightWorld)
                            self.ptCloudSectionLeft[self.loop,
                                                    2] = 0
                            self.ptCloudSectionRight[self.loop,
                                                     2] = 0
                            # self.ptCloudSectionLeft[self.loop,
                            #                         2] = 0
                            # self.ptCloudSectionRight[self.loop,
                            #                          2] = 0
                            self.ptCloudObjHeightUpper[self.loop,
                                                       2] = skeletonHeight / 2
                            self.ptCloudObjHeightLower[self.loop,
                                                       2] = self.ptCloudObjHeightUpper[self.loop, 2] * -1
                            self.loop = self.loop + 1
                            break
                # for lower edgesR
                if flagObjLowerEdge == False and flagObjUpperEdge == True and pixObjVal < 255:
                    flagObjLowerEdge = True
                    posLower = [x, y, 1]
                    posLowerWorld = mathTools.homographyTransform(
                        self.homographyMatrix, posLower, self.scale)
                    self.edgeObjLower.append(np.array(posLower))
                    self.edgeObjLowerWorld.append(posLowerWorld)
                    self.ptCloudSectionRight[self.loop, :] = posLowerWorld
                    # self.ptCloudSectionRight[self.loop, 0] = posLowerWorld[0]
                    # self.ptCloudSectionRight[self.loop, 1] = posLowerWorld[1]
                    break
        print(self.loop)

    def reconstructVolume(self, splineResolution):
        # creat 3D array to store point cloud
        #        1st array              nth array
        # [upper.x   upper.z]       [upper.x   upper.z]
        # [middle.x  middle.z] ...  [middle.x  middle.z]
        # [lower.x   lower.z]       [lower.x   lower.z]
        #
        # ---- Parameters description ------
        # splineResolution = amount of spline estimation points, default is 0.05

        # 3 base points upper middle lower.
        splineTotalPoints = int(
            (self.ptCloudSectionLeft.shape[1] - 1) / splineResolution)
        self.halfSliceLeft = np.zeros(
            (self.ptCloudSectionLeft.shape[1], 2, self.ptCloudSectionLeft.shape[0]))
        self.halfSliceRight = np.zeros(
            (self.ptCloudSectionLeft.shape[1], 2, self.ptCloudSectionLeft.shape[0]))
        self.sliceSplineLeft = np.zeros(
            (splineTotalPoints, 2, self.ptCloudSectionLeft.shape[0]))
        self.sliceSplineRight = np.zeros(
            (splineTotalPoints, 2, self.ptCloudSectionLeft.shape[0]))
        self.sliceModel = np.zeros(
            (splineTotalPoints * 2, 3, self.ptCloudSectionLeft.shape[0]))
        self.sliceModelArea = np.zeros(
            (self.ptCloudSectionLeft.shape[0], 2,))
        self.sliceSplineX = np.array([])
        self.sliceSplineY = np.array([])
        self.sliceSplineZ = np.array([])
        self.totalLength = self.ptCloudSectionLeft[self.loop -1, 1] - self.ptCloudSectionLeft[0, 1]
        print("Object Total Length = ", self.totalLength)
        # self.width = np.amax(self.ptCloudSectionRight[:, 0]) - np.amin(self.ptCloudSectionLeft[:, 0])
        # print("width: " + str(np.amax(self.ptCloudSectionRight[:, 0]) - np.amin(self.ptCloudSectionLeft[:, 0])))

        for i in range(0, self.loop):
            # to compute area properly polygon points must be sort to counter clockwise
            # start with top with half left slice
            # append x of upper, middle and lower to 3d array
            self.halfSliceLeft[:, 0, i] = (self.ptCloudObjHeightUpper[i, 0],
                                           self.ptCloudSectionLeft[i, 0], self.ptCloudObjHeightLower[i, 0])
            # apped y of upper, middle and lower to 3d array
            self.halfSliceLeft[:, 1, i] = (self.ptCloudObjHeightUpper[i, 2],
                                           self.ptCloudSectionLeft[i, 2], self.ptCloudObjHeightLower[i, 2])
            # half right slice
            # append x of lower, middle and upper to 3d array
            self.halfSliceRight[:, 0, i] = (self.ptCloudObjHeightLower[i, 0],
                                            self.ptCloudSectionRight[i, 0], self.ptCloudObjHeightUpper[i, 0])
            # apped y of upper, middle and lower to 3d array
            self.halfSliceRight[:, 1, i] = (self.ptCloudObjHeightLower[i, 2],
                                            self.ptCloudSectionRight[i, 2], self.ptCloudObjHeightUpper[i, 2])
            # spline estimation of half slice left side
            self.sliceSplineLeft[:, :, i] = np.array(mathTools.splineEstimate(
                self.halfSliceLeft[:, :, i], splineResolution)).T
            # spline estimation half slice right side
            self.sliceSplineRight[:, :, i] = np.array(mathTools.splineEstimate(
                self.halfSliceRight[:, :, i], splineResolution)).T

            # append y (length of object) to first column of sliceModel
            self.sliceModel[:, 0, i] = self.ptCloudSectionLeft[i, 1]
            # append x and z from half left and right spline interpolation
            self.sliceModel[:, 1, i] = np.concatenate(
                (self.sliceSplineLeft[:, 0, i], self.sliceSplineRight[:, 0, i]), axis=None)
            self.sliceModel[:, 2, i] = np.concatenate(
                (self.sliceSplineLeft[:, 1, i], self.sliceSplineRight[:, 1, i]), axis=None)
            # self.sliceModel[:, 1:3, i] = np.concatenate(
            #     (self.sliceSplineLeft[:, :, i], self.sliceSplineRight[:, :, i]), axis=None)

            # compute area of each slice of object length (along with y-axis)
            # append y (length of object) to first column of sliceModelArea
            self.sliceModelArea[i, 0] = self.ptCloudSectionLeft[i, 1]
            # 2nd is column of computes polygon area
            self.sliceModelArea[i, 1] = mathTools.polyArea(
                self.sliceModel[:, 1, i], self.sliceModel[:, 2, i])

            self.sliceSplineX = np.concatenate(
                (self.sliceSplineX, self.sliceModel[:, 0, i]), axis=None)
            self.sliceSplineY = np.concatenate(
                (self.sliceSplineY, self.sliceModel[:, 1, i]), axis=None)
            self.sliceSplineZ = np.concatenate(
                (self.sliceSplineZ, self.sliceModel[:, 2, i]), axis=None)

            # for using with lightning chart
            # objJson = {
            #     "x": self.sliceModel[:, 0, i],
            #     "y": self.sliceModel[:, 1, i],
            #     "z": self.sliceModel[:, 2, i],
            # }

            # self.objJson = np.concatenate(self.sliceModel[:, 0, i])
            # compute object volume by integrate computed areas (Riemann sum)
            if i > 0:
                sumVolume = self.sliceModelArea[i, 1] * (
                    self.sliceModelArea[i, 0] - self.sliceModelArea[i-1, 0])
                self.objVolume = self.objVolume + sumVolume

                # sA = ((self.sliceModelArea[i, 1] + self.sliceModelArea[i-1, 1])/2) * (self.sliceModelArea[i, 0] - self.sliceModelArea[i-1, 0]) + (
                #     self.sliceModelArea[0, 1]/2) * self.totalLength + (self.sliceModelArea[self.loop-1, 1]/2) * self.totalLength
                # self.objVolume = self.objVolume + sA
        # print("x = ", self.halfSliceLower[:, 0, 10])
        # print("y = ", self.halfSliceLower[:, 1, 10])
        self.objVolume = round(self.objVolume / 1000, 2)
        # print(self.objVolume)
        self.slicingObj = np.vstack(
            [self.sliceSplineX, self.sliceSplineY, self.sliceSplineZ]).T

        debug = False
        sliceNumber = 50
        if debug == True:
            figSlicing = plot
            figSlicing.scatter(
                self.halfSliceUpper[:, 0, sliceNumber], self.halfSliceUpper[:, 1, sliceNumber], marker='o')
            figSlicing.scatter(
                self.halfSliceLower[:, 0, sliceNumber], self.halfSliceLower[:, 1, sliceNumber], marker='o')
            figSlicing.show()

            figSpline = plot
            figSpline.scatter(
                self.sliceSplineUpper[:, 0, sliceNumber], self.sliceSplineUpper[:, 1, sliceNumber], marker='o')
            figSpline.scatter(
                self.sliceSplineLower[:, 0, sliceNumber], self.sliceSplineLower[:, 1, sliceNumber], marker='o')
            
            figSpline.show()

        self.width = self.slicingObj[np.argmax(self.slicingObj[:, 1]), 1] - self.slicingObj[np.argmin(self.slicingObj[:, 1]), 1]
        # self.width = abs(np.amax(self.ptCloudSectionRight[:, 0]) - np.amin(self.ptCloudSectionLeft[:, 0]))
        
        # print("sliceLeft: " + str(np.argmax(self.ptCloudSectionLeft[:, 0])) + ", " + str(np.argmin(self.ptCloudSectionLeft[:, 0])))
        # print("sliceRight: " + str(np.argmax(self.ptCloudSectionRight[:, 0])) + ", " + str(np.argmin(self.ptCloudSectionRight[:, 0])))
        self.height = self.slicingObj[np.argmax(self.slicingObj[:, 2]), 2] - self.slicingObj[np.argmin(self.slicingObj[:, 2]), 2]
        # self.height = np.amax(self.ptCloudObjHeightUpper[:,2]) * 2
        # print("width:" + self.width)
        # print("height: " + self.height)
        return self.slicingObj, self.objVolume, self.totalLength, self.width, self.height

    def imgChart_3d(self):
        imgObjEdgeUpper = np.array(self.edgeObjUpper)
        imgObjEdgeMiddle = np.array(self.edgeObjMiddle)
        imgObjEdgeLower = np.array(self.edgeObjLower)
        imgShadowEdgesUpper = np.array(self.edgesShadowUpper)
        imgShadowEdgesLower = np.array(self.edgesShadowLower)

        figIMG = plot.figure()
        imageCoordinate = plot.axes(projection='3d')

        imageCoordinate.scatter(imgObjEdgeUpper[:, 0], imgObjEdgeUpper[:, 1],
                                imgObjEdgeUpper[:, 2], s=[0.1], label='Upper Edge')
        imageCoordinate.scatter(imgObjEdgeMiddle[:, 0], imgObjEdgeMiddle[:, 1],
                                imgObjEdgeMiddle[:, 2], s=[0.1], label='Middle Edge')
        imageCoordinate.scatter(imgObjEdgeLower[:, 0], imgObjEdgeLower[:, 1],
                                imgObjEdgeLower[:, 2], s=[0.1], label='Lower Edge')
        imageCoordinate.scatter(imgShadowEdgesLower[:, 0], imgShadowEdgesLower[:, 1],
                                imgShadowEdgesLower[:, 2], s=[0.1], label='Shadow Lower Edge')
        imageCoordinate.scatter(imgShadowEdgesUpper[:, 0], imgShadowEdgesUpper[:, 1],
                                imgShadowEdgesUpper[:, 2], s=[0.1], label='Shadow Upper Edge')
        # draw line from virtual light source position to head and tail shadow position
        # shadow head
        for i in range(0, imgShadowEdgesUpper.shape[0], 100):
            imageCoordinate.plot([self.posVirlightIMG[0], imgShadowEdgesUpper[i, 0]], [self.posVirlightIMG[1], imgShadowEdgesUpper[i, 1]],
                                 [self.posVirlightIMG[2], imgShadowEdgesUpper[i, 2]])
        imageCoordinate.set_xlabel('x (Pixels)')
        imageCoordinate.set_ylabel('y (Pixels)')
        imageCoordinate.set_zlabel('z (mm)')
        imageCoordinate.legend()

        figIMG.show()

    def worldChart_3d(self):
        worldObjEdgeUpper = np.array(self.edgeObjUpperWorld)
        worldObjEdgeMiddle = np.array(self.edgeObjMiddleWorld)
        worldObjEdgeLower = np.array(self.edgeObjLowerWorld)
        worldShadowEdgesUpper = np.array(self.edgesShadowUpperWorld)
        worldShadowEdgesLower = np.array(self.edgesShadowLowerWorld)

        figWorld = plot.figure()
        worldCoordinate = plot.axes(projection='3d')
        worldCoordinate.scatter(worldObjEdgeUpper[:, 0], worldObjEdgeUpper[:, 1],
                                worldObjEdgeUpper[:, 2], s=[0.1], label='Upper Edge')
        worldCoordinate.scatter(worldObjEdgeMiddle[:, 0], worldObjEdgeMiddle[:, 1],
                                worldObjEdgeMiddle[:, 2], s=[0.1], label='Middle Edge')
        worldCoordinate.scatter(worldObjEdgeLower[:, 0], worldObjEdgeLower[:, 1],
                                worldObjEdgeLower[:, 2], s=[0.1], label='Lower Edge')
        worldCoordinate.scatter(worldShadowEdgesLower[:, 0], worldShadowEdgesLower[:, 1],
                                worldShadowEdgesLower[:, 2], s=[0.1], label='Shadow Lower Edge')
        worldCoordinate.scatter(worldShadowEdgesUpper[:, 0], worldShadowEdgesUpper[:, 1],
                                worldShadowEdgesUpper[:, 2], s=[0.1], label='Shadow Upper Edge')
        # draw line from virtual light source position to head and tail shadow position
        # shadow head
        for i in range(0, worldShadowEdgesUpper.shape[0], 100):
            worldCoordinate.plot([self.posVirlightWorld[0], worldShadowEdgesUpper[i, 0]], [self.posVirlightWorld[1], worldShadowEdgesUpper[i, 1]],
                                 [self.posVirlightWorld[2], worldShadowEdgesUpper[i, 2]])
        worldCoordinate.set_xlabel('x (mm)')
        worldCoordinate.set_ylabel('y (mm)')
        worldCoordinate.set_zlabel('z (mm)')
        worldCoordinate.legend()

        figWorld.show()

    def pointCloudChart_3d(self):
        figPointCloud = plot.figure()
        pointCloudChart = plot.axes(projection='3d')

        pointCloudChart.scatter(self.ptCloudSectionLeft[:, 0], self.ptCloudSectionLeft[:, 1],
                                self.ptCloudSectionLeft[:, 2], s=[0.1], label='Section Left')
        pointCloudChart.scatter(self.ptCloudSectionRight[:, 0], self.ptCloudSectionRight[:, 1],
                                self.ptCloudSectionRight[:, 2], s=[0.1], label='Section Right')
        pointCloudChart.scatter(self.ptCloudObjHeightUpper[:, 0], self.ptCloudObjHeightUpper[:, 1],
                                self.ptCloudObjHeightUpper[:, 2], s=[0.1], label='Section Middle Upper')
        pointCloudChart.scatter(self.ptCloudObjHeightLower[:, 0], self.ptCloudObjHeightLower[:, 1],
                                self.ptCloudObjHeightLower[:, 2], s=[0.1], label='Section Middle Lower')

        pointCloudChart.set_xlabel('x (mm)')
        pointCloudChart.set_ylabel('y (mm)')
        pointCloudChart.set_zlabel('z (mm)')
        pointCloudChart.legend()

        figPointCloud.show()

    def volumeChart(self, processTime):
        processTime = round(processTime, 3)
        # figVolume = plot.figure()
        # volumeChart = plot.axes(projection='3d')
        # volumeChart.scatter(
        #     self.slicingObj[:, 0], self.slicingObj[:, 1], self.slicingObj[:, 2], s=[0.1], label='spline cloud')
        # volumeChart.set_xlabel('x (mm)')
        # volumeChart.set_ylabel('y (mm)')
        # volumeChart.set_zlabel('z (mm)')
        # volumeChart.legend()

        # figVolume.show()
        fig = go.Figure(data=[go.Scatter3d(x=self.slicingObj[:, 0], y=self.slicingObj[:, 1], z=self.slicingObj[:, 2],
                                           mode='markers',
                                           marker=dict(
            size=2,
            # set color to an array/list of desired values
            color=self.slicingObj[:, 1],
            colorscale='Viridis',   # choose a colorscale
            opacity=0.8
        ))])

        fig.update_layout(
            autosize=True,
            width=1800,
            height=1000,
            scene=dict(xaxis=dict(title='length (mm)'), yaxis=dict(title='width (mm)'), zaxis=dict(title='height (mm)'),
                       aspectratio=dict(x=1.5, y=0.8, z=0.25)
                       ),
            title_text=(
                f'Volume estimate : {self.objVolume} cm^3 with computation time : {processTime}s on 6k resolution'),
            title_font_color="red",
            title_font_size=24,
        )
        fig.show()
