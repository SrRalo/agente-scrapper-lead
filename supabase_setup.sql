-- ============================================
-- EJECUTA ESTO EN SUPABASE SQL EDITOR
-- ============================================
-- Supabase Dashboard > SQL Editor > New Query > Paste this > Run

-- 1. Crear tabla leads
CREATE TABLE IF NOT EXISTS leads (
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
  brief_content TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Crear tabla scrape_jobs
CREATE TABLE IF NOT EXISTS scrape_jobs (
  id BIGSERIAL PRIMARY KEY,
  query TEXT NOT NULL,
  location TEXT DEFAULT '',
  niche TEXT DEFAULT '',
  results_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  error TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Habilitar Row Level Security
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;

-- 4. Crear policies (solo usuarios autenticados pueden acceder)
CREATE POLICY "Authenticated users can CRUD leads" ON leads
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can CRUD scrape_jobs" ON scrape_jobs
  FOR ALL USING (auth.role() = 'authenticated');

-- ============================================
-- LISTO! Ahora crea tu usuario en Auth:
-- Authentication > Users > Add User
-- Email: tu@email.com
-- Password: tu_contraseña_segura
-- Email Confirm: OFF
-- ============================================
