from pathlib import Path
import json
import re

base = Path(__file__).resolve().parent
target = base / "index.html"
data = json.loads((base / "news-data.json").read_text(encoding="utf-8"))
html = target.read_text(encoding="utf-8")

news_js = "const NEWS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
html, n = re.subn(
    r"const NEWS=\[.*?\];\nconst TOPICS=",
    news_js + "\nconst TOPICS=",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("No se pudo actualizar el bloque NEWS")

html = html.replace(
    'content="Te Equipamos News — demo funcional con noticias ficticias de ejemplo."',
    'content="Te Equipamos News — actualidad, deporte, tecnología, outdoor y novedades."',
)
html = html.replace(
    '<div class="demo"><b>DEMO FUNCIONAL</b><span>Todos los titulares, fuentes y artículos de esta versión son ficticios y sirven únicamente como ejemplo.</span></div>',
    '<div class="demo"><b>EDICIÓN REAL · 8 SEP 2026</b><span>Noticias verificadas y resumidas por Te Equipamos con enlace directo a la fuente original.</span></div>',
)
html = html.replace(
    'Botón de demostración preparado para conectar más adelante con tu newsletter.',
    'Próximamente podrás recibir una selección diaria de noticias y novedades.',
)
html = html.replace('title="Demo">J</button>', 'title="Te Equipamos">J</button>')

primary = '.primary{width:100%;border:0;border-radius:22px;background:var(--accent);color:#fff;padding:11px 14px;font-weight:800;cursor:pointer}'
source_css = '.sourceBtn{display:inline-block;margin-top:16px;background:var(--accent);color:#fff;padding:11px 18px;border-radius:22px;font-family:Arial,sans-serif;font-size:14px;font-weight:800}'
if source_css not in html:
    html = html.replace(primary, primary + source_css)

article_fn = r'''function renderArticle(id){const n=NEWS.find(x=>x.id===Number(id));if(!n){history.replaceState({},"","./");renderPortal();return}$("#portalView").classList.add("hidden");$("#articleView").classList.remove("hidden");document.title=`${n.title} — Te Equipamos News`;const ps=[n.summary,n.details||"Te Equipamos ha preparado este resumen para ofrecer una lectura rápida de la actualidad.","Este contenido ha sido redactado de forma independiente a partir de la información publicada por la fuente indicada. Para consultar todos los detalles, contexto y posibles actualizaciones, utiliza el enlace a la noticia original."];$("#article").innerHTML=`<img class="articleHero" src="${esc(n.image)}" alt="${esc(n.title)}"><div class="articleBody"><span class="kicker">${esc(n.category)} · Actualidad</span><h1>${esc(n.title)}</h1><p class="deck">${esc(n.summary)}</p><div class="byline"><strong>Te Equipamos News</strong><span>•</span><span>Fuente: ${esc(n.source)}</span><span>•</span><span>${esc(n.time)}</span></div><div class="copy">${ps.map((p,i)=>`${i===1?'<h2>Lo más importante</h2>':''}<p>${esc(p)}</p>`).join("")}<a class="sourceBtn" href="${esc(n.url)}" target="_blank" rel="noopener noreferrer">Leer noticia original en ${esc(n.source)} ↗</a></div><div class="note"><strong>Transparencia editorial:</strong> Te Equipamos resume y contextualiza la información. La autoría y el contenido completo pertenecen al medio enlazado. Imagen de portada ilustrativa.</div></div>`;$("#related").innerHTML=NEWS.filter(x=>x.id!==n.id).slice(0,4).map(x=>`<div class="rel" data-article="${x.id}"><b>${esc(x.title)}</b><small>${esc(x.category)} · ${esc(x.time)}</small></div>`).join("")}
'''

html, n = re.subn(
    r"function renderArticle\(id\)\{.*?\}\nfunction closeMenu\(\)",
    article_fn + "\nfunction closeMenu()",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError("No se pudo actualizar renderArticle")

target.write_text(html, encoding="utf-8")
print(f"Te Equipamos News actualizado con {len(data)} noticias reales")
