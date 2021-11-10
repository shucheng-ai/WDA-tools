from collections import defaultdict
from .geometry import Box, Box3D
from shapely.geometry import Polygon

upright_color = {
    'apr': 'aprupright',
    'shelf':'shelfupright',
    'mezzanine':'mezzanineupright'
}


def draw_fixtures (scene, canvases):

    plan = scene['top_view']

    for i in plan:
        t = i['color']
            
        if t == 'wall' or t == 'obstacle':
            continue
            
        p = i['points']

        with canvases.style(lineColor=t):
            canvases.path(p, closed=True)
            
    pass

def draw_walls (scene, canvases):

    plan = scene['top_view']

    for i in plan:
        t = i['color']
 
        if t != 'wall':
            continue
        p = i['points']

        with canvases.style(lineColor=t):
            canvases.path(p, closed=True)
    
    pass
    
def draw_test_fixtures (scene, canvases):

    plan = scene['top_view']
    wall, column, door = [], [], []

    for i in plan:
        t = i['color']
        p = i['points']

        if t == 'wall':
            wall.append(p)
        elif t == 'door' or t == 'dock' or t == 'exit':
            door.append(p)
        elif t == 'column' or t == 'misc_column':
            column.append(p)

    with canvases.layer('WDA_PARSE_WALL'):
        with canvases.style(lineColor='wall_parse'):
            for item in wall:
                canvases.path(item)

    with canvases.layer('WDA_PARSE_COLUMN'):
        with canvases.style(lineColor='column_parse'):
            for item in column:
                canvases.path(item)

    with canvases.layer('WDA_PARSE_DOOR'):
        with canvases.style(lineColor='door_parse'):
            for item in door:
                canvases.path(item)
        




def draw_top_view_skeleton (plan, moving_paths, stype, canvases):

    empty_underpass = False
    if moving_paths == [] or stype == 'shelf':
        empty_underpass = True

    for uprights in plan['upright']:
        upright1, upright2 = uprights[0], uprights[1]
        
        box3d = get_pairs_box(upright1, upright2)
        box = box3d.drop(2)
        [x0, y0], [x1, y1] = box.unpack() #获得upright水平坐标

        if not empty_underpass and in_moving_path(x0, y0, x1, y1, moving_paths):
            lineColor = 'underpass'
        else:
            lineColor = upright_color[stype]
            
        with canvases.style(lineColor = lineColor):
            package = ((x0,y0),(x0,y1),(x1,y1),(x1,y0))
            canvases.path(package, closed = True)   

    if (y1 - y0) < (x1 - x0): #判断货架方向，获得beam应该减去的宽度
        rotation = False
        beam_with = upright1[1][1] - upright1[0][1]
    else:
        rotation = True
        beam_with = upright1[1][0] - upright1[0][0]

    
    beam_set = []
    underpass = []


    for beams in plan['beam']:
        beam1, beam2 = beams[0], beams[1]
        box3d = get_pairs_box(beam1, beam2)
        box = box3d.drop(2)
        [x0, y0], [x1, y1] = box.unpack()  
    

        if rotation == False: #水平和垂直货架的不同摆放方式
            line1 = ((x0,y0 + beam_with), (x0, y1 - beam_with))
            line2 = ((x1,y0 + beam_with), (x1, y1 - beam_with))
        else:
            line1 = ((x0 + beam_with, y0 ), (x1 - beam_with, y0))
            line2 = ((x0 + beam_with, y1), (x1 - beam_with, y1))       

        if not empty_underpass and in_moving_path(x0, y0, x1, y1, moving_paths): #如果是underpass
            underpass.append(line1)
            underpass.append(line2)         
        else: #如果不是underpass
            beam_set.append(line1)
            beam_set.append(line2)

    #由于垂直方向上多个beam只需要画一次，画图去重
    beam_set = list(set(beam_set))
    underpass = list(set(underpass))

    with canvases.style(lineColor = stype):

        for item in beam_set:
            canvases.path(item)

    with canvases.style(lineColor = 'underpass'):
        for item in underpass:
            canvases.path(item)

    return canvases        



def draw_top_view_stack (plan, canvases):

    for region in plan['children']:
        for row in region['children']:
            for stack in row['children']:
                for unit in stack['children']:
                    box3d = Box3D(unit['box'][0], unit['box'][1])
                    box = box3d.drop(2)
                    [x0, y0], [x1, y1] = box.unpack()
                    lineColor = 'stack'
                    with canvases.style(lineColor = lineColor):
                        package = [[x0,y0],[x0,y1],[x1,y1],[x1,y0]]
                        canvases.path(package, closed = True)  
                        canvases.path([[x0,y0],[x1,y1]], closed = False) 
                        canvases.path([[x0,y1],[x1,y0]], closed = False) 
                    pass
    pass

