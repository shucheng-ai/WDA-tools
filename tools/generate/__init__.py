#!/usr/bin/env python3
#coding:utf-8
from .process_3d import init_mesh
from .static_fixtures import init_static


def generate3d (scene, plan, outpath = None):

    init_mesh (scene, plan, outpath)

def static (jsonfile, outpath = ""):

    init_static (jsonfile, outpath)