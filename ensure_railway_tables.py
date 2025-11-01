#!/usr/bin/env python3
"""
Ensure database tables are created in Railway deployment
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

async def ensure_tables():
    """Ensure all database tables are created"""
    try:
        from app.core.database import init_database
        from app.models.base import Base
        from app.models.lead import Lead
        from app.models.assessment import Assessment
        from app.models.campaign import Campaign
        from app.models.co_creator_program import CoCreatorProgram, CoCreator
        from app.models.payment_transaction import PaymentTransaction
        from app.models.founder_story import FounderStory
        from app.models.event import Event
        from app.models.chat_session import ChatSession
        from app.models.crm_integration import CRMIntegration
        from app.models.user import User
        
        print("Initializing database and creating tables...")
        print("=" * 50)
        
        # Initialize database
        engine, session_factory = init_database()
        
        # Create all tables
        async with engine.begin() as conn:
            print("Creating all database tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully")
        
        # Verify tables exist
        async with engine.begin() as conn:
            print("\nVerifying tables exist...")
            
            # Check for key tables
            tables_to_check = [
                'leads', 'assessments', 'campaigns', 'co_creator_programs', 
                'co_creators', 'payment_transactions', 'founder_stories',
                'events', 'chat_sessions', 'crm_integrations', 'users'
            ]
            
            for table_name in tables_to_check:
                result = await conn.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """)
                exists = result.scalar()
                if exists:
                    print(f"✅ Table '{table_name}' exists")
                else:
                    print(f"❌ Table '{table_name}' missing")
        
        # Check if preferred_crm column exists in leads table
        async with engine.begin() as conn:
            print("\nChecking CRM-related columns...")
            result = await conn.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'leads' 
                AND column_name IN ('preferred_crm', 'current_crm_system')
                ORDER BY column_name;
            """)
            
            columns = result.fetchall()
            for column in columns:
                print(f"✅ Column '{column[0]}' ({column[1]}) exists in leads table")
        
        await engine.dispose()
        print("\n🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main function"""
    print("Railway Database Table Creation")
    print("=" * 50)
    
    # Check environment
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"✅ Database URL found: {database_url[:50]}...")
    else:
        print("⚠️  DATABASE_URL not found in environment")
    
    # Run table creation
    success = asyncio.run(ensure_tables())
    
    if success:
        print("\n✅ Railway database setup completed successfully!")
        print("The following features are now available:")
        print("- CRM selector with preferred_crm storage")
        print("- Compact assessment IDs (assess_YYMMDD_xxxx)")
        print("- Complete assessment flow with lead capture")
        print("- All database tables created and verified")
    else:
        print("\n❌ Database setup failed. Check the logs above.")

if __name__ == "__main__":
    main()