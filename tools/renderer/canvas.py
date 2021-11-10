import cv2
import os
from contextlib import contextmanager
from .geometry import Box, Point
import numpy as np
class Style:
    def __init__(self, lineColor=0, fillColor=None):
        self.lineColor = lineColor
        self.fillColor = fillColor
        pass

    def copy(self):
        s = Style()
        s.lineColor = self.lineColor
        s.fillColor = self.fillColor
        return s

    def __str__(self):
        return 'LC: %s FC: %s' % (self.lineColor, self.fillColor)
    pass


class Canvas:

    def __init__(self):
        self.styles = [Style()]  # style栈，可以用with canvas.style不断往里压
        pass

    @contextmanager
    def style(self, **kwargs):
        try:
            s = self.styles[-1].copy()
            for k, v in kwargs.items():
                s.__setattr__(k, v)
                pass
            self.styles.append(s)
            yield None
        finally:
            self.styles.pop()
            pass
        pass

    def line(self, v1, v2):
      self.path([v1, v2])
      pass

    def hatch (self, points):   
        lc = self.styles[-1].lineColor
        fc = self.styles[-1].fillColor
        if fc is None:
            fc = lc
        with self.style(lineColor=lc, fillColor=fc):
            self.path(points, closed=True)
        pass
    pass


ColorMap = {'apr':30,
            'aprupright':5,
            'underpass':3,
            'apr_double_deep':5,
            'lss':11,
            'stack':0,
            'mezzanine':30,
            'mezzanineupright':5,
            'shelf':1,
            'shelfupright':4,
            'wall':0,
            'dock':12,
            'door':13,
            'exit':14,
            'column':15,
            'safety_door':17,
            'guard':18,
            'obstacle':19,
            'fire_hydrant':20,
            'forklift':21,
            'solid_line':0,
            'frame':6,
            'wall_parse':22,
            'column_parse':23,
            'door_parse':24
}

TABLEAU20 = [[255, 255, 255],[0, 0, 255],[220, 10, 10],[0, 255, 0],[255, 255, 0],
[255, 0, 0],[10, 10, 10],[255, 255, 255],[100, 100, 100],[180, 119, 31],
[232, 199, 174],[14, 127, 255],[120, 187, 255],[44, 160, 44],[138, 223, 152],
[40, 39, 214],[150, 152, 255],[189, 103, 148],[213, 176, 197],[75, 86, 140],
[148, 156, 196],[194, 119, 227],[210, 182, 247],[127, 127, 127],[199, 199, 199],
[129, 96, 86],[141, 219, 219],[207, 190, 23],[229, 218, 158],[240, 240, 240],
[0, 127, 255],[220, 10, 10],[230, 220, 10],[20, 200, 10],[170, 20, 220],[200, 200, 200],[0, 230, 230],[100, 100, 100],[180, 119, 31],[232, 199, 174],[14, 127, 255],[120, 187, 255],[44, 160, 44],[138, 223, 152],[40, 39, 214],[150, 152, 255],[189, 103, 148],[213, 176, 197],[75, 86, 140],[148, 156, 196],[194, 119, 227],[210, 182, 247],[127, 127, 127],[199, 199, 199],[34, 189, 188],[141, 219, 219],[207, 190, 23],[229, 218, 158]]



