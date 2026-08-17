# Plan: Supabase Auth + PostgreSQL + Deploy a Vercel

## Resumen
Migrar el proyecto de SQLite local a Supabase PostgreSQL, agregar autenticación de usuario único con Supabase Auth, y desplegar en Vercel como serverless functions.

---

## Arquitectura Actual → Nueva

```
ACTUAL:                          NUEVO:
FastAPI + SQLite local           FastAPI (Vercel Serverless)
↓                                ↓
uvicorn :8000                    Supabase PostgreSQL (DB)
↓                                ↓
Sin auth                         Supabase Auth (JWT)
↓                                ↓
localhost                        Vercel (HTTPS + dominio)
```

---

## Fase 1: Configuración de Supabase

### 1.1 Crear tabla `leads` en Supabase SQL Editor
```sql
-- Ejecutar en Supabase SQL Editor
CREATE TABLE leads (
  id BIGSERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  business_name TEXT NOT NULL,
  business_type TEXT DEFAULT '',
  category TEXT DEFAULT '',
  description_short TEXT DEFAULT '',
  phone TEXT DEFAULT '',
  email TEXT DEFAULT '',
  website TEXT DEFAULT '',
  address TEXT DEFAULT '',
  city TEXT DEFAULT '',
  country TEXT DEFAULT '',
  rating REAL DEFAULT 0,
  reviews_count INTEGER DEFAULT 0,
  place_id TEXT DEFAULT '',
  google_url TEXT DEFAULT '',
  logo_url TEXT DEFAULT '',
  hero_url TEXT DEFAULT '',
  images TEXT DEFAULT '[]',
  status TEXT DEFAULT 'scraped',
  notes TEXT DEFAULT '',
  contact_method TEXT DEFAULT '',
  contact_date TEXT DEFAULT '',
  brief_data TEXT DEFAULT '{}',
  problem TEXT DEFAULT '',
  problem_key TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla scrape_jobs (opcional, para tracking)
CREATE TABLE scrape_jobs (
  id BIGSERIAL PRIMARY KEY,
  query TEXT NOT NULL,
  location TEXT DEFAULT '',
  niche TEXT DEFAULT '',
  results_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  error TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS (Row Level Security)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;

-- Policy: solo usuarios autificados pueden acceder
CREATE POLICY "Authenticated users can CRUD leads" ON leads
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can CRUD scrape_jobs" ON scrape_jobs
  FOR ALL USING (auth.role() = 'authenticated');
```

### 1.2 Crear usuario único en Supabase Auth
- Ir a Authentication → Users → Add User
- Email: `adrian@tu-dominio.com` (o el que prefieras)
- Password: contraseña segura
- Email Confirm: OFF (ya que eres el único usuario)

### 1.3 Obtener credenciales de Supabase
- Settings → API
- `SUPABASE_URL`: `https://xxxxx.supabase.co`
- `SUPABASE_ANON_KEY`: `eyJhbGciOi...` (public, va en frontend)
- `SUPABASE_SERVICE_KEY`: `eyJhbGciOi...` (secret, solo backend)

---

## Fase 2: Migración del Backend

### 2.1 Nuevas dependencias (`requirements.txt`)
```txt
fastapi
uvicorn[standard]
pydantic
serpapi
python-dotenv
asyncpg          # PostgreSQL async driver (reemplaza aiosqlite)
supabase         # Supabase Python SDK (para auth)
python-jose[cryptography]  # JWT verification
starlette        # Para session middleware
```

