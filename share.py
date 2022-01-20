# pip3 install svglib

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

drawing = svg2rlg('share.svg')
renderPM.drawToFile(drawing, 'share.png', fmt='PNG')
