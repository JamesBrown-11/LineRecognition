from core.LineIdentification import LineIdentification

import os

IMAGES_DIR = os.getcwd() + "\\images"

if __name__ == '__main__':
    identifier = LineIdentification()

    images = os.listdir(IMAGES_DIR)
    identifier.edge_detection(IMAGES_DIR + "\\" + images[0])
    #identifier.extract_pixels(IMAGES_DIR + "\\" + images[0])
    #identifier.find_lines()
    #identifier.show_img()