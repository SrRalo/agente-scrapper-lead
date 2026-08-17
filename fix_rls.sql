-- ============================================
-- MIGRACIÓN: RLS off + brief_content column
-- Ejecuta esto en Supabase SQL Editor
-- ============================================

-- 1. Desactivar RLS (el backend ya verifica JWT)
ALTER TABLE leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_jobs DISABLE ROW LEVEL SECURITY;

-- 2. Agregar columna para almacenar el brief generado
ALTER TABLE leads ADD COLUMN IF NOT EXISTS brief_content TEXT DEFAULT '';

-- 3. Verificar
SELECT COUNT(*) as total_leads FROM leads;
