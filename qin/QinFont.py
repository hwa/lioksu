#-*- coding: utf-8 -*-

#__all__ = ['subfont']

import os
import fontforge
import psMat
from math import *


def subfont(origin_font, template_font, unicodes, output_path):
    font0 = origin_font
    font1 = template_font
    
    # 令字大一致
    font1.em = font0.em

    font1.selection.all()
    font1.clear()

    for u in unicodes:
        try:
            uname = fontforge.nameFromUnicode(ord(u))
            font0.selection.select(uname)
            font0.copy()
            font1.selection.select(uname)
            font1.paste()
        except ValueError:
            continue 

    font1.generate(output_path + ".ttf")
    cmd = "./ttf2eot < %s.ttf > %s.eot" % (output_path, output_path)
    os.system(cmd)
    font1.generate(output_path + ".woff")

#
# module states as globals
#
global font_count ; font_count = 0

def reset_config(origin_font, tpl_font):
    global c_font, c_tpl_font, c_emsize, c_halfsize, c_descent, c_middle
    c_font = fontforge.open(origin_font)
    c_tpl_font = fontforge.open(tpl_font)
    c_emsize = c_font.em - 100
    c_halfsize = c_emsize / 2
    c_descent = c_font.descent - 50
    c_middle = c_halfsize - c_descent


#
# font generator
#

def get_current_priv_point():
    global font_count
    c = font_count
    font_count += 1
    return unichr(0xF8FF - c)

def used_priv_points():
    global font_count
    return ''.join([unichr(0xF8FF - i ) for i in range(font_count)])

def generate(unicodes):
    global c_font, c_tpl_font
    subfont(c_font,
            c_tpl_font,
            unicodes,
            "output/out")

def create_priv_font(comp):
    layer = comp.layer
    global c_font
    c = glyph_name(get_current_priv_point())
    m = glyph_name(u'鹿')
    c_font[m].layers[1] = layer
    c_font.selection.select(m)
    c_font.copy()
    c_font.selection.select(c)
    c_font.paste()

def glyph_name(unic):
    return fontforge.nameFromUnicode(ord(unic))

def char_layerof(c):
    global c_font
    return c_font[glyph_name(c)].layers[1]

#
# glyph component
#

class Component:
    def __init__(self, x, metrics=None):
        global Metrics
        if isinstance(x, unicode):
            (self.height, self.width), (self.inner_x, self.inner_y, self.inner_size) = Metrics.get(x, ((1.0, 1.0), (None, None, None)))
            self.layer = char_layerof(x)
        elif isinstance(x, fontforge.layer):
            self.layer = x
            if not metrics:
                metrics = ((1.0,1.0), (None, None, None))
            (self.height, self.width), (self.inner_x, self.inner_y, self.inner_size) = metrics
        else:
            raise Exception, "unicode or Component object required"

global Metrics
Metrics = {u'艹' : ((0.4, 1.0), (None, None, None)),
           u'乚' : ((0.9, 0.6), (0.6, 0.6, 0.8)),
           u'勹' : ((1.0, 1.0), (0.4, 0.4, 0.6))}



def add(*comps):
    l = reduce(lambda x, y: x+y, [c.layer for c in comps])
    return Component(l)

def transform(matrix):
    def _(comp):
        a, b, c, d, x, y = matrix
        sx = sqrt(a**2 + c**2)
        sy = sqrt(b**2 + d**2)
        l = comp.layer.dup()
        l.transform(matrix)
        return Component(l, ((comp.width * sx, comp.height * sy),
                             (comp.inner_x, comp.inner_y, comp.inner_size)))
    return _

def m_compose(*matris):
    return reduce(psMat.compose, matris)

def m_translate(x, y):
    return psMat.translate(x, y)

def m_scale(scaleX, scaleY):
    return m_compose(psMat.translate(-c_halfsize, -c_middle),
                     psMat.scale(scaleX, scaleY),
                     psMat.translate(c_halfsize, c_middle))

def m_rotate(radiant):
    return m_compose(psMat.translate(-c_halfsize, -c_middle),
                     psMat.rotate(radiant),
                     psMat.translate(c_halfsize, c_middle))

def m_skew(radiant):
    return m_compose(psMat.translate(-c_halfsize, -c_middle),
                     psMat.skew(radiant),
                     psMat.translate(c_halfsize, c_middle))

def percent_y(percent):
    return c_emsize * percent - c_descent

def percent_x(percent):
    return c_emsize * percent

#
# combinators
#
def accept_unicodes(f):
    def _(*comps):
        cs = [Component(c) if not isinstance(c, Component) else c for c in comps]
        return f(*cs)
    return _

@accept_unicodes        
def chu(comp1, comp2): # 出
    x, y = comp1.height, comp2.height
    s1 = s2 = 1.0/(x+y)
    h1, h2 = (x/2.0+y) / (x+y), y/2.0 / (x+y)
    m1 = m_compose(m_scale(1, s1),
                   m_translate(0, percent_y(h1)- percent_y(0.5)))
    m2 = m_compose(m_scale(1, s2),
                   m_translate(0, percent_y(h2)- percent_y(0.5)))
    l1, l2 = comp1.layer.dup(), comp2.layer.dup()
    l1.transform(m1)
    l2.transform(m2)
    return add(Component(l1), Component(l2))

@accept_unicodes
def cong(comp1, comp2): #从
    x, y = comp1.width, comp1.width
    s1, s2 = 1.0/(x+y), 1.0/(x+y)
    w1, w2 = x/2.0/(x+y), (y/2.0 + x)/(x+y)
    m1 = m_compose(m_scale(s1, 1.0),
                   m_translate(percent_x(w1) - percent_x(0.5), 0))
    m2 = m_compose(m_scale(s2, 1.0),
                   m_translate(percent_x(w2) - percent_x(0.5), 0))
    l1, l2 = comp1.layer.dup(), comp2.layer.dup()
    l1.transform(m1)
    l2.transform(m2)
    return add(Component(l1), Component(l2))

@accept_unicodes
def gou(comp1, comp2): #勾
    x, y = comp1.inner_x, comp1.inner_y
    a = comp1.inner_size
    x0, y0 = (x -0.5) * c_emsize, (y - 0.5) * c_emsize
    m2 = m_compose(m_scale(a, a), m_translate(x0, y0))
    l1, l2 = comp1.layer.dup(), comp2.layer.dup()
    l2.transform(m2)
    return add(Component(l1), Component(l2))

        
def lisp_eval(tpl):
    if not isinstance(tpl, tuple):
        return tpl
    else:
        return tpl[0](*[lisp_eval(a) for a in tpl[1:]])

le = lisp_eval

if __name__ == "__main__":
    reset_config("fonts/FZSongTi.ttf", "li.tpl.ttf")
    tiao = transform(m_compose(m_scale(1.5,1.0),
                               m_translate(-100,0)))(Component(u'乚'))
    chuo = transform(m_scale(0.5, 0.7))(Component(u'卜'))
    ps = [(chu, u'艹', (gou, u'勹', u'三')),
         (chu, u'木', (gou, tiao, u'六')),
         (gou, u'勹', u'四'),
         (gou, tiao, u'七'),
         (gou, u'勹', u'五'),
         (gou, tiao, u'六'),
         (chu, (cong, u'夕', u'十'), (chu, chuo, (gou, u'勹', u'四')))
         ]
    for p in ps:
        create_priv_font(le(p))
    generate(u'四五六'+used_priv_points())
