import aiosqlite
from backend.config import DATABASE_PATH


async def get_db():
    db = await aiosqlite.connect(str(DATABASE_PATH))
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    async with aiosqlite.connect(str(DATABASE_PATH)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scrape_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                location TEXT DEFAULT '',
                niche TEXT DEFAULT '',
                results_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                error TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()
