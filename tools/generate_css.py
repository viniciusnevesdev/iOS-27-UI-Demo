#!/usr/bin/env python3
"""Gerar classes web a partir dos JSON exportados (sem dependências)."""
import json,re,unicodedata
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'data/ios27-tokens.json').read_text())
g=json.loads((root/'data/glass-styles.json').read_text())

def sl(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();return re.sub('-+','-',re.sub(r'[^a-z0-9]+','-',s)).strip('-')

def baseline(name):
 dark='Dark/' in name
 if 'Inactive' in name:return ('0px','1','rgba(150,150,160,.12)' if dark else 'rgba(245,245,250,.35)')
 if 'Tinted' in name:return ('6px','1','rgba(104,133,238,.30)' if dark else 'rgba(64,117,226,.22)')
 if 'Regular - Small' in name:return ('6px','2' if not dark else '1','rgba(255,255,255,.18)' if not dark else 'rgba(240,240,255,.08)')
 if 'Regular - Medium' in name:return ('15px' if not dark else '30px','1.4' if not dark else '1.2','rgba(255,255,255,.20)' if not dark else 'rgba(235,235,255,.09)')
 if 'Regular - Large' in name:return ('30px','1.4' if not dark else '1.2','rgba(255,255,255,.26)' if not dark else 'rgba(230,235,255,.12)')
 if 'Keyboard' in name:return ('4px' if not dark else '8px','1','rgba(245,246,249,.42)' if not dark else 'rgba(25,27,38,.35)')
 if 'App Library' in name:return ('5px','1.3','rgba(255,255,255,.23)' if not dark else 'rgba(25,27,38,.28)')
 if 'Dock' in name:return ('3px','1','rgba(255,255,255,.19)' if not dark else 'rgba(25,27,38,.22)')
 return ('3px','1','rgba(255,255,255,.20)' if not dark else 'rgba(35,35,55,.20)')
css=[]
css.append('''/* iOS 27 Glass Web: interpretação CSS de 19 estilos Sketch. NÃO é shader Liquid Glass nativo.
   --ios-glass-blur e --ios-glass-sat originados nos parâmetros Blur do Sketch.
   Outras propriedades (refração/distorção/profundidade) são aproximadas e documentadas em JSON.
   Ajuste --glass-user-blur / --glass-user-opacity / --glass-user-sat no playground. */
.ios-glass {
 --ios-glass-blur: 15px; --ios-glass-sat: 1.4;
 --ios-glass-tint: rgba(255,255,255,.20);
 --ios-glass-border: rgba(255,255,255,.61);
 --ios-glass-hilite: rgba(255,255,255,.74);
 --ios-glass-shadow: 0 14px 35px rgba(58,67,105,.13), 0 1px 2px rgba(54,63,99,.05);
 position: relative; isolation: isolate;
 background: var(--ios-glass-tint);
 -webkit-backdrop-filter: blur(var(--glass-user-blur, var(--ios-glass-blur))) saturate(var(--glass-user-sat,var(--ios-glass-sat)));
 backdrop-filter: blur(var(--glass-user-blur, var(--ios-glass-blur))) saturate(var(--glass-user-sat,var(--ios-glass-sat)));
 border: 1px solid var(--ios-glass-border);
 box-shadow: inset 0 1px 0 var(--ios-glass-hilite), inset 0 -1px 0 rgba(255,255,255,.17), var(--ios-glass-shadow);
 border-radius: var(--ios-radius, 28px);
}
.ios-glass::before, .ios-glass::after { content:""; position:absolute; pointer-events:none; inset:0; border-radius: inherit; z-index:-1; }
.ios-glass::before {
 background: linear-gradient(160deg,rgba(255,255,255,.37) 0%, rgba(255,255,255,.04) 30%, transparent 61%, rgba(255,255,255,.085) 100%);
 opacity:var(--glass-user-opacity,1);
}
.ios-glass::after {
 inset: 1px;
 box-shadow: inset 1.1px 1.4px 2px rgba(255,255,255,.29), inset -1px -1.5px 1.8px rgba(69,74,108,.075);
}
[data-theme="dark"] .ios-glass {--ios-glass-border: rgba(255,255,255,.22); --ios-glass-hilite:rgba(255,255,255,.22);
--ios-glass-shadow:0 20px 43px rgba(0,0,0,.25),0 1px 4px rgba(0,0,0,.20)}
[data-theme="dark"] .ios-glass::before { background:linear-gradient(154deg,rgba(255,255,255,.13),rgba(255,255,255,.025) 45%,transparent 70%,rgba(255,255,255,.05)) }
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) { .ios-glass { background:rgba(247,248,254,.94) } [data-theme="dark"] .ios-glass {background:rgba(37,39,52,.96)} }
@media (prefers-reduced-transparency:reduce) { .ios-glass { -webkit-backdrop-filter:none!important; backdrop-filter:none!important; background:rgba(249,250,255,.96)!important } [data-theme="dark"] .ios-glass {background:rgba(30,31,45,.98)!important} }
''')
for v in g:
 n=v['name']; b=v['blurs'][0] if v['blurs'] else None
 blur,sat,tint=baseline(n)
 if b:
  blur=f'{b["radius"]:g}px';sat=f'{b["saturation"]:g}'
 style=f'--ios-glass-blur:{blur};--ios-glass-sat:{sat};--ios-glass-tint:{tint};'
 if 'Dark/' in n: style+='--ios-glass-border:rgba(255,255,255,.23);--ios-glass-hilite:rgba(255,255,255,.19);'
 if 'Inactive' in n:style+='--ios-glass-shadow:0 1px 5px rgba(50,50,70,.04);'
 css.append(f'.{v["cssClass"]} {{{style}}}')
css.append('''
/* Equivalentes semânticos práticos para os aplicativos */
.ios-glass--small {--ios-glass-blur:6px;--ios-glass-sat:2;--ios-radius:999px}
.ios-glass--medium {--ios-glass-blur:15px;--ios-glass-sat:1.4}
.ios-glass--large {--ios-glass-blur:30px;--ios-glass-sat:1.4}
.ios-glass--tinted {--ios-glass-blur:6px;--ios-glass-sat:1;--ios-glass-tint:rgba(104,140,240,.27)}
[data-theme="dark"] .ios-glass--small {--ios-glass-sat:1;--ios-glass-tint:rgba(60,64,88,.30)}
[data-theme="dark"] .ios-glass--medium {--ios-glass-blur:30px;--ios-glass-sat:1.2;--ios-glass-tint:rgba(47,50,66,.25)}
[data-theme="dark"] .ios-glass--large {--ios-glass-blur:30px;--ios-glass-sat:1.2;--ios-glass-tint:rgba(38,41,57,.32)}
[data-theme="dark"] .ios-glass--tinted {--ios-glass-tint:rgba(77,102,188,.33)}
''')
(root/'css/glass.css').write_text('\n'.join(css)+'\n')
styles=['/* Classes tipográficas extraídas de 105 estilos do Sketch. Não redistribui fontes Apple. */',':root { --ios-font: -apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif; }']
for v in d['typography']:
 size=v['size']
 if size is None: continue
 name='ios-type--'+sl(v['name'])
 weight='700' if 'Bold' in (v['name'] or '') else ('600' if 'Semibold' in (v['font'] or '') or 'Headline' in (v['name'] or '') else '400')
 variant='font-style:italic;' if 'Italic' in v['name'] else ''
 line=f'line-height:{v["lineHeight"]:g}px;' if v['lineHeight'] and v['lineHeight']>=size else 'line-height:1.2;'
 styles.append(f'.{name} {{font-family:var(--ios-font);font-size:{size:g}px;{line}font-weight:{weight};{variant}}}')
(root/'css/typography.css').write_text('\n'.join(styles)+'\n')
# Embedding summaries permits file:// preview without fetch.
palette=[{'name':s['name'],'hex':s['value']['hex'],'alpha':s['value']['alpha'],'css':s['value']['css'],'token':s['token']} for s in d['swatches']]
summaries=[{'name':s['name'].removeprefix('Liquid Glass/'),'class':s['cssClass'],'blur':s['blurs'][0]['radius'] if s['blurs'] else 0,'sat':s['blurs'][0]['saturation'] if s['blurs'] else None,'depth':s['blurs'][0]['depth'] if s['blurs'] else None,'distortion':s['blurs'][0]['distortion'] if s['blurs'] else None,'fills':len(s['fills']),'shadows':len(s['shadows'])} for s in g]
(root/'js/catalog.js').write_text('/* Dados do Sketch embutidos: visualização funciona até em file:// */\nwindow.IOS27_PALETTE='+json.dumps(palette,ensure_ascii=False,separators=(',',':'))+';\nwindow.IOS27_GLASS='+json.dumps(summaries,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
print('Generated: CSS 19 Glass + CSS 105 text styles + embedded datasets')
