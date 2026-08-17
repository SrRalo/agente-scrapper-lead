import json
from pathlib import Path
from backend.config import BRIEFS_DIR


def generate_brief(lead: dict, extra_data: dict = None) -> str:
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    data = {**lead}
    if extra_data:
        data.update(extra_data)

    brief_data = {}
    if lead.get("brief_data"):
        try:
            brief_data = json.loads(lead["brief_data"])
        except json.JSONDecodeError:
            pass

    name = data.get("business_name", "Negocio")
    slug = data.get("slug", "negocio")
    biz_type = data.get("business_type", "servicio")
    category = data.get("category", "")
    desc = data.get("description_short", "Descripción no disponible")
    city = data.get("city", "")
    country = data.get("country", "")
    rating = data.get("rating", 0)
    reviews = data.get("reviews_count", 0)
    phone = data.get("phone", "No disponible")
    email = data.get("email", "No disponible")
    website = data.get("website", "No disponible")
    address = data.get("address", "No disponible")

    tagline = brief_data.get("tagline", f"{name} - Tu mejor opción en {category or biz_type}")
    tone = brief_data.get("tone", "profesional y cercano")
    audience = brief_data.get("audience", f"Clientes en {city}" if city else "Público general")
    objective = brief_data.get("objective", "Contactar al negocio para más información")

    hero_title = brief_data.get("hero_title", name)
    hero_subtitle = brief_data.get("hero_subtitle", desc or tagline)
    cta_text = brief_data.get("cta_text", "Contáctanos")
    cta_url = brief_data.get("cta_url", f"tel:{phone}" if phone != "No disponible" else "#contacto")

    features = brief_data.get("features", [])
    faq = brief_data.get("faq", [])
    pricing = brief_data.get("pricing", [])
    testimonials = brief_data.get("testimonials", [])
    colors = brief_data.get("colors", {})
    form_fields = brief_data.get("form_fields", [])

    images = []
    if data.get("images"):
        try:
            images = json.loads(data["images"]) if isinstance(data["images"], str) else data["images"]
        except (json.JSONDecodeError, TypeError):
            pass

    md = f"""---
# Brief: {name}
# Generado automáticamente por Lead Pipeline
# Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
slug: {slug}
status: brief_generated
---

# Brief del Proyecto: {name}

## Información del Negocio

| Campo | Valor |
|-------|-------|
| **Nombre** | {name} |
| **Tipo** | {biz_type} |
| **Categoría** | {category} |
| **Ciudad** | {city} |
| **País** | {country} |
| **Rating** | {rating} ({reviews} reseñas) |
| **Teléfono** | {phone} |
| **Email** | {email} |
| **Web** | {website} |
| **Dirección** | {address} |

---

## Identidad

- **Tagline:** {tagline}
- **Tono de voz:** {tone}

---

## Contenido

### Hero

- **Título:** {hero_title}
- **Subtítulo:** {hero_subtitle}
- **CTA:** [{cta_text}]({cta_url})

### Audiencia Principal

{audience}

### Objetivo de Conversión

{objective}

---

## Descripción del Negocio

{desc}

---

## Características / Beneficios

"""
    if features:
        for f in features:
            md += f"- {f}\n"
    else:
        md += "_Pendiente de completar_\n"

    md += "\n---\n\n## FAQ\n\n"
    if faq:
        for item in faq:
            q = item.get("q", "") if isinstance(item, dict) else item
            a = item.get("a", "") if isinstance(item, dict) else ""
            md += f"**Q:** {q}\n**A:** {a}\n\n"
    else:
        md += "_Pendiente de completar_\n"

    md += "\n---\n\n## Precios / Planes\n\n"
    if pricing:
        for p in pricing:
            if isinstance(p, dict):
                md += f"### {p.get('name', 'Plan')}\n"
                md += f"- **Precio:** {p.get('price', 'Consultar')}\n"
                md += f"- **Detalle:** {p.get('detail', '')}\n\n"
            else:
                md += f"- {p}\n"
    else:
        md += "_No aplica o pendiente de completar_\n"

    md += "\n---\n\n## Testimonios\n\n"
    if testimonials:
        for t in testimonials:
            if isinstance(t, dict):
                md += f"> {t.get('text', '')} — _{t.get('author', 'Anónimo')}_\n\n"
            else:
                md += f"> {t}\n\n"
    else:
        md += "_Pendiente de completar_\n"

    md += f"""
---

## Imágenes

- **Logo:** {data.get('logo_url', 'Pendiente')}
- **Hero:** {data.get('hero_url', 'Pendiente')}
"""
    if images:
        md += "- **Galería:**\n"
        for img in images:
            md += f"  - {img}\n"

    md += f"""
---

## Formulario de Contacto

"""
    if form_fields:
        md += "### Campos del formulario\n\n"
        for field in form_fields:
            md += f"- {field}\n"
    else:
        md += f"### Formulario básico\n- Nombre\n- Email\n- Teléfono\n- Mensaje\n\n**Destino:** {email}\n"

    md += f"""
---

## Paleta de Colores

"""
    if colors:
        for k, v in colors.items():
            md += f"- **{k}:** {v}\n"
    else:
        md += "_Pendiente de definir_\n"

    md += f"""

---

## Notas para el Agente Web Builder

- Copiar el contenido real del negocio, NO inventar datos.
- Si falta información crítica (precios, descripción detallada), marcar como "Pendiente".
- El CTA debe ser prominente y funcionar.
- Incluir schema markup para {biz_type} local.
- Responsive design obligatorio.
- SEO local: título, meta description, Open Graph con datos reales.
"""

    filepath = BRIEFS_DIR / f"{slug}.md"
    filepath.write_text(md, encoding="utf-8")

    return str(filepath)
