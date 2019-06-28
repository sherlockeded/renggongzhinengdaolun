#!/usr/bin/env python3
import re
import glob
import sys
import os
import hashlib
from multiprocessing import Pool
from subprocess import call

MAX_NUMBER = 150*1000

THREADS = 4

IMAGE_DIR = "formula_image1"
DATASET_FILE = "im2latex1.lst"
NEW_FORMULA_FILE = "im2latex_formulas1.lst"

# Running a thread pool masks debug output. Set DEBUG to 1 to run
# formulas over images sequentially to see debug errors more clearly
DEBUG = False

DEVNULL = open(os.devnull, "w")

BASIC_SKELETON = r"""
\documentclass[12pt]{article}
\pagestyle{empty}
\usepackage{amsmath}
\usepackage{xcolor}
\begin{document}

\begin{displaymath}
%s
\end{displaymath}

\end{document}
"""
RENDERING_SETUPS = {"basic": [BASIC_SKELETON,
                              "convert -density 200 -quality 100 -colorspace RGB %s.pdf %s.png",
                              lambda filename: os.path.isfile(filename + ".png")]
                   }

def remove_temp_files(name):
    """ Removes .aux, .log, .pdf and .tex files for name """
    os.remove(name+".aux")
    os.remove(name+".log")
    os.remove(name+".pdf")
    os.remove(name+".tex")


def formula_to_image(formula,rgb):
    """ Turns given formula into images based on RENDERING_SETUPS
    returns list of lists [[image_name, rendering_setup], ...], one list for
    each rendering.
    Return None if couldn't render the formula"""
    formula = formula.strip("%")
    #name = hashlib.sha1(formula.encode('utf-8')).hexdigest()[:15]
    name="latex"
    ret = []
    for rend_name, rend_setup in RENDERING_SETUPS.items():
        full_path = name + "_" + rend_name

        # Create latex source
        color = r'''\color[rgb]{''' + rgb+r'''}
        '''
        formula=color+formula
        latex = rend_setup[0] % formula
        # Write latex source
        with open(full_path + ".tex", "w") as f:
            f.write(latex)

        # Call pdflatex to turn .tex into .pdf
        code=-1


        code = call(["pdflatex", '-interaction=nonstopmode', '-halt-on-error', full_path + ".tex"],
                    stdout=DEVNULL, stderr=DEVNULL)
        if code != 0:
            os.system("rm -rf " + full_path + "*")
            return code

        # Turn .pdf to .png
        # Handles variable number of places to insert path.
        # i.e. "%s.tex" vs "%s.pdf %s.png"
        full_path_strings = rend_setup[1].count("%") * (full_path,)
        code = call((rend_setup[1] % full_path_strings).split(" "),
                    stdout=DEVNULL, stderr=DEVNULL)

        # Remove files
        try:
            remove_temp_files(full_path)
        except Exception as e:
            # try-except in case one of the previous scripts removes these files
            # already
            return -1

        # Detect of convert created multiple images -> multi-page PDF
        resulted_images = glob.glob(full_path + "-*")

        if code != 0:
            # Error during rendering, remove files and return None
            os.system("rm -rf " + full_path + "*")
            return code
        elif len(resulted_images) > 1:
            # We have multiple images for same formula
            # Discard result and remove files
            for filename in resulted_images:
                os.system("rm -rf " + filename + "*")
            return -1
        else:
            ret.append([full_path, rend_name])
    return code


def getimage(oneformula,rgb):

    try:
        os.mkdir(IMAGE_DIR)
    except OSError as e:
        pass  # except because throws OSError if dir exists
    print("Turning formulas into images...")

    # Change to image dir because textogif doesn't seem to work otherwise...
    oldcwd = os.getcwd()
    # Check we are not in image dir yet (avoid exceptions)
    if not IMAGE_DIR in os.getcwd():
        os.chdir(IMAGE_DIR)

    names = formula_to_image(oneformula,rgb)

    os.chdir(oldcwd)
    return names
if __name__ == '__main__':
    code=getimage(sys.argv[1],sys.argv[2])
    if(code!=0):
        exit(-1)
    else:
        exit(0)