### 2.2 Nuevo archivo `backend/config.py`
- Agregar: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`
- Mantener: `SERPAPI_KEY`, `BRIEFS_DIR`, `LEAD_STATUSES`

### 2.3 Nuevo archivo `backend/database.py`
- Conexión async a PostgreSQL con `asyncpg`
- Pool de conexiones global
- Funciones helper: `fetch_one()`, `fetch_all()`, `execute()`

### 2.4 Nuevo archivo `backend/auth.py`
- Función `verify_token(token: str)` que valida JWT de Supabase
- Decodificar JWT usando `python-jose` con el `SUPABASE_JWT_SECRET`
- Dependency `get_current_user` para FastAPI

### 2.5 Modificar `backend/models.py`
- Eliminar `aiosqlite` y `init_db()` (la tabla ya existe en Supabase)
- Eliminar `get_db()` (reemplazar por `database.py`)

### 2.6 Modificar todas las rutas (`backend/routes/`)
- Agregar dependency `user = Depends(get_current_user)` a cada endpoint
- Reemplazar queries de SQLite por PostgreSQL (asyncpg)
- Cambiar `?` placeholders por `$1, $2, ...` (formato PostgreSQL)
- Los archivos a modificar:
  - `routes/leads.py`
  - `routes/scraper.py`
  - `routes/briefs.py`

### 2.7 Modificar `backend/app.py`
- Eliminar `init_db()` del lifespan
- Agregar middleware CORS (para Vercel frontend)
- Agregar startup/shutdown para el pool de PostgreSQL
- Mantener: favicon, static files, routes

### 2.8 Nuevo archivo `backend/brief_generator.py` (ajuste menor)
- Las rutas de archivos briefs seguirán siendo locales (en Vercel son temporales)
- Opcional: subir briefs a Supabase Storage

---

## Fase 3: Frontend (Login + Auth Flow)

### 3.1 Nuevo archivo `frontend/login.html`
- Formulario de email + password
- Llamada a Supabase Auth `signInWithPassword()`
- Guardar `access_token` en localStorage
- Redirigir a `/dashboard` al autenticarse
- Diseño dark theme consistente con el dashboard

### 3.2 Modificar `frontend/index.html`
- Al cargar, verificar si hay `access_token` en localStorage
- Si no hay token → redirigir a `/login`
- Agregar botón "Cerrar Sesión" en el sidebar
- Agregar header `Authorization: Bearer <token>` a todas las llamadas API
- Función `logout()` que limpie localStorage y redirija a `/login`

### 3.3 Nuevo archivo `frontend/js/auth.js`
- `supabaseClient` inicializado con URL + anon key
- `signOut()` function
- `getSession()` function
- `isAuthenticated()` check

---

## Fase 4: Deploy a Vercel

### 4.1 Archivo `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "backend/app.py" },
    { "src": "/js/(.*)", "dest": "/frontend/js/$1" },
    { "src": "/css/(.*)", "dest": "/frontend/css/$1" },
    { "src": "/favicon.ico", "dest": "backend/app.py" },
    { "src": "/login", "dest": "/frontend/login.html" },
    { "src": "/(.*)", "dest": "backend/app.py" }
  ]
}
```

### 4.2 Variables de entorno en Vercel
- Ir a Vercel Dashboard → Settings → Environment Variables
- Agregar:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_KEY`
  - `SUPABASE_JWT_SECRET`
  - `SERPAPI_KEY`
  - `DATABASE_URL` (connection string de Supabase PostgreSQL)

### 4.3 Adaptar `app.py` para Vercel
- Exportar `app` como variable global (Vercel lo detecta automáticamente)
- El `lifespan` de FastAPI funciona con Vercel
- Static files: servir desde `/frontend` montado como StaticFiles

### 4.4 Instalar Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

---

## Fase 5: Testing

### 5.1 Local
```bash
# Copiar .env.example a .env y llenar credenciales
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```
- Probar login en `localhost:8000/login`
- Probar CRUD de leads
- Probar scraper
- Probar generación de briefs

### 5.2 En Vercel
- Verificar que el login funciona
- Verificar que todas las API routes responden
- Verificar que el scraper funciona (SerpAPI key)
- Verificar que los briefs se generan

---

## Archivos que se MODIFICAN
- `backend/app.py` — CORS, lifespan, static mount
- `backend/config.py` — nuevas env vars
- `backend/models.py` — eliminar SQLite, usar asyncpg
- `backend/schemas.py` — sin cambios significativos
- `backend/routes/leads.py` — queries PostgreSQL + auth
- `backend/routes/scraper.py` — queries PostgreSQL + auth
- `backend/routes/briefs.py` — queries PostgreSQL + auth
- `frontend/index.html` — auth check + logout + auth headers
- `requirements.txt` — nuevas dependencias

## Archivos que se CREAN
- `backend/database.py` — pool PostgreSQL
- `backend/auth.py` — JWT verification
- `frontend/login.html` — página de login
- `frontend/js/auth.js` — helper de autenticación
- `vercel.json` — configuración de deploy
- `.env.example` — plantilla de variables

## Archivos que se ELIMINAN
- `data/leads.db` — ya no se usa (migrado a Supabase)
- `run.bat` — reemplazado por Vercel (o mantener para local)

---

## Estimación de tiempo
- Fase 1 (Supabase): ~10 min (configuración manual en dashboard)
- Fase 2 (Backend): ~30 min
- Fase 3 (Frontend): ~20 min
- Fase 4 (Vercel): ~15 min
- Fase 5 (Testing): ~15 min

**Total: ~90 minutos**

---

## Riesgos y Consideraciones
1. **Vercel cold start**: Las primeras llamadas pueden tardar 2-5s
2. **SQLite briefs**: En Vercel los archivos son efímeros. Los briefs se perderán entre requests. Solución: usar Supabase Storage o Redis
3. **SerpAPI key**: Se expone en variables de entorno de Vercel (cifradas)
4. **CORS**: Necesario para Vercel ya que frontend y backend están en dominios diferentes
5. **Costo Supabase**: Free tier permite 500MB DB + 50K usuarios auth (suficiente para uso personal)