class RasterCanvas(Canvas):

    def __init__ (self, bbox, size, padding=0):
        '''
        bbox: 被画对象的bounding box
        size: canvas较长边的大小
        '''
        super().__init__()
        self.padding = padding
        self.styles = [Style()]
        self.bbox = bbox
        self.palette = TABLEAU20
        [x0, y0], [x1, y1] = bbox.unpack()
        w = x1 - x0
        h = y1 - y0
        assert w > 0 and h > 0
        l = max(w, h)
        self.scale_num = size - 1 - padding * 2
        self.scale_denom = l
        self.size = ((h * self.scale_num + self.scale_denom - 1) // self.scale_denom + 1 + padding * 2), \
                    ((w * self.scale_num + self.scale_denom - 1) // self.scale_denom + 1 + padding * 2)
        pass

    def map (self, vector):
        '''坐标转换, ezdxf.math.vector转成整数(x,y)'''
        x = round((vector[0] - self.bbox.point1[0]) * self.scale_num / self.scale_denom)
        y = round((vector[1] - self.bbox.point1[1]) * self.scale_num / self.scale_denom)
        return (x + self.padding, self.size[0] - y - self.padding)

    def unmap (self, pt):
        '''坐标逆转换，返回的是浮点数'''
        x, y = pt
        x -= self.padding
        y = self.size[0] - y - self.padding
        x = x * self.scale_denom / self.scale_num + self.bbox[0][0]
        y = y * self.scale_denom / self.scale_num + self.bbox[0][1]
        return (x, y)

    def scale (self, r):
        ''' 半径转换为整数(四舍五入)'''
        return round(r * self.scale_num / self.scale_denom)


class CvCanvas(RasterCanvas):

    def __init__ (self, box, size, padding=0):
        super().__init__(box, size, padding)
        self.image = np.zeros(self.size + (3,), dtype=np.uint8)
        pass

    def gray (self):
        return cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def lineColor (self):
        return self.palette[ColorMap[self.styles[-1].lineColor]]

    def fillColor (self):
        '''获取当前应该用的颜色, [b,g,r]'''
        if self.styles[-1].fillColor is None:
            return None
        return self.palette[ColorMap[self.styles[-1].fillColor]]

    def copycvs (self, target, resolution):
        self.image = cv2.resize( target.image, (resolution, resolution), interpolation=cv2.INTER_CUBIC )
  
    def path (self,points,closed = False):
        """
        多个点构成的折线
        :param points: 多个点  [(x1,y1),(x2,y2)]
        :param closed: 图形是否闭合
        """
        if len(points) == 0:
            return
        pts = []
        for p in points:
            pts.append(self.map(p))

        if closed and not self.fillColor() is None:
            #实现hatch
            cv2.fillPoly(self.image, [np.round(np.array(pts)).astype(np.int32)], self.fillColor())
            return
        cv2.polylines(self.image, [np.round(np.array(pts)).astype(np.int32)], closed, self.lineColor())
        pass

    
    def arc (self,center,radius, angle, start_angle, end_angle):
        """
        圆弧（可实现 圆 、 椭圆 、 圆弧等）
        :param center: 中心
        :param radius: 半径 格式为（r1,r2),r1为半长轴，r2为半短轴。若需绘制图形为圆，则r1=r2
        :param angle: 旋转的角度 顺时针
        :param start_angle: 开始角度
        :param end_angle: 结束角度
        :param shift: 线宽 -1填充图形 默认0
        """
        angle, start_angle, end_angle = angle_cad_to_cv(angle, start_angle, end_angle)

        cv2.ellipse(self.image, self.map(center), 
                (self.scale(radius[0]), self.scale(radius[1])),
                angle, start_angle, end_angle, self.lineColor())
        pass

    def save(self, path):
        cv2.imwrite(path, self.image)
        pass

    def save_alpha(self, path):
        alpha = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        alpha = (alpha > 0) * 255
        image = np.dstack([self.image, alpha])
        cv2.imwrite(path, image)
        pass


    def fill_with_white(self):
        self.image[:]=(255,255,255)

    pass


class JsonCanvas(Canvas):
    #画布记录为json格式
    def __init__(self):
        super().__init__()
        self.shapes = []
        self.bbox = Box()
        self.label = ''
        pass

    def path (self,points,closed = False):

        if len(points) == 0:
            return
        #for v in points:
        #    expandFloat(self.bbox, v)
        points = [round_point(v) for v in points]
        if closed:
            points.append(points[0])
        self.shapes.append({
            'points': points, 'color': self.styles[-1].lineColor
        })
        pass

    def arc (self,center,radius, angle,start_angle, end_angle):
        # TODO
        pass

    def dump(self):
        return (self.shapes)

    def update(self, second_canvas):
        self.shapes.append(second_canvas.shapes)
    pass


def compact_boxes(boxes, dist=5000):
    i = 0 
    mapped_boxes = []
    vects = []
    xo = 0  #compact图的左上角
    yo = 0
    wide = 0
    height = 0
    tmp_x = 0 #左上角 
    for box in boxes:
        [x0, y0], [x1, y1] = box.unpack()
        # 第一个box
        if i == 0:
            mapped_boxes.append(box)
            vects.append([0,0])
            xo = x0
            yo = y1
            tmp_x = x0
            
        else:
            tmp_x += (wide + dist) #更新左上角 
            mapped_boxes.append(Box(tmp_x, yo+y0-y1, tmp_x+x1-x0, yo))
            vects.append([tmp_x-x0,yo-y1])

        wide = x1-x0
        height = y1-y0
        
        i += 1
        
    return mapped_boxes, vects


def bound_boxes(mapped_boxes):
    if len(mapped_boxes) < 1:
        return None
    min_x = min_y = max_x = max_y = None
    for i in range(len(mapped_boxes)):
        box = mapped_boxes[i]
        if i == 0:
            min_x, min_y, max_x, max_y = box.unpack()
        else:
            [x0, y0], [x1, y1] = box.unpack()
            if x1> max_x:
                max_x = x1
            if y0 < min_y:
                min_y = y0
    return Box(min_x, min_y, max_x, max_y)

def convert_point(p, boxes, vects):
    for i in range(len(boxes)):
        [x0, y0], [x1, y1] = boxes[i].unpack()
        xp, yp = p
        if x0 <= xp <= x1 and y0 <= yp <= y1:
            #return Point(xp+vects[i][0],yp+vects[i][1])
            return (xp+vects[i][0],yp+vects[i][1])

def round_point(v):
    return [round(v[0]), round(v[1])]
