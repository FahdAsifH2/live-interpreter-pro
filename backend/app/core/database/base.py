from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import urllib.parse

# Supabase requires SSL, so ensure the connection string includes sslmode=require
# If not present, add it
database_url = settings.DATABASE_URL
if "supabase" in database_url.lower() and "sslmode" not in database_url.lower():
    # Parse and add sslmode if using Supabase
    parsed = urllib.parse.urlparse(database_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    query_params['sslmode'] = ['require']
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    database_url = urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )

engine = create_engine(
    database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"sslmode": "require"} if "supabase" in database_url.lower() else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

