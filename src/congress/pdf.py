from logging import root
from pdf2image import convert_from_path

import re
import cv2 
import numpy as np
import pytesseract
from pytesseract import Output
from matplotlib import pyplot as plt

import os
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Any, Optional
import pdb


class OCR:
    def __init__(self):
        return
    # get grayscale image
    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(self, image):
        return cv2.medianBlur(image,5)
    
    #thresholding
    def thresholding(self, image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    #dilation
    def dilate(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.dilate(image, kernel, iterations = 1)
        
    #erosion
    def erode(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.erode(image, kernel, iterations = 1)

    #opening - erosion followed by dilation
    def opening(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    #canny edge detection
    def canny(self, image):
        """Ref:
        Canny filter: https://docs.opencv.org/3.4/da/d22/tutorial_py_canny.html
        """
        return cv2.Canny(image, 100, 200)

    #skew correction
    def deskew(self, image):
        """Ref:
        Angle of rotation [-90,0]: https://theailearner.com/tag/cv2-minarearect/
        """
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        """      
        dst = cv.warpAffine(src, M, dsize[, dst[, flags[, borderMode[, borderValue]]]] )
        src: input image
        M: Transformation matrix
        dsize: size of the output image
        flags: interpolation method to be used
        """
        rotated = cv2.warpAffine(
            image, 
            M,
            (w, h), 
            flags=cv2.INTER_CUBIC, 
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    #template matching
    def match_template(self, image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 
    
    def run(self, image, config=None):
        custom_config = r'--oem 3 --psm 6' 
        gray = self.get_grayscale(image)
        text = pytesseract.image_to_string(gray, config=custom_config)
        return text

class ReadPDF:
  """Class to extract text from PDFs. Document pages are converted to JPG and 
  then they go through OCR"""
  def __init__(self):
    self.ocr = OCR()
    return
  
  def extract_pages(self, file_path: str):
    """Convert PDF pages into JPG images"""
    images = convert_from_path(file_path, dpi=200)
    return images

  def extract_text(self, images):
    texts = []    
    for image in images:
      image = np.array(image)
      text = self.ocr.run(image)
      del image
      texts.append(text)
    return "\n".join(texts)

  def write_text(self, text, file_name):
    with open(file_name, 'w') as f:
      f.write(text)

  def run(self, root_path: str):
    if not os.path.exists(root_path):
        raise Exception(f"Path: {root_path} doesn't exist")
    
    pdfs = [f for f in os.listdir(root_path) if f.lower().endswith('.pdf')]
    print(f'Analyzing {len(pdfs)} PDFs files at: {root_path}')
    progress_bar = tqdm(pdfs)
    for pdf in progress_bar:
        file_path = os.path.join(root_path, pdf)
        progress_bar.set_description(f"File: {file_path}")
        pages = self.extract_pages(file_path)
        text = self.extract_text(pages)
        del pages

        output_path = Path(file_path)
        self.write_text(text, output_path.with_suffix('.txt'))
    return

if __name__ == "__main__":
    root_path = 'data/peru/laws/pdfs/'
    pdf_reader = ReadPDF() 
    pdf_reader.run(root_path=root_path)