#!/usr/bin/env python3
#coding:utf-8
from .info_tools import compute_quantity, compute_rackspec, compute_polygon_area 
import numpy as np

def __basic_info (name, value) :
    return {
        'name' : name,
        'value' : value,
        'type' : 'basic'
    }

def connection_info (con, type = "", params = {}) :
    #各种影响通道的因素

    info = {}

    box = con['box']
    x0, y0, x1, y1 = box[0][0], box[0][1], box[1][0], box[1][1]
    direction = con['direction']

    info['size'] = __basic_info('size', str(x1 - x0) + 'mm*' + str(y1 - y0) + 'mm')
    info['width'] = __basic_info('width(mm)', y1 - y0 if direction[1] == 0 else x1 - x0)
    info['direction'] = __basic_info('direction', 'left-right' if direction[1] == 0 else 'bottom-top')

    return(info)

def collision_info (col, type = "", params = {}) :
    #表示各种障碍物
    info = {}
    col = np.array(col)
    x0 = np.min(col[:,0])
    y0 = np.min(col[:,1])
    x1 = np.max(col[:,0])
    y1 = np.max(col[:,1])

    info["area"] = __basic_info('area(m*m)', compute_polygon_area (col)/1000000)
    info['bounding_box'] = __basic_info('bounding box', str(x1 - x0) + 'mm*' + str(y1 - y0) + 'mm')

    return(info)

def region_info (region, stype, params = {}) :

    info = {}
    box = region
    x0, y0, x1, y1 = box[0][0], box[0][1], box[1][0], box[1][1]

    info['length'] = __basic_info('length', x1 - x0)
    info['width'] = __basic_info('width', y1 - y0)
    info['area'] = __basic_info('area(m*m)', (x1 - x0) * (y1 - y0) / 1000000)

    return(info)
 
def plan_info (plan, stype = "", params = {}) :
    
    info = {}
    box = plan['bbox']

    x0, y0, x1, y1 = box[0][0], box[0][1], box[1][0], box[1][1]
    info['area'] = __basic_info('area', (x1 - x0) * (y1 - y0) / 1000000)
    info['total_local_quantity'] = __basic_info('total local quantity', compute_quantity(plan, stype))
    info['rack_spec'] = __basic_info('rack spec', compute_rackspec(plan, stype))

    return(info)

def room_info (room, type = "", params = {}) :
    info = {}
    walls = np.array(room['walls'])
    if len(walls) == 0 : return {}
    x0 = np.min(walls[:,0])
    y0 = np.min(walls[:,1])
    x1 = np.max(walls[:,0])
    y1 = np.max(walls[:,1])

    info['area'] = __basic_info('area(m*m)', compute_polygon_area(walls) / 1000000)
    info['bounding_box'] = __basic_info('bounding box', str(x1 - x0) + 'mm*' + str(y1 - y0) + 'mm')

    return info
