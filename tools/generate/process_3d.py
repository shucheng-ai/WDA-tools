#!/usr/bin/env python3
# coding:utf-8
import open3d as o3d
import os
import numpy as np
import copy
import math
import json

color = [[0.95, 0.95, 0.95], [0.3, 0.5, 0.8], [0.9, 0.9, 0.6],
         [0.5, 0.2, 0.3], [0.9, 0.9, 0.9], [0.8, 0.8, 0.8],
         [0.7, 0.7, 0.7], [1, 0.5, 0], [0, 1, 1],
         [1, 0, 0], [0.8, 0.6, 0.2], [0.2, 0.2, 0.5],
         [0.3, 0.8, 0.95], [0.9, 0.6, 0.92]]
# color_index:
# 0:off_white
# 1:apr_upright
# 2:package
# 3:pallet
# 4:stack
# 5:wall and pillars
# 6:doors and gate
# 7:apr_beam
# 11:dock
# 12:apr_double

color_checklist = {
    'wall': 1,
    'dock': 2,
    'door': 3,
    'exit': 4,
    'column': 5,
    'misc_column': 6,
    'safety_door': 3,
    'obstacle': 1,
    'guard': 1,
    'guard_2m': 1,
    'acc_guard': 1,
    'fire_hydrant': 3,
    'dock_in': 2,
    'dock_out': 2,
    'guard_passage': 1,
    'customize': 1,
    'forklift': 1
}

upright_color = {
    'apr': 1,
    'shelf': 1
}
mesh_color = [0, 5, 11, 3, 1, 6, 6, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0]  # assign到expand_box中的mesh color
# 模型颜色0：黑色
# 1：墙
# 2：Dock
# 3：Door
# 4：Exit
# 5：Column
# 6：Misc Column

pallet_htight = 75  # pallet
room_height = 9000
wall_depth = 100
door_height = 4000
beam_height = 0


def get_indice(point_cloud):
    indice = [[4, 7, 5], [4, 6, 7], [0, 2, 4], [2, 6, 4], [0, 1, 2], [1, 3, 2],
              [1, 5, 7], [1, 7, 3], [2, 3, 7], [2, 7, 6], [0, 4, 1], [1, 4, 5]]
    # 计算好的顶点规则

    return np.array(indice)


def expand_box(box, mesh, color_id):
    points = []

    for i in range(2):
        for j in range(2):
            for k in range(2):
                points.append([box[i*3], box[j*3+1], box[k*3+2]])

    point_cloud = np.array(points)

    indices = get_indice(point_cloud)

    unit_mesh = o3d.geometry.TriangleMesh()
    unit_mesh.vertices = o3d.utility.Vector3dVector(point_cloud)
    unit_mesh.triangles = o3d.utility.Vector3iVector(indices)
    # o3d.visualization.draw_geometries([mesh])

    unit_mesh.paint_uniform_color((color[color_id]))  # mesh上色

    mesh += unit_mesh

    return mesh


def expand_shape(points, mesh, color):

    point_cloud = np.array(points)
    indices = get_indice(point_cloud)
    unit_mesh = o3d.geometry.TriangleMesh()
    unit_mesh.vertices = o3d.utility.Vector3dVector(point_cloud)
    unit_mesh.triangles = o3d.utility.Vector3iVector(indices)
    unit_mesh.paint_uniform_color(color)  # mesh上色

    mesh += unit_mesh
    return mesh


def add_cylinder(points, radius, room_height, mesh):

    x = points[0]
    y = points[1]
    z = (room_height/2)
    cld = o3d.geometry.TriangleMesh.create_cylinder(radius, room_height, 4)
    cld.translate(np.array([x, y, z]))
    cld.paint_uniform_color([0.8, 0.8, 0.8])

    mesh += cld
    return mesh


