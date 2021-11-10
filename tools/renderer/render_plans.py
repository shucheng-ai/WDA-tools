from .modules import handler, draw_top_view, get_bbox, draw_fixtures, draw_walls, draw_test_fixtures
from .canvas import CvCanvas, JsonCanvas
from .dxfwriter import DxfCanvas
from .geometry import Box, Box3D
import copy
import os

layer_name = {
    'apr': 'WDAS_APR',
    'shelf': 'WDAS_SHELF',
    'stack': 'WDAS_STACK',
    'wall': 'WDAS_WALLS',
    'fixture': 'WDAS_FIXTURES'
}


def render_top_view(plan, stype, params):
    packages = plan['packages']
    skeleton = plan['skeleton']
    moving_paths = plan['moving_paths']
    js = JsonCanvas()

    box = packages["box"]
    js.bbox = Box([box[0][0], box[0][1]], [box[1][0], box[1][1]])

    draw_top_view(packages, skeleton, moving_paths, stype, js)

    # 将画图结果写入results中
    results = {}
    results["bbox"] = plan['bbox']
    results["top_view"] = js.dump()
    results["params"] = params
    return results


def render_cvcanvas(plan, stype, params, out_dir, thumbnail):  # top view图片生成接口

    packages = plan['packages']
    skeleton = plan['skeleton']
    moving_paths = plan['moving_paths']

    box = plan['obstacle']
    bbox = Box([box[0][0], box[0][1]], [box[1][0], box[1][1]])
    cvs = CvCanvas(bbox, thumbnail, padding=20)

    draw_top_view(packages, skeleton, moving_paths, stype, cvs)

    if out_dir == None:
        img_path = "design.png"
    else:
        img_path = os.path.abspath(os.path.join(out_dir, "design.png"))

    cvs.save(img_path)
    pass


def render_side_view(base_rack, params, thumbnail, path):
    bbox = get_bbox("side", base_rack, params)
    cvs = CvCanvas(bbox, thumbnail, padding=20)
    handler("side", base_rack, params, cvs)
    if path is None:
        img_path = "side_view.png"
    else:
        img_path = os.path.join(path+"side_view.png")
    cvs.save(img_path)
    pass


def render_front_view(base_rack, params, thumbnail, path):
    bbox = get_bbox("front", base_rack, params)
    cvs = CvCanvas(bbox, thumbnail, padding=20)
    handler("front", base_rack, params, cvs)
    if path is None:
        img_path = "front_view.png"
    else:
        img_path = os.path.join(path+"front_view.png")
    cvs.save(img_path)
    pass


def render_cad_top_view(scene, plan_list, dxfpath, outpath):

    dxf = DxfCanvas(dxfpath)

    if dxfpath == None:

        with dxf.layer(layer_name['wall']):
            draw_walls(scene, dxf)
        with dxf.layer(layer_name['fixture']):
            draw_fixtures(scene, dxf)

    for id in plan_list:

        plan = plan_list[id]
        packages = plan['packages']
        skeleton = plan['skeleton']
        moving_paths = plan['moving_paths']

        stype = plan['base_rack']
        if plan['base_rack'] == 'stack':
            stype = 'stack'

        with dxf.layer(layer_name[plan['base_rack']]+id):
            draw_top_view(packages, skeleton, moving_paths, stype, dxf)

    if outpath == None:
        outpath = ""

    outpath = os.path.join(outpath, "design.dxf")
    dxf.save(outpath)

    pass

def render_png_top_view(scene, plan_list, outpath, thumbnail):

    box = scene["top_view_bbox"]
    bbox = Box([box[0][0], box[0][1]], [box[1][0], box[1][1]])
    cvs = CvCanvas(bbox, thumbnail, padding=20)

    draw_walls(scene, cvs)
    draw_fixtures(scene, cvs)

    for id in plan_list:

        plan = plan_list[id]
        packages = plan['packages']
        skeleton = plan['skeleton']
        moving_paths = plan['moving_paths']

        stype = plan['base_rack']
        if plan['base_rack'] == 'stack':
            stype = 'stack'

        draw_top_view(packages, skeleton, moving_paths, stype, cvs)

    if outpath == None:
        outpath = ""

    img_path = os.path.join(outpath+"thumbnail.png")
    cvs.save(img_path)
    return

    pass

def render_scene(scene, outpath):

    dxf = DxfCanvas()

    draw_test_fixtures(scene, dxf)

    if outpath == None:
        outpath = ""

    outpath = os.path.join(outpath, "wda_parse.dxf")
    dxf.save(outpath)

    pass