def draw_side_upright (stype, params, canvases):
    lineColor = upright_color[stype]

    overhang = (params["storage_depth"] - params["package_depth"])/2
    upright_depth = params["upright_depth"]
    row_depth = params["row_depth"]
 
    #upright, x0最左侧坐标，x1最右侧坐标
    [x0, y0], [x1, y1] = canvases.bbox.unpack()
    y1 = params["upright_height"]
    uprights = []
    for row in range(row_depth):
        #单stack外侧立柱
        x0 -= overhang
        x1 += overhang
        uprights.append(expand(x0, y0, x0 + upright_depth, y1))
        uprights.append(expand(x1, y0, x1 - upright_depth, y1))
        #单stack内侧立柱
        x0 += params["storage_depth"] - upright_depth
        x1 -= params["storage_depth"] - upright_depth
        uprights.append(expand(x0, y0, x0 + upright_depth, y1))
        uprights.append(expand(x1, y0, x1 - upright_depth, y1))     
        x0 -= overhang - upright_depth
        x1 += overhang - upright_depth

  
    with canvases.style(lineColor = lineColor):
        for upright in uprights:
            canvases.path(upright, closed = True)


def draw_side_unit (stype, params, canvases):
    lineColor = "solid_line"

    upright_height = params["upright_height"]
    package_height = params["package_height"]
    floor_clearance = params["floor_clearance"]
    upward_clearance = params["upward_clearance"]
    row_depth = params["row_depth"]
    package_depth = params["package_depth"]
    beam_height = params["beam_height"]
    layers_per_stack = params["layers_per_stack"]
    overhang = (params["storage_depth"] - params["package_depth"])/2
    upright_depth = params["upright_depth"]

    packages = []
    beams = []
    cross = []
    x0 = 0
    stack_counter = 0

    for depth in range(2):
        for stack in range(row_depth):
            stack_counter += 1
            if floor_clearance>0:
                y0 = floor_clearance + beam_height
                #beams.append(expand(x0, y0, x0 + package_depth, y0 - beam_height))
            else:
                y0 = 0
            
            left_upright = x0 - overhang + upright_depth
            right_upright =x0 + package_depth + overhang - upright_depth
            if stype == 'shelf':
                beams.append(expand(x0, upright_height, x0 + package_depth, upright_height - beam_height))
            elif stype == "apr":
                beams.append(expand(left_upright, upright_height, right_upright, upright_height - beam_height ))

            for layer in range(layers_per_stack):

                x1 = x0 + package_depth
                y1 = y0 + package_height
                packages.append(expand(x0, y0, x1, y1))
                
                #画横梁
                if layer > 0 or floor_clearance>0:
                    beams.append(expand(left_upright, y0, right_upright, y0 - beam_height))

                #画斜撑
                if layer == layers_per_stack - 1:
                    continue

                direction = (layer + stack_counter) % 2
                if direction == 0:
                    cross.append([[left_upright, y0], [right_upright, y1 + upward_clearance]])
                else:
                    cross.append([[left_upright, y1 + upward_clearance], [right_upright, y0]])

                y0 += package_height +upward_clearance + beam_height
            x0 += package_depth
        x0 += params["storage_gap"]


    with canvases.style(lineColor = 'frame'):
        for package in packages:
            pass
            canvases.path(package, closed = True)

    with canvases.style(lineColor = stype):
        for beam in beams:
            canvases.path(beam, closed = True)
        for line in cross:
            canvases.path(line, closed = False)
    pass

def draw_side_view_apr (params, canvases):
    
    unit_height = params["package_height"] + params["upward_clearance"] + params["beam_height"]
    params["layers_per_stack"] = (params["upright_height"] - params["floor_clearance"]) // unit_height +1
    params["row_depth"] = params["apr_depth"]
    draw_side_upright ("apr", params, canvases)
    draw_side_unit ("apr", params, canvases) 
    pass

def draw_side_view_shelf (params, canvases):

    unit_height = params["package_height"] + params["upward_clearance"] + params["beam_height"]
    params["layers_per_stack"] = (params["upright_height"]) // unit_height
    params["row_depth"] = params["shelf_depth"]
    draw_side_upright ("shelf", params, canvases)
    draw_side_unit ("shelf", params, canvases) 
    pass

