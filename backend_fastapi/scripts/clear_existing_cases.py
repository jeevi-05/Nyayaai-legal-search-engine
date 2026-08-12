"""
Database Cleanup Script
=======================
Removes dummy cases, manually inserted documents, and sample PDF records.
Does NOT delete database schema - keeps tables, relationships, embeddings structure.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()


def clear_existing_cases():
    """Remove dummy cases, manually inserted documents, and sample PDF records."""
    
    # Parse DATABASE_URL to determine database type
    db_url = settings.DATABASE_URL
    
    if "sqlite" in db_url:
        # SQLite database
        engine = create_engine(db_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            try:
                # Delete records from legal_documents table
                # Keep only records that were properly ingested from Indian Kanoon API
                # Remove records with source='dataset', source='manual', or empty judgment_text
                
                delete_query = """
                    DELETE FROM legal_documents 
                    WHERE source IN ('dataset', 'manual', 'local')
                    OR (source IS NULL AND file_type = 'JSON')
                    OR (judgment_text IS NULL OR judgment_text = '')
                """
                
                result = session.execute(text(delete_query))
                session.commit()
                
                print(f"✓ Deleted {result.rowcount} dummy/manual cases from database")
                
                # Show remaining records
                count_query = "SELECT COUNT(*) FROM legal_documents"
                count_result = session.execute(text(count_query))
                remaining = count_result.scalar()
                print(f"✓ Remaining records in database: {remaining}")
                
            except Exception as e:
                session.rollback()
                print(f"✗ Error clearing cases: {e}")
                raise
            finally:
                session.close()
                
    else:
        # PostgreSQL or other database
        print("⚠️  Database cleanup script is configured for SQLite only.")
        print("   For PostgreSQL, please run the following SQL manually:")
        print("""
            DELETE FROM legal_documents 
            WHERE source IN ('dataset', 'manual', 'local')
            OR (source IS NULL AND file_type = 'JSON')
            OR (judgment_text IS NULL OR judgment_text = '');
        """)


if __name__ == "__main__":
    print("=" * 60)
    print("NyayaAI Database Cleanup Script")
    print("=" * 60)
    print()
    
    try:
        clear_existing_cases()
        print()
        print("✓ Database cleanup completed successfully!")
    except Exception as e:
        print()
        print(f"✗ Database cleanup failed: {e}")
        sys.exit(1)
