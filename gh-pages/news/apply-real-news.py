from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import re

base = Path(__file__).resolve().parent
target = base / "index.html"
data = json.loads((base / "news-data.json").read_text(encoding="utf-8"))
html = target.read_text(encoding="utf-8")

months = {1:"ENE",2:"FEB",3:"MAR",4:"ABR",5:"MAY",6:"JUN",7:"JUL",8:"AGO",9:"SEP",10:"OCT",11:"NOV",12:"DIC"}
today = datetime.now(ZoneInfo("Europe/Madrid"))
edition = f"{today.day} {months[today.month]} {today.year}"

news_js = "const NEWS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
html, n = re.subn(
    r"const NEWS=\[.*?\];\nconst TOPICS=",
    lambda m: news_js + "\nconst TOPICS=",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("No se pudo actualizar el bloque NEWS")

html = html.replace(
    'content="Te Equipamos News — demo funcional con noticias ficticias de ejemplo."',
    'content="Te Equipamos News — actualidad outdoor, senderismo, trail running, ciclismo, montaña, equipamiento y reviews."',
)
html = html.replace(
    '<div class="demo"><b>DEMO FUNCIONAL</b><span>Todos los titulares, fuentes y artículos de esta versión son ficticios y sirven únicamente como ejemplo.</span></div>',
    f'<div class="demo"><b>EDICIÓN OUTDOOR · {edition}</b><span>Actualidad seleccionada automáticamente y contenido propio de Te Equipamos, siempre con enlace a la fuente o landing correspondiente.</span></div>',
)
html = html.replace(
    'Espacio preparado para conectar más adelante con tu newsletter.',
    'Noticias, guías, reviews y selección outdoor de Te Equipamos.',
)

source_css = '.sourceBtn{display:inline-block;margin-top:16px;background:var(--accent);color:#fff;padding:11px 18px;border-radius:22px;font-family:Arial,sans-serif;font-size:14px;font-weight:800}'
if source_css not in html:
    html = html.replace('.empty{', source_css + '.empty{', 1)

article_fn = r'''function renderArticle(id){const n=NEWS.find(x=>x.id===Number(id));if(!n){history.replaceState({},'','./');renderPortal();return}$('#portal').classList.add('hidden');$('#articleView').classList.remove('hidden');document.title=`${n.title} — Te Equipamos News`;const own=!!n.owned;const label=own?'Contenido Te Equipamos':'Actualidad';const p=own?[n.summary,n.details||'Contenido propio de Te Equipamos.','Esta pieza forma parte del ecosistema de reviews, guías, novedades y landings de Te Equipamos.']:[n.summary,n.details||'Te Equipamos News ha seleccionado esta información por su interés para el mundo outdoor.','Para ampliar contexto, datos, declaraciones y posibles actualizaciones, consulta siempre la publicación original enlazada.'];const button=own?'Abrir contenido de Te Equipamos →':`Leer noticia original en ${esc(n.source)} ↗`;const note=own?'<strong>Contenido propio:</strong> esta publicación enlaza a una review, guía, novedad o landing de Te Equipamos.':'<strong>Transparencia editorial:</strong> Te Equipamos organiza y presenta esta información para facilitar su descubrimiento. La autoría y el contenido completo pertenecen al medio enlazado.';$('#article').innerHTML=`<img class="articleHero" src="${esc(n.image)}" alt="${esc(n.title)}"><div class="articleBody"><span class="kicker">${esc(n.category)} · ${label}</span><h1>${esc(n.title)}</h1><p class="deck">${esc(n.summary)}</p><div class="byline"><strong>${own?esc(n.source):'Te Equipamos News'}</strong><span>•</span><span>${own?'Te Equipamos':'Fuente: '+esc(n.source)}</span><span>•</span><span>${esc(n.time)}</span></div><div class="copy">${p.map((x,i)=>`${i===1?'<h2>Lo más importante</h2>':''}<p>${esc(x)}</p>`).join('')}<a class="sourceBtn" href="${esc(n.url)}" target="_blank" rel="noopener noreferrer">${button}</a></div><div class="note">${note}</div></div>`;$('#related').innerHTML=NEWS.filter(x=>x.id!==n.id).slice(0,4).map(x=>`<div class="rel" data-article="${x.id}"><b>${esc(x.title)}</b><small>${esc(x.category)} · ${esc(x.time)}</small></div>`).join('')}
'''

html, n = re.subn(
    r"function renderArticle\(id\)\{.*?\}\ndocument\.addEventListener",
    lambda m: article_fn + "document.addEventListener",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("No se pudo actualizar renderArticle")

target.write_text(html, encoding="utf-8")
print(f"Te Equipamos News actualizado con {len(data)} contenidos")