def draw_side_view_stack (params, canvases):

    lineColor = "solid_line"

    stack_depth = params["stack_depth"]
    package_layers = params["package_layers"]
    package_depth = params["package_depth"]
    package_height = params["package_height"]
    package_gap = params["package_gap"]
    
    packages = []
    cross = []
    x0 = 0

    for depth in range(2):
        for stack in range(stack_depth):
            y0 = 0
            for layer in range(package_layers):

                x1 = x0 + package_depth
                y1 = y0 + package_height

                #确定stack货物和斜线的位置
                packages.append(expand(x0, y0, x1, y1))
                cross.append([[x0, y1], [x1, y0]])
                cross.append([[x0, y0], [x1, y1]])

                y0 += package_height
            x0 += package_depth
        x0 += package_gap

    #在画布上画stack和斜线
    with canvases.style(lineColor = lineColor):
        for package in packages:
            canvases.path(package, closed = True)

        for line in cross:
            canvases.path(line, closed = True)

    pass

def draw_side_view_lss (params, canvases):
    pass

def draw_side_view_mezzanine (params, canvases):
    pass

def draw_front_upright (stype, params, canvases):

    upright_width = params["upright_width"]
    storage_width = params["storage_width"]

    #upright, x0最左侧坐标，x1最右侧坐标
    x0, y0, x1, y1 = 0, 0, upright_width, params["upright_height"]
    uprights = []
    uprights.append(expand(x0, y0, x1, y1))

    for side in range(2):
        x0 += storage_width - upright_width
        x1 = x0 + upright_width
        uprights.append(expand(x0,y0,x1,y1))

        pass
  
    with canvases.style(lineColor = upright_color[stype]):
        for upright in uprights:
            canvases.path(upright, closed = True)


def draw_front_unit (stype, params, canvases):
    lineColor = "solid_line"

    upright_height = params["upright_height"]
    upright_width = params["upright_width"]

    package_height = params["package_height"]
    floor_clearance = params["floor_clearance"]
    upward_clearance = params["upward_clearance"]
    package_width = params["package_width"]
    beam_height = params["beam_height"]
    layers_per_stack = params["layers_per_stack"]
    pallet_per_face = params["pallet_per_face"] 
    storage_width = params["storage_width"]

    gap = (storage_width - pallet_per_face * package_width) // (pallet_per_face + 1)

    if gap != params["package_gap"] :
        print("calculated package gap value:", gap, "// package gap value from params:", params["package_gap"])
        if gap < 0:
            return
    packages = []
    beams = []
    cross = []
    x0 = 0
    x_start = 0

    for side in range(2):

        if floor_clearance>0:
            y0 = floor_clearance + beam_height
            beams.append(expand(x0 + upright_width, y0, x0 + storage_width - upright_width, y0 - beam_height))
        else:
            y0 = 0    

        if stype == 'shelf':
            beams.append(expand(x0, upright_height, x0 + storage_width - upright_width, upright_height - beam_height))        
            
        for layer in range(layers_per_stack):

            #判断 underpass
            if side > 0 and stype == 'apr':
                if y0 - beam_height< params["underpass_height"]:
                    y0 += package_height + upward_clearance + beam_height
                    continue
            #画横梁
            x0 = x_start +gap
            if layer > 0 or floor_clearance>0:
                beams.append(expand(x_start + upright_width, y0, x_start + storage_width - upright_width, y0 - beam_height))
            
            for unit in range(pallet_per_face):

                #画包裹
                x1 = x0 + package_width
                y1 = y0 + package_height
                packages.append(expand(x0, y0, x1, y1 ))

                #cross
                cross.append([[x0,y0],[x1,y1]])
                cross.append([[x0,y1],[x1,y0]])

                x0 += package_width + gap 
            y0 += package_height + upward_clearance + beam_height
        x_start += storage_width - upright_width


    with canvases.style(lineColor = "frame"):
        for package in packages:
            canvases.path(package, closed = False)
        for line in cross:
            canvases.path(line, closed = False)

    with canvases.style(lineColor = stype):
        for beam in beams:
            canvases.path(beam, closed = True)
              
    pass

def draw_front_view_apr (params, canvases):
    unit_height = params["package_height"] + params["upward_clearance"] + params["beam_height"]
    params["layers_per_stack"] = (params["upright_height"] - params["floor_clearance"]) // unit_height +1
    params["row_depth"] = params["apr_depth"]
    draw_front_upright ("apr", params, canvases)
    draw_front_unit ("apr", params, canvases) 
    pass