def process_stack(packages, mesh):

    if not 'children' in packages and not 'box' in packages:
        for item in packages:
            process_stack(item, mesh)

    elif 'children' in packages:
        process_stack(packages['children'], mesh)

    elif 'box' in packages:
        box = packages['box']
        x0, y0, z0, x1, y1, z1 = box[0][0], box[0][1], box[0][2], box[1][0], box[1][1], box[1][2]

        expand_box([x0, y0, z0, x1, y1, z1], mesh, 4)

    return


def process_skeleton(skeleton, stype, mesh):

    for row in skeleton['upright']:
        for box in row:
            x0, y0, z0, x1, y1, z1 = box[0][0], box[0][1], box[0][2], box[1][0], box[1][1], box[1][2]
            expand_box([x0, y0, z0, x1, y1, z1], mesh, upright_color[stype])

        box1, box2 = row[0], row[1]
        x0, y0, z0 = min(box1[0][0], box2[0][0]), min(
            box1[0][1], box2[0][1]), min(box1[0][2], box2[0][2])
        x1, y1, z1 = max(box1[1][0], box2[1][0]), max(
            box1[1][1], box2[1][1]), max(box1[1][2], box2[1][2])
        upright_width = min(x1-x0, y1-y0)

        if stype == 'apr':
            expand_box([x0, y0, z1 - upright_width, x1, y1, z1],
                       mesh, upright_color[stype])

    top_height = z1

    if stype == 'apr':
        for pair in skeleton['beam']:
            for row in pair:
                x0, y0, z0, x1, y1, z1 = row[0][0], row[0][1], row[0][2], row[1][0], row[1][1], row[1][2]

                if x1 - x0 > y1 - y0:
                    x0 += upright_width
                    x1 -= upright_width
                else:
                    y0 += upright_width
                    y1 -= upright_width

                expand_box([x0, y0, z0, x1, y1, z1], mesh, 7)

    else:
        for pair in skeleton['beam']:
            box1, box2 = pair[0], pair[1]
            x0, y0, z0 = box1[0][0], box1[0][1], box1[0][2]
            x1, y1, z1 = box2[1][0], box2[1][1], box2[1][2]
            if x1 - x0 > y1 - y0:
                x0 += upright_width
                x1 -= upright_width
            else:
                y0 += upright_width
                y1 -= upright_width

            expand_box([x0, y0, z0, x1, y1, z1], mesh, 6)

            if z0 <= 300:
                expand_box([x0, y0, top_height-(z1-z0),
                           x1, y1, top_height], mesh, 6)

    global beam_height
    beam_height = z1 - z0

    return


def process_packages(packages, stype, mesh):

    if stype == 'apr':
        for row in packages['children']:
            for stack in row['children']:
                if not 'children' in stack:
                    continue
                for unit in stack['children']:
                    if 'children' in unit:
                        for bbox in unit['children']:
                            box = bbox['box']
                            x0, y0, z0, x1, y1, z1 = box[0][0], box[0][1], box[0][2], box[1][0], box[1][1], box[1][2]
                            expand_box(
                                [x0, y0, z0 + beam_height, x1, y1, z1], mesh, 2)
    else:
        for row in packages['children']:
            for stack in row['children']:
                if not 'children' in stack:
                    continue
                for unit in stack['children']:
                    box = unit['box']
                    x0, y0, z0, x1, y1, z1 = box[0][0], box[0][1], box[0][2], box[1][0], box[1][1], box[1][2]
                    expand_box(
                        [x0, y0, z0 + beam_height, x1, y1, z1], mesh, 2)


def process_mezzanine(skeleton, mesh):
    pass


