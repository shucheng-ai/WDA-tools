#!/usr/bin/env python3
# coding:utf-8
from .render_plans import render_front_view, render_cvcanvas, render_side_view, render_top_view, render_cad_top_view, render_scene, render_png_top_view
from .models_dxf import init_static_models
import os


def render (plan, stype, params = {}):
    
    #返回前端绘图用top view
    results = render_top_view(plan, stype, params)
    return results

def canvas (plan, stype, params = {}, out_dir = None, thumbnail = 2048):

    #返回top view png文件
    if out_dir != None:
        os.makedirs(out_dir, exist_ok=True)
    render_cvcanvas(plan, stype, params, out_dir, thumbnail)
    pass

def side_view (base_rack, params, thumbnail = 512, path = None):

    #返回side view png文件
    parameters = {}
    var = params
    for key, value in var.items():
        parameters[key] = value['value']
    render_side_view(base_rack, parameters, thumbnail, path)
    pass

def front_view (base_rack, params, thumbnail = 512, path = None):

    #返回front view png文件
    parameters = {}
    var = params
    for key, value in var.items():
        parameters[key] = value['value']
    render_front_view(base_rack, parameters, thumbnail, path)
    pass

def generateCad (scene, plan_list, dxfpath = None, outpath = None):

    #render cad文件

    render_cad_top_view (scene, plan_list, dxfpath, outpath)
    pass

def scene_parse (scene, outpath = None):
    
    render_scene(scene, outpath)
    pass
    
def models_on_cad (jsonfile, outpath = "", dxfpath = None):
    
    init_static_models (jsonfile, dxfpath, outpath)


def dxf2png(scene, plan_list, outpath=None, thumbnail=512):

    render_png_top_view (scene, plan_list, outpath, thumbnail)
    pass
