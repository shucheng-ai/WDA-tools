#!/usr/bin/env python3
import sys
import os
import json
import math

def init_static(jsonfile, output_dir = ""):

    with open(jsonfile, "r") as f:
        plan = json.loads(f.read())
    output = {}

    tracks = []
    static = []
    for item in plan:
        bbox = item['bbox']
        x_offset = -(bbox[2]-bbox[0])/2 - bbox[0]  #计算y轴位移
        y_offset = -(bbox[3]-bbox[1])/2 - bbox[1]  #计算x轴位移
        model_detailes = {}
        type_id = item['type']
        points = item['points']
        x0, y0 = points[0][0], points[0][1]
        x1, y1 = points[1][0], points[1][1]
        
        model_detailes['model'] = item['model']
        model_detailes['position'] = [(x0 + x1)/2 + x_offset, (y0 + y1)/2 + y_offset, 350]
        model_detailes['name'] = item['name']
        model_detailes['scale'] = [1000, 1000, 1000]

        direction = {
            "upwards":[math.pi/2, math.pi, 0],
            "downwards":[math.pi/2, 0, 0],
            "leftwards":[math.pi/2, -math.pi/2, 0],
            "rightwards":[math.pi/2, math.pi/2, 0]
        }        
        model_detailes['direction'] = direction[item['direction']]

        if type_id == 17: #forklift
            pass

        elif type_id ==18: #agv
            pass

        elif type_id == 19: #manup_truck
            pass
        
        elif type_id == 20: #operating_platform
            if item['direction'] == 'leftwards' or item['direction'] == 'rightwards':
                model_detailes['scale'] = [(x1 - x0)/1.1 , 1000, (y1 - y0)/0.7 ]
            else:
                model_detailes['scale'] =  [(x1 - x0)/0.7 , 1000, (y1 - y0)/1.1 ]
            pass
        
        elif type_id == 21: #warehouse_operator
            model_detailes['scale'] = [24.5, 24.5, 24.5]
            pass
        
        elif type_id == 22: #convey_line
            
            if item['direction'] == 'leftwards' or item['direction'] == 'rightwards':
                ratio = (x1-x0)/(y1-y0)
                model_detailes['scale'] = [(y1 - y0), 1000, (x1 - x0)/3]

            else:
                ratio = (y1-y0)/(x1-x0)
                model_detailes['scale'] = [(x1 - x0), 1000, (y1 - y0)/3]
            #model_detailes['direction'][1] -= math.pi/2
            print(item['direction'] , model_detailes['scale'] )
        static.append(model_detailes)

    output['tracks'] = tracks
    output['static'] = static

    json_path = os.path.join(output_dir, "static_fixtures.json")
    with open(json_path, 'w') as f:
        f.write(json.dumps(output))

    pass


if __name__ == '__main__':
    #path = os.path.abspath(os.path.dirname(__file__))
    #default_session_path = os.path.abspath(os.path.join(path, "session"))

    jsonfile = sys.argv[1]
    output_dir = sys.argv[2]

    init_static(jsonfile, output_dir)
