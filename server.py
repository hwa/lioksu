#-*- coding: utf-8 -*-
import bottle
import fontforge
import os

font_dir = "./subfonts/"

template_font = fontforge.open("./li.tpl.ttf")
HanDingYanTi_font = fontforge.open("./fonts/wt064.ttf")
font_files = {"HanDingYanTi" : HanDingYanTi_font}

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

def mk_css_resp(font_name, font_path):
    return """@font-face {
  font-family: '%s';
  src: url(%s.eot);
  src: local('☺'), url('%s.eot?') format('eot'), url('%s.woff') format('woff'), url('%s.ttf') format('truetype');
}""" % (font_name, font_path, font_path, font_path, font_path)



def mk_font_path(font_name, text):
    return font_dir + (font_name + "-" + str(hash(text)))




@bottle.route("/css/:font_name")
def css(font_name):
    text = bottle.request.query.text
    text = ''.join(sorted(list(set(text))))
    output_path = mk_font_path(font_name, text)
    origin_font = font_files[font_name]
    subfont(origin_font, template_font, text, output_path)
    bottle.response.set_header("Content-Type", "text/css")
    return mk_css_resp(font_name, output_path)

@bottle.route("/css/subfonts/<filename:path>")
def font(filename):
    bottle.response.set_header("Content-Type", "font/" + filename.split('.')[1])
    bottle.response.set_header("Cache-Control", "public, max-age=2544316")
    bottle.response.set_header("Access-Control-Allow-Origin", "*")
    return bottle.static_file(filename, root="./subfonts/")




if __name__ == "__main__":
    bottle.run(host="0.0.0.0", port=9200)
