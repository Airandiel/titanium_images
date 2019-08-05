import copy
import cv2
from math import *
import numpy as np
import os
# import pytesseract
from PIL import Image, ImageEnhance
from functools import partial

class AveragePicture:

    def preparePicture(self, image):
        #image = image.convert('L')
        image = np.array(image)  # convert image from pillow to cv
        image = cv2.resize(image, (320, 180))
        color_palette = np.array(self.readPalette())
        h, w = image.shape[:2]
        for y in range(h):
            for x in range(w):
                #image[y][x] = self.colorBestMatch(image[y][x], color_palette)
                image[y][x] = min(color_palette[:,1:4], key = partial(self.colorDifference, image[y][x]))
        Image.fromarray(image).save("image.png")
        # find edges on image the constants 250 and 300 are set good
        edges = self.makeEdges(image)

        Image.fromarray(edges).save("edges.png")
        # new_width = 250
        # # change the dimensions to width=250
        # h = int(h * new_width / w)
        # w = new_width
        # # B&W
        # drawing = np.zeros((h, w), np.uint8)
        # # make contours from edges and draw them
        # cv2.drawContours(edges, [box], 0, 150, 2)

    def convertPictureTo8Color(self, image_path):
        image = Image.open(image_path)
        image = np.array(image)  # convert image from pillow to cv
        image = cv2.resize(image, (320, 180))
        color_palette = np.array(self.readPalette(path="palette.txt"))
        h, w = image.shape[:2]
        the_best_colors = []
        best_color_distances =[]

        for i in range(8):      # we want to find 8 the best colors
            map_of_current_color = np.array([])
            the_best_colors.append([[0,0,0,0],0])
            color_distances = []
            for color in color_palette:
                color_distances = (image-color[1:4])*(image-color[1:4]) # calculate distance
                color_distances = color_distances[:, :, 0] + color_distances[:, :, 1] + color_distances[:, :, 2]
                how_well_fits = sum(sum(color_distances < 1000))
                if the_best_colors[i][1] < how_well_fits:
                    the_best_colors[i] = [color, how_well_fits]
                    map_of_current_color = color_distances < 1000
            color_palette = np.delete(color_palette, color_palette == the_best_colors[i][0], axis=0)
            image[map_of_current_color] = [3000,3000,3000]
            best_color_distances.append(color_distances)
        minimals = np.argmin(np.array(best_color_distances), axis=0) # indexes of palette on image
        for y in range(h):
            for x in range(w):
                image[y][x] = the_best_colors[minimals[y,x]][0][1:4]
        Image.fromarray(image).save("processed.png")

    def convertFrom8ColorPalette(self, image_path):
        image = Image.open(image_path)
        image = np.array(image)  # convert image from pillow to cv
        # image = cv2.resize(image, (320, 180))
        color_palette = np.array(self.readPalette(path="my_palette.txt"))
        h, w = image.shape[:2]
        color_distances = []
        # image *= image >= 0
        for color in color_palette:
            color_temp_distance = (image-color[1:4])*(image-color[1:4])
            color_temp_distance = color_temp_distance[:, :, 0] + color_temp_distance[:, :, 1] + color_temp_distance[:, :, 2]
            color_distances.append(color_temp_distance)
        minimals = np.argmin(np.array(color_distances), axis=0)
        for y in range(h):
            for x in range(w):
                image[y][x] = color_palette[minimals[y, x]][1:4]
        Image.fromarray(image).save("processed.png")


    def makeEdges(self, image):
        return cv2.Canny(image,1, 1, apertureSize=3)

    def makePalette(self):
        palette_picture = Image.open("palette.png")
        palette_picture = np.array(palette_picture)
        h, w = palette_picture.shape[:2]
        palette = []
        y = 1
        x = 1

        ### WRITING TO FILE
        with open("palette.txt", "w") as output_file:
            for cord_y in range(int(h / 16), h, int(h / 8)):
                for cord_x in range(int(w / 16), w, int(w / 8)):
                    duplicate = False
                    for elem in palette:
                        if elem[1] == palette_picture[cord_y][cord_x].tolist():
                            duplicate = True
                            break
                    if not duplicate:
                        palette.append([y * 10 + x, palette_picture[cord_y][cord_x].tolist()])
                        output_file.write("%d\t%d\t%d\t%d\n"% (y * 10 + x,
                                          palette_picture[cord_y][cord_x][0],
                                          palette_picture[cord_y][cord_x][1],
                                          palette_picture[cord_y][cord_x][2]))
                    x = x % 8 + 1
                y = y % 8 + 1

    def readPalette(self, path='palette.txt'):
        with open(path) as f:
            palette = []
            temp = [[int(x) for x in line.split()] for line in f]
            for elem in temp:
                # palette[str(elem[0])] = [elem[1], elem[2], elem[3]]
                # palette.append([elem[0], [elem[1], elem[2], elem[3]]])
                palette.append([elem[0], elem[1], elem[2], elem[3]])
        return palette
    # def readPalette(self):
    #     with open('paletteRGB.txt') as f:
    #         # w, h = [int(x) for x in next(f).split()]
    #         palette = [[int(x) for x in line.split()] for line in f]
    #         palette = sorted(palette)
    #         copy = []
    #         for index, elem in enumerate(palette):
    #             if (elem != palette[index - 1] and index > 0):
    #                 copy.append(elem)
    #         return copy

    def colorDistance(self, color1, color2):
        return sqrt(sum([(e1-e2)**2 for e1, e2 in zip(color1, color2)]))

    def colorBestMatch(self, sample, colors):
        by_distance = sorted(colors, key=lambda c: self.colorDistance(c, sample))
        return by_distance[0]

    def colorDifference(self, testColor, otherColor):
        # difference = 0
        # difference += abs(testColor[0]-otherColor[0])
        # difference += abs(testColor[1]-otherColor[1])
        # difference += abs(testColor[2]-otherColor[2])

        return sum([(e1-e2)**2 for e1, e2, in zip(testColor, otherColor)])

    def interval(color):
        if color > 255:
            return 255
        elif color < 0:
            return 0
        else:
            return int(color)


if __name__ == "__main__":
    # image = Image.open("purple.jpg")
    # # `
    # # AveragePicture().makePalette()`
    # print(AveragePicture().preparePicture(image))

    # image = Image.open("image.png")
    # Image.fromarray(AveragePicture().makeEdges(np.array(image))).save("edges.png")
    AveragePicture().convertFrom8ColorPalette("satelite.jpg")
