#!/usr/bin/env python3
"""Extrai estilos e catálogo não-binário de um documento .sketch ZIP.
Uso: python3 tools/extract_sketch.py '/caminho/Apple iOS 27 UI Kit.sketch.zip'
Não copia imagens/fontes/artefatos do design original.
"""
import sys, json, zipfile, re, unicodedata, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def clamp(v): return max(0,min(255, round(float(v)*255)))
def col(c):
    if not c: return None
    r,g,b = (clamp(c.get(x,0)) for x in ('red','green','blue'))
    a = round(c.get('alpha',1),4)
    return {'hex':f'#{r:02X}{g:02X}{b:02X}', 'alpha':a,'css':f'rgba({r}, {g}, {b}, {a:g})'}

def slug(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii').lower()
    return re.sub('-+','-',re.sub(r'[^a-z0-9]+','-',s)).strip('-')

def extract(zip_path):
 with zipfile.ZipFile(zip_path) as z:
    d=json.loads(z.read('document.json'))
    swatches=[{'name':x['name'], 'id':x['do_objectID'], 'value':col(x['value']), 'token':'--ios-'+slug(x['name'])} for x in d['sharedSwatches']['objects']]
    glass=[]; layer_styles=[]
    for x in d['layerStyles']['objects']:
        v=x['value']; blurs=[b for b in v.get('blurs',[]) if b.get('isEnabled')]
        sty={'name':x['name'],'id':x['do_objectID'],'blurs':[{k:b.get(k) for k in ['radius','saturation','brightness','distortion','depth','type','isCustomGlass','chromaticAberrationMultiplier']} for b in blurs],
             'fills':[{'color':col(f.get('color')), 'enabled':f.get('isEnabled'), 'blendMode':f.get('contextSettings',{}).get('blendMode'),'opacity':f.get('contextSettings',{}).get('opacity'),
                       'gradientType':f.get('gradient',{}).get('gradientType'),'gradientStops':[{'position':t.get('position'),'color':col(t.get('color'))} for t in f.get('gradient',{}).get('stops',[])] if f.get('fillType')!=0 else []} for f in v.get('fills',[])],
             'shadows':[{'inner':s.get('isInnerShadow',False),'blur':s.get('blurRadius',0),'x':s.get('offsetX',0),'y':s.get('offsetY',0),'spread':s.get('spread',0),'color':col(s.get('color')),'blendMode':s.get('contextSettings',{}).get('blendMode'),'enabled':s.get('isEnabled')} for s in v.get('shadows',[])],
             'corners':v.get('corners',{})}
        layer_styles.append(sty)
        if x['name'].startswith('Liquid Glass/'):
            sty['cssClass']='ios-glass--'+slug(x['name'].removeprefix('Liquid Glass/'))
            glass.append(sty)
    texts=[]
    for x in d['layerTextStyles']['objects']:
        a=x['value'].get('textStyle',{}).get('encodedAttributes',{})
        f=a.get('MSAttributedStringFontAttribute',{}).get('attributes',{})
        p=a.get('paragraphStyle',{})
        texts.append({'name':x['name'],'id':x['do_objectID'],'font':f.get('name'), 'size':f.get('size'), 'lineHeight':p.get('maximumLineHeight') or p.get('minimumLineHeight'),'color':col(a.get('MSAttributedStringColorAttribute'))})
    pages=[]
    for ref in d['pages']:
        path=ref['_ref']+'.json';page=json.loads(z.read(path)); layers=page.get('layers',[])
        sample=[{'name':k.get('name'),'type':k.get('_class')} for k in layers[:40]]
        pages.append({'name':page['name'],'topLevelLayers':len(layers),'examples':sample})
    out={'metadata':{'origin':Path(zip_path).name,'swatchCount':len(swatches),'layerStyleCount':len(layer_styles),'glassCount':len(glass),'textStyleCount':len(texts),'pageCount':len(pages),'note':'Dados extraídos de estilos Sketch. Valores Glass nativos não equivalem a CSS diretamente.'},
         'swatches':swatches,'styles':layer_styles,'typography':texts,'pages':pages}
    (ROOT/'data/ios27-tokens.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'data/glass-styles.json').write_text(json.dumps(glass,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'data/pages-index.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf8')
    with (ROOT/'data/cores.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['nome','token','cor_css','hex','alpha']);w.writerows([[v['name'],v['token'],v['value']['css'],v['value']['hex'],v['value']['alpha']] for v in swatches])
    with (ROOT/'data/tipografia.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['nome','fonte','tamanho','altura_linha','cor']);w.writerows([[v['name'],v['font'],v['size'],v['lineHeight'],v['color']['css'] if v['color'] else ''] for v in texts])
    with (ROOT/'data/efeitos-glass.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['nome','classe_css','blur','saturacao','distorcao','profundidade','preenchimentos','sombras']);w.writerows([[v['name'],v['cssClass'],v['blurs'][0]['radius'] if v['blurs'] else 0,v['blurs'][0]['saturation'] if v['blurs'] else '',v['blurs'][0]['distortion'] if v['blurs'] else '',v['blurs'][0]['depth'] if v['blurs'] else '',len(v['fills']),len(v['shadows'])] for v in glass])
    css=['/* 107 amostras do documento Sketch — cores exportadas sem alteração. */',':root {']
    for v in swatches:
        css.append('  '+v['token']+': '+v['value']['css']+';')
    css+=['}','', '/* Aliases para os componentes deste projeto. */', ':root, [data-theme="light"] {']
    aliases={ 'color-bg':'Backgrounds/Light/Primary', 'color-surface':'Backgrounds/Light/Secondary', 'color-text':'Labels/Light/1 Primary', 'color-muted':'Labels/Light/2 Secondary','color-accent':'System Colors/Light/8 Blue','color-separator':'Separators/Light/Non-Opaque'}
    for alias,name in aliases.items():
        found=next((s for s in swatches if s['name']==name),None)
        if found:css.append(f'  --ios-{alias}: var({found["token"]});')
    css.append('}')
    css.append('[data-theme="dark"] {')
    aliases={ 'color-bg':'Backgrounds/Dark - Base/Primary', 'color-surface':'Backgrounds/Dark - Base/Secondary', 'color-text':'Labels/Dark/1 Primary', 'color-muted':'Labels/Dark/2 Secondary', 'color-accent':'System Colors/Dark/8 Blue','color-separator':'Separators/Dark/Non-Opaque'}
    for alias,name in aliases.items():
        found=next((s for s in swatches if s['name']==name),None)
        if found:css.append(f'  --ios-{alias}: var({found["token"]});')
    css.append('}')
    (ROOT/'css/tokens.css').write_text('\n'.join(css)+'\n',encoding='utf8')
    print(f'Extraídos: {len(swatches)} cores; {len(layer_styles)} estilos (dos quais {len(glass)} Glass); {len(texts)} textos; {len(pages)} páginas.')

if __name__=='__main__':
 if len(sys.argv)!=2: sys.exit('Uso: python3 tools/extract_sketch.py arquivo.sketch.zip')
 extract(sys.argv[1])