def process_fixtures(plan, mesh):

    for i in plan:
        p = i['points']
        t = color_checklist[i['color']]
        color = mesh_color[t]

        if t == 1:
            # 用每个fixture区域的bounding box来替换画地板范围
            floor_x = [float('inf'), float('-inf')]
            floor_y = [float('inf'), float('-inf')]

            for x_position, y_position in p:
                floor_x[0] = min(x_position, floor_x[0])
                floor_y[0] = min(y_position, floor_y[0])
                floor_x[1] = max(x_position, floor_x[1])
                floor_y[1] = max(y_position, floor_y[1])
            expand_box([floor_x[0]-4000, floor_y[0]-4000, -100,
                       floor_x[1]+4000, floor_y[1]+4000, 0], mesh, 0)

            p.append(p[0])

            for id in range(len(p)-1):
                # 补上墙面转角处，添加一个cylinder
                add_cylinder(p[id], wall_depth * 2, room_height, mesh)

                if p[id][0] != p[id+1][0] and p[id][1] != p[id+1][1]:  # 若x，y坐标均不在同一位置则为斜边
                    x0, x1 = p[id][0], p[id+1][0]
                    y0, y1 = p[id][1], p[id+1][1]

                    # 计算斜边四个顶点的位置，需要求出顶点需要位移的距离dx, dy
                    a, b = y1-y0, x1-x0
                    c = np.sqrt(np.square(a)+np.square(b))
                    dx, dy = - a * wall_depth / c, b * wall_depth / c
                    # 列出斜边墙的8个顶点位置
                    wall = [[x0-dx, y0-dy, 0], [x0-dx, y0-dy, room_height], [x0+dx, y0+dy, 0], [x0+dx, y0+dy, room_height],
                            [x1-dx, y1-dy, 0], [x1-dx, y1-dy, room_height], [x1+dx, y1+dy, 0], [x1+dx, y1+dy, room_height]]
                else:
                    # 若为水平或垂直的墙面则无需特殊处理
                    x0, x1 = min(p[id][0], p[id+1][0]
                                 ), max(p[id][0], p[id+1][0])
                    y0, y1 = min(p[id][1], p[id+1][1]
                                 ), max(p[id][1], p[id+1][1])
                    if y0 == y1:  # 若为垂直墙面
                        wall = [[x0, y0-wall_depth, 0], [x0, y0-wall_depth, room_height], [x0, y1+wall_depth, 0], [x0, y1+wall_depth, room_height],
                                [x1, y0-wall_depth, 0], [x1, y0-wall_depth, room_height], [x1, y1+wall_depth, 0], [x1, y1+wall_depth, room_height]]
                    else:  # 若为水平墙面
                        wall = [[x0-wall_depth, y0, 0], [x0-wall_depth, y0, room_height], [x0-wall_depth, y1, 0], [x0-wall_depth, y1, room_height],
                                [x1+wall_depth, y0, 0], [x1+wall_depth, y0, room_height], [x1+wall_depth, y1, 0], [x1+wall_depth, y1, room_height]]

                expand_shape(wall, mesh, [0.8, 0.8, 0.8])

        elif t == 4 or t == 7:
            # door 或者gate or safety gate
            expand_box([p[0][0], p[0][1], 0, p[1][0], p[2]
                       [1], door_height], mesh, color)
        elif t == 5 or t == 6:
            # 柱子
            expand_box([p[0][0], p[0][1], 0, p[1][0], p[2]
                       [1], room_height], mesh, color)

        elif t == 2 or t == 3:
            # dock
            x0, x1 = min(p[0][0], p[1][0], p[2][0], p[3][0]), max(
                p[0][0], p[1][0], p[2][0], p[3][0])
            y0, y1 = min(p[0][1], p[1][1], p[2][1], p[3][1]), max(
                p[0][1], p[1][1], p[2][1], p[3][1])
            if y1-y0 > x1-x0:
                x1 += 400
                x0 -= 400
            else:
                y1 += 400
                y0 -= 400
            expand_box([x0, y0, 0, x1, y1, door_height], mesh, color)
        pass

    return mesh


