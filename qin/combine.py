#-*- coding: utf-8 -*-

import os
import fontforge
import psMat

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


def test():
    font0 = fontforge.open('fonts/gbsn00lp.ttf')

    c0 = fontforge.nameFromUnicode(ord(u'艹'))
    c1 = fontforge.nameFromUnicode(ord(u'五'))
    cy = fontforge.nameFromUnicode(ord(u'\uE000'))

    g0 = font0[c0]
    g1 = font0[c1]

    l0 = g0.layers[1]
    l1 = g1.layers[1]

    l0.transform(psMat.scale(1,0.9))
    l0.transform(psMat.translate(0,250))
    l1.transform(psMat.scale(1, 0.5))
    l1.transform(psMat.translate(0,-104))
    #l1.transform(psMat.rotate(1.7))

    g0.layers[1] =  l0 + l1

    font0.selection.select(c0)
    font0.copy()
    font0.selection.select(cy)
    font0.paste()


    font0.generate('output/out.ttf')


class FontCreator:
    def __init__(self, origin_font):
        self.font = fontforge.open(origin_font)
        self.count = 0
        #self.combinator = Combinator()

    def current_priv_point(self):
        c = self.count
        self.count += 1
        return unichr(0xE000 + c)

    def generate(self, unicodes):
        subfont(self.font,
                fontforge.open('li.tpl.ttf'),
                unicodes,
                "output/out")

    def create(self, layer):
        c = glyph_name(self.current_priv_point())
        m = glyph_name(u'鹿')
        self.font[m].layers[1] = layer
        self.font.selection.select(m)
        self.font.copy()
        self.font.selection.select(c)
        self.font.paste()

    def layerof(self, unic):
        return self.font[glyph_name(unic)].layers[1]
        

emsize = 968
halfsize = emsize/2
descent = 194
middle = halfsize - descent

def add(*layers):
    return reduce(lambda x,y: x+y,
                  layers)

def transform(matrix):
    def _f(layer):
        l = layer.dup()
        l.transform(matrix)
        return l
    return _f


def compose(*matris):
    return reduce(psMat.compose, matris)

def translate(x, y):
    return psMat.translate(x, y)
                  
def scale(scaleX, scaleY):
    return compose(psMat.translate(-halfsize, -middle),
                   psMat.scale(scaleX, scaleY),
                   psMat.translate(halfsize, middle))

def rotate(radiant):
    return compose(psMat.translate(-halfsize, -middle),
                   psMat.rotate(radiant),
                   psMat.translate(halfsize, middle))

def skew(radiant):
    return compose(psMat.translate(-halfsize, -middle),
                   psMat.skew(radiant),
                   psMat.translate(halfsize, middle))

def percent_y(percent):
    return emsize * percent - descent

def percent_x(percent):
    return emsize * percent

def chu(x, y): #出
    def _f(layer1, layer2):
        s1, s2 = x/(x+y), y/(x+y)
        h1, h2 = (x/2.0+y) / (x+y), y/2.0/(x+y)
        m1 = compose(scale(1, s1/x),
                     translate(0, percent_y(h1)- percent_y(0.5)))
        m2 = compose(scale(1, s2/y),
                     translate(0, percent_y(h2)- percent_y(0.5)))
        l1, l2 = layer1.dup(), layer2.dup()
        l1.transform(m1)
        l2.transform(m2)
        return add(l1, l2)
    return _f

def cong(x, y): #从
    def _f(layer1, layer2):
        s1, s2 = 1.0/(x+y), 1.0/(x+y)
        w1, w2 = x/2.0/(x+y), (y/2.0 + x)/(x+y)
        m1 = compose(scale(s1, 1.0),
                     translate(percent_x(w1) - percent_x(0.5), 0))
        m2 = compose(scale(s2, 1.0),
                     translate(percent_x(w2) - percent_x(0.5), 0))
        l1, l2 = layer1.dup(), layer2.dup()
        l1.transform(m1)
        l2.transform(m2)
        return add(l1, l2)
    return _f

def gou(x, y, a): #勾
    def _f(layer1, layer2):
        x0, y0 = (x -0.5) * emsize, (y - 0.5) * emsize
        m2 = compose(scale(a, a), translate(x0, y0))
        l1, l2 = layer1.dup(), layer2.dup()
        l2.transform(m2)
        return add(l1, l2)
    return _f
        
def glyph_name(unic):
    return fontforge.nameFromUnicode(ord(unic))


if __name__ == "__main__":
    fc = FontCreator('fonts/FZSongTi.ttf')
    fc.create(chu(0.4, 1.0)(fc.layerof(u'艹'), gou(0.4, 0.4, 0.6)(fc.layerof(u'勹'), fc.layerof(u'三'))))
    g0 = chu(1.0, 1.0)(fc.layerof(u'木'), fc.layerof(u'六'))
    g1 = fc.layerof(u'乚')
    g1.transform(compose(scale(1.4,1), translate(-90, 0)))
    fc.create(gou(0.6, 0.6, 0.7)(g1, g0))
    g2 = fc.layerof(u'卜')
    g2.transform(scale(0.3, 0.3))
    g3 = cong(1.0, 1.0)(fc.layerof(u'夕'), fc.layerof(u'十'))
    g3.transform(scale(1.0, 0.7))
    g4 = chu(0.3, 1.0)(g2, gou(0.4, 0.4, 0.6)(fc.layerof(u'勹'), fc.layerof(u'四')))
    fc.create(chu(0.7, 1.0)(g3, g4))


    fc.generate(u'艹四五\uE000\uE001\uE002\uE003')


#艹乚勹