def draw_front_view_shelf (params, canvases):
    unit_height = params["package_height"] + params["upward_clearance"] + params["beam_height"]
    params["layers_per_stack"] = (params["upright_height"]) // unit_height
    draw_front_upright ("shelf", params, canvases)
    draw_front_unit ("shelf", params, canvases) 

    pass

def draw_front_view_stack (params, canvases):

    lineColor = "solid_line"

    package_layers = params["package_layers"]
    package_width = params["package_width"]
    package_height = params["package_height"]
    package_gap = params["package_gap"]
    
    packages = []
    cross = []
    x0 = 0

    for depth in range(2):
        for stack in range(1):
            y0 = 0
            for layer in range(package_layers):

                x1 = x0 + package_width
                y1 = y0 + package_height

                #确定stack货物和斜线的位置
                packages.append(expand(x0, y0, x1, y1))
                cross.append([[x0, y1], [x1, y0]])
                cross.append([[x0, y0], [x1, y1]])

                y0 += package_height
            x0 += package_width
        x0 += package_gap

    #在画布上画stack和斜线
    with canvases.style(lineColor = lineColor):
        for package in packages:
            canvases.path(package, closed = True)

        for line in cross:
            canvases.path(line, closed = True)

    pass
    pass

def draw_front_view_mezzanine (params, canvases):
    pass

def draw_front_view_lss (params, canvases):
    pass

def draw_top_view (packages, skeleton, moving_paths, stype, canvases):
    #draw_top_view_apr (packages, canvases)

    if stype=='stack':
        draw_top_view_stack (packages, canvases)
    else:
        draw_top_view_skeleton (skeleton, moving_paths, stype, canvases)

def do_nothing (params, canvases):
    pass

METHODS = {
    # 所有画模块的函数都分们别类存在这里
    # METHOD[view][base_rack] 是API和do_nothing一样的画画函数
        'top': defaultdict(lambda: do_nothing),
        'front': defaultdict(lambda: do_nothing),
        'side': defaultdict(lambda: do_nothing),
        'fixtures': defaultdict(lambda: do_nothing),

}
def handler (view, base_rack, params, canvases):
    # 按rack type & view找到画画函数
    canvases.fill_with_white()
    method = METHODS[view][base_rack]
    method(params, canvases)
    pass

# 注册画画函数
def register (view, base_rack):
    def wrap (func):
        METHODS[view][base_rack] = func
        return func
    return wrap

def get_bbox(view, base_rack, params):

    #计算画图的画布大小
    if base_rack == "apr":
        depth = params["apr_depth"]
    elif base_rack == "shelf":
        depth = params["shelf_depth"]
    elif base_rack == "stack":
        depth = params["stack_depth"]
        
        if view == "side":
            x1 = (params["package_depth"] * depth) *2 + params["package_gap"]
        else:
            x1 = params["package_width"] * 2 + params["package_gap"]

        y1 = params["package_height"] * params["package_layers"]
        
        bbox = Box([0, 0],[x1, y1])
        return bbox

    if view == "side":
        x1 = (params["package_depth"] * depth)*2 + params["storage_gap"]
    else:
        x1 = params["storage_width"] * 2

    y1 = params["upright_height"] + params["package_height"]

    bbox = Box([0, 0],[x1, y1])
    return bbox

def expand(x0, y0, x1, y1):
    return ([[x0, y0], [x0, y1], [x1,y1], [x1,y0]])

def get_pairs_box(box1, box2):
    
    minbox = []
    maxbox = []
    for i in range(3):
        minbox.append( min(box1[0][i],box2[1][i]) )
        maxbox.append( max(box1[0][i],box2[1][i]))
    box3d = Box3D(minbox, maxbox)
    return box3d

def in_moving_path (x0, y0, x1, y1, paths):

    beam = Polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])

    for pts in paths:
        path = Polygon([(pts[0][0], pts[0][1]), (pts[0][0], pts[1][1]), (pts[1][0], pts[1][1]), (pts[0][0], pts[1][1])])
        if path.intersects(beam):
            return True

    return False

METHODS['side']['apr'] = draw_side_view_apr
METHODS['side']['stack'] = draw_side_view_stack
METHODS['side']['shelf'] = draw_side_view_shelf
METHODS['side']['lss'] = draw_side_view_lss
METHODS['side']['mezzanine'] = draw_side_view_mezzanine

METHODS['front']['apr'] = draw_front_view_apr
METHODS['front']['stack'] = draw_front_view_stack
METHODS['front']['shelf'] = draw_front_view_shelf
METHODS['front']['lss'] = draw_front_view_lss
METHODS['front']['mezzanine'] = draw_front_view_mezzanine
