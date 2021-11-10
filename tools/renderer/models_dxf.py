#!/usr/bin/env python3
import sys
import os
import json
import math
from .canvas import CvCanvas, JsonCanvas 
from .dxfwriter import DxfCanvas

lineColor = 'static_fixtures'
body_lenth = {'forklift':1150,
              'manup':1150
              }
def draw_agv (bbox, direction, dxf):

    with dxf.style(lineColor = lineColor):
        dxf.path(bbox, closed = True)
    pass

def draw_forklift (bbox, direction, dxf):
    
    adjust_direction(bbox, direction, body_lenth['forklift'], dxf)
    
    pass

def draw_conveyor (bbox, direction, dxf):

    lineColor = 'conveyor'
    x0, y0, x1, y1 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]

    if direction == 'upwards' or direction == 'downwards': 
        side1 = [[x0, y0], [x0 + 50, y0], [x0 + 50, y1], [x0, y1]]
        side2 = [[x1 - 50, y0], [x1, y0], [x1, y1], [x1 - 50, y1]]
        line1 = [[x0, y0], [x1, y0]]
        line2 = [[x0, y1], [x1, y1]]
        middle = [[(x0+x1)/2 , y0], [(x0+x1)/2, y1]]

    else:
        side1 = [[x0, y0], [x0, y0 + 50], [x1, y0 + 50], [x1, y0]]
        side2 = [[x0, y1], [x0, y1 - 50], [x1, y1 - 50], [x1, y1]]
        line1 = [[x0, y0], [x0, y1]]
        line2 = [[x1, y0], [x1, y1]]
        middle = [[x0, (y0+y1)/2], [x1, (y0+y1)/2]]  


    with dxf.style(lineColor = lineColor):
        dxf.path(side1, closed = True)
        dxf.path(side2, closed = True)
        dxf.path(middle)

    lineColor = 'conveyor_side'
    with dxf.style(lineColor = lineColor):
        dxf.path(line1)
        dxf.path(line2)        
    pass

def draw_manup (bbox, direction, dxf):

    adjust_direction(bbox, direction, body_lenth['manup'], dxf)
    pass

def adjust_direction (bbox, direction, blen, dxf):

    fork1 = []
    fork2 = []
    if direction == 'downwards':
        bbox[0][1] += blen
        bbox[1][1] += blen
        x0, y0, x1, y1 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]
        fork1 = [[x0, y0], [x0, y0 - blen], [x0 + 200, y0 - blen], [x0 + 200, y0]]
        fork2 = [[x1, y0], [x1, y0 - blen], [x1 - 200, y0 - blen], [x1 - 200, y0]]

    elif direction == "leftwards":
        bbox[0][0] += blen
        bbox[3][0] += blen   
        x0, y0, x1, y1 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]
        fork1 = [[x0, y0], [x0 - blen, y0], [x0 - blen, y0 + 200], [x0, y0 + 200]]
        fork2 = [[x0, y1], [x0 - blen, y1], [x0 - blen, y1 - 200], [x0, y1 - 200]]

    elif direction == "upwards":
        bbox[2][1] -= blen
        bbox[3][1] -= blen
        x0, y0, x1, y1 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]
        fork1 = [[x0, y1], [x0, y1 + blen], [x0 + 200, y1 + blen], [x0 + 200, y1]]
        fork2 = [[x1, y1], [x1, y1 + blen], [x1 - 200, y1 + blen], [x1 - 200, y1]]

    elif direction == "rightwards":
        bbox[1][0] -= blen
        bbox[2][0] -= blen   
        x0, y0, x1, y1 = bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]
        fork1 = [[x1, y0], [x1 + blen, y0], [x1 + blen, y0 + 200], [x1, y0 + 200]]
        fork2 = [[x1, y1], [x1 + blen, y1], [x1 + blen, y1 - 200], [x1, y1 - 200]]

    with dxf.style(lineColor = lineColor):
        dxf.path(bbox, closed = True)
        dxf.path(fork1, closed = True)
        dxf.path(fork2, closed = True)
        dxf.path([[x0, y0], [x1, y1]])
        dxf.path([[x0, y1], [x1, y0]])
    

def draw_platform(bbox, direction, dxf):

    lineColor = 'platform'
    with dxf.style(lineColor = lineColor):
        dxf.path(bbox, closed = True)
    pass

METHODS = {}
METHODS['AGV'] = draw_agv
METHODS['forklift'] = draw_forklift
METHODS['convey_line'] = draw_conveyor
METHODS['manup_truck'] = draw_manup
METHODS['platform'] = draw_platform

def init_static_models (jsonfile, dxfpath, outpath):

    with open(jsonfile, "r") as f:
        plan = json.loads(f.read())
    output = {}

    dxf = DxfCanvas(dxfpath)
    
    with dxf.layer('WDA_STATIC_FIXTURES'):

        for item in plan:
            points = item['points']
            model = item['model']
            direction = item['direction']
            x0, y0 = points[0][0], points[0][1]
            x1, y1 = points[1][0], points[1][1]
            bbox = [[x0, y0], [x1, y0], [x1, y1], [x0,y1]]

            method = METHODS[model]
            method(bbox, direction, dxf)
            
    if outpath == None:
        outpath = ""

    outpath = os.path.join (outpath, "design.dxf")
    dxf.save(outpath)

if __name__ == '__main__':
    #path = os.path.abspath(os.path.dirname(__file__))
    #default_session_path = os.path.abspath(os.path.join(path, "session"))

    jsonfile = sys.argv[1]
    output_dir = sys.argv[2]

    init_static(jsonfile, output_dir)