def static_fixtures(jsonfile, output_dir=""):

    with open(jsonfile, "r") as f:
        plan = json.loads(f.read())
    output = {}

    tracks = []
    static = []
    for item in plan:
        bbox = item['bbox']
        x_offset = -(bbox[2]-bbox[0])/2 - bbox[0]  # 计算y轴位移
        y_offset = -(bbox[3]-bbox[1])/2 - bbox[1]  # 计算x轴位移
        model_detailes = {}
        type_id = item['type']
        points = item['points']
        x0, y0 = points[0][0], points[0][1]
        x1, y1 = points[1][0], points[1][1]

        model_detailes['model'] = item['model']
        model_detailes['position'] = [
            (x0 + x1)/2 + x_offset, (y0 + y1)/2 + y_offset, 0]
        model_detailes['direction'] = [math.pi/2, math.pi, 0]  # 默认朝上
        model_detailes['name'] = item['name']
        model_detailes['scale'] = [1000, 1000, 1000]
        direction = {
            "upwards": [math.pi/2, math.pi, 0],
            "downwards": [math.pi/2, 0, 0],
            "leftwards": [math.pi/2, -math.pi/2, 0],
            "rightwards": [math.pi/2, math.pi/2, 0]
        }
        if type_id == 17:  # forklift
            model_detailes['direction'] = direction[item['direction']]
            pass

        elif type_id == 18:  # agv
            model_detailes['scale'] = [(x1 - x0)/7.99, 265, (y1 - y0)/11.8]
            model_detailes['direction'] = direction[item['direction']]

        elif type_id == 19:  # manup_truck
            model_detailes['direction'] = direction[item['direction']]
            pass

        elif type_id == 20:  # operating_platform
            model_detailes['scale'] = [(x1 - x0)/8.62, 265, (y1 - y0)/4.97]
            model_detailes['direction'] = direction[item['direction']]
            pass

        elif type_id == 21:  # warehouse_operator
            model_detailes['scale'] = [24.5, 24.5, 24.5]
            pass

        elif type_id == 22:  # convey_line
            model_detailes['scale'] = [(x1 - x0)/5.83, 10000, (y1 - y0)/0.62]
            if x1 - x0 < y1 - y0:
                model_detailes['direction'][1] = [-math.pi/2]
            pass
        static.append(model_detailes)

    output['tracks'] = tracks
    output['static'] = static

    json_path = os.path.join(output_dir, "static_fixtures.json")
    with open(json_path, 'w') as f:
        f.write(json.dumps(output))

    pass


def render_storage(plan_list):
    mesh = o3d.geometry.TriangleMesh()

    for id in plan_list:
        plan = plan_list[id]
        packages = plan['packages']
        box = packages['box']
        stype = plan['base_rack']

        floor = [box[0][0], box[0][1], -100, box[1][0], box[1][1], 0]
        expand_box(floor, mesh, 0)

        if stype == 'stack':
            process_stack(packages, mesh)

        else:
            skeleton = plan['skeleton']

            if stype == 'apr' or stype == 'shelf':
                process_skeleton(skeleton, stype, mesh)
                process_packages(packages, stype, mesh)

            elif stype == 'mezzanine':
                process_mezzanine(skeleton, mesh)
                pass
    pass

    return mesh


def render_fixtures(scene):

    mesh = o3d.geometry.TriangleMesh()

    process_fixtures(scene['top_view'], mesh)
    pass

    return mesh


def init_mesh(scene, plan_list, path):

    mesh = render_storage(plan_list)

    if scene != None:

        fixtures_mesh = render_fixtures(scene)
        mesh += fixtures_mesh

    mesh.translate(np.array([0, 0, 0]), False)
    mesh.remove_duplicated_triangles()

    if path == None:
        mesh_path = 'design.gltf'
    else:
        mesh_path = os.path.join(path, "design.gltf")
    o3d.io.write_triangle_mesh(mesh_path, mesh)
    print('write mesh', mesh)
    # o3d.visualization.draw_geometries(mesh)
