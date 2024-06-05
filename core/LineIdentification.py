import math

from PIL import Image

import cv2
import numpy as np
import time

LINE_WIDTH = 10
SIGMA_L = 128
SIGMA_D = 20


class LineIdentification:
    def __init__(self):
        self.img = None
        self.pixels = None


    def extract_pixels(self, img):
        self.img = Image.open(img)
        self.pixels = self.img.load()


    def calculate_pixel_luminance(self, r, g, b):
        return (r * 0.2126) + (g * 0.7152) + (b * 0.0722)

    def find_lines(self):
        size = self.img.size

        for x in range(size[0]):
            for y in range(size[1]):
                current_pixel = self.pixels[x,y]
                pixel_r = self.pixels[x, y][0]
                pixel_g = self.pixels[x, y][1]
                pixel_b = self.pixels[x, y][2]
                pixel_luminance = self.calculate_pixel_luminance(pixel_r, pixel_g, pixel_b)
                # check if the rgb values of the pixel are white
                # each value must be greater tha 240
                if pixel_luminance >= SIGMA_L:
                    # Since this is considered a white pixel, determine if the pixels LINE_WIDTH linearly
                    # Must account for if the current pixel is near the left edge
                    left_most_x = max(x - LINE_WIDTH, 0)
                    right_most_x = min(x + LINE_WIDTH, size[0]-1)
                    top_most_y = max(y - LINE_WIDTH, 0)
                    bottom_most_y = min(y + LINE_WIDTH, size[1]-1)

                    left_most_pixel = self.pixels[left_most_x, y]
                    right_most_pixel = self.pixels[right_most_x, y]
                    top_most_pixel = self.pixels[x, top_most_y]
                    bottom_most_pixel = self.pixels[x, bottom_most_y]

                    left_most_pixel_luminance = self.calculate_pixel_luminance(left_most_pixel[0], left_most_pixel[1], left_most_pixel[2])
                    right_most_pixel_luminance = self.calculate_pixel_luminance(right_most_pixel[0], right_most_pixel[1], right_most_pixel[2])
                    top_most_pixel_luminance = self.calculate_pixel_luminance(top_most_pixel[0], top_most_pixel[1], top_most_pixel[2])
                    bottom_most_pixel_luminance = self.calculate_pixel_luminance(bottom_most_pixel[0], bottom_most_pixel[1], bottom_most_pixel[2])

                    if ((pixel_luminance - left_most_pixel_luminance >= SIGMA_D and pixel_luminance - right_most_pixel_luminance >= SIGMA_D)
                            or (pixel_luminance - top_most_pixel_luminance >= SIGMA_D and pixel_luminance - bottom_most_pixel_luminance >= SIGMA_D)):
                        # print('White line detection')
                        # If this check is passed, the candidate pixel is considered on a line
                        # TODO: We must exclude white pixels that are in textrued regions i.e. letters in logos, white areas in stadium, or spectators
                        # TODO: Hough Line Detection

                        self.img.putpixel((x, y), (0, 0, 0))
        self.img.show()

    def edge_detection(self, path):
        image = cv2.imread(path)
        size = image.shape

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        blurred = cv2.GaussianBlur(src=gray, ksize=(3,5), sigmaX=0.5)

        edges = cv2.Canny(blurred, 70, 135)

        # Apply HoughLinesP method to
        # to directly obtain line end points
        lines_list = []
        lines = cv2.HoughLinesP(
            edges,  # Input edge image
            1,  # Distance resolution in pixels
            np.pi / 180,  # Angle resolution in radians
            threshold=150,  # Min number of votes for valid line
            minLineLength=20,  # Min allowed length of line
            maxLineGap=300  # Max allowed gap between line for joining them
        )

        top_threshold_y = size[0] - int(size[0] * 0.95)
        bottom_threshold_y = size[0] * 0.95

        # Iterate over points
        count = 0
        for points in lines:
            # Extracted points nested in the list
            x1, y1, x2, y2 = points[0]

            if (y1 > top_threshold_y or y2 > top_threshold_y) and (y1 < bottom_threshold_y or y2 < bottom_threshold_y):
                # Draw the lines joining the points

                # Maintain a simples lookup list for points
                lines_list.append([(x1, y1), (x2, y2)])
                count += 1

        self.merge_line(lines_list)
        self.draw_line(lines_list, image)
        cv2.imwrite('modified.png', image)
        img = Image.open('modified.png')
        img.show()
        # time.sleep(10)
        print("Done")

    def merge_line(self, line_list):
        i = 0
        while i < len(line_list):
            line = line_list[i]
            x1, y1 = line[0]
            x2, y2 = line[1]
            slope = (y2-y1)/(x2-x1)

            j = 0
            while j < len(line_list)-1:
                if j != i:
                    other_line = line_list[j]
                    other_x1, other_y1 = other_line[0]
                    other_x2, other_y2 = other_line[1]
                    other_slope = (other_y2-other_y1)/(other_x2-other_x1)

                    slope_diff = abs(slope-other_slope)
                    if slope_diff < 0.5:
                        point_1_distance = math.sqrt((x1 - other_x1)**2 + (y1 - other_y1)**2)
                        point_2_distance = math.sqrt((x2 - other_x2)**2 + (y2 - other_y2)**2)

                        if point_1_distance < 25 and point_2_distance < 25:
                            del line_list[j]
                            j -= 1
                j += 1
            i += 1

    def draw_line(self, lines_list, image):
        count = 0
        for line in lines_list:
            x1, y1 = line[0]
            x2, y2 = line[1]

            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # font
            font = cv2.FONT_HERSHEY_SIMPLEX

            # org
            org = (int((x1 + x2) / 2), int((y1 + y2) / 2))

            # fontScale
            fontScale = 1

            # Blue color in BGR
            color = (255, 0, 0)

            # Line thickness of 2 px
            thickness = 1

            # Using cv2.putText() method
            image = cv2.putText(image, 'Line ' + str(count), org, font,
                                 fontScale, color, thickness, cv2.LINE_AA)
            count += 1