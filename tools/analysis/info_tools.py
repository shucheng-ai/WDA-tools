import numpy as np

def compute_quantity (plan, stype):
    
    if stype == 'stack':
        return compute_quantity_stack (plan['packages']['children'])
    elif stype == 'shelf':
        return compute_quantity_shelf (plan['packages']['children'])
    else:
        return compute_quantity_apr (plan['packages']['children'])

def compute_quantity_stack (packages):
    
    counter = 0
    for row in packages:
        for stack in row['children']:
            if 'children' in stack :
                for unit in stack['children']:
                    counter += (len(unit['children']))
    
    return counter

def compute_quantity_apr (packages):
    
    counter = 0
    for row in packages:
        for stack in row['children']:
            if 'children' in stack :
                for unit in stack['children']:
                    counter += (len(unit['children']))
    
    return counter

def compute_quantity_shelf (packages):
    
    counter = 0
    for row in packages:
        for stack in row['children']:
            if 'children' in stack :
                counter += (len(stack['children']))
    
    return counter

def compute_rackspec (plan, stype):

    rackspec = {}
    if stype == 'stack':
        return {}

    uprights = plan['skeleton']['upright']
    beams = plan['skeleton']['beam']

    
    unit= uprights[0]
    beam = beams[0]

    rackspec['bay_depth'] = max( unit[1][1][0] - unit[0][0][0], unit[1][1][1] - unit[0][0][1])
    rackspec['upright_counts'] = len( uprights )
    rackspec['upright_width'] = min( unit[1][1][0] - unit[0][0][0], unit[1][1][1] - unit[0][0][1])


    return rackspec

def compute_polygon_area ( polygon, type = ""):

    pts = polygon
    x = []
    y = []
    
    for id in range(len(pts)):
        x.append(pts[id][0])
        y.append(pts[id][1])

    size = 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
    return size
    
    
