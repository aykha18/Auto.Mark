import asyncio
import asyncpg

async def fix_production_schema():
    # Connect to Railway production database
    conn = await asyncpg.connect(
        'postgresql://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway'
    )
    
    try:
        print("🔗 Connected to Railway production database")
        
        # Add missing columns
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_requested BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_requested")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_booked BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_booked")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_completed")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_type VARCHAR(100);
        ''')
        print("✓ Added consultation_type")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_challenges TEXT;
        ''')
        print("✓ Added consultation_challenges")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_scheduled_at TIMESTAMP;
        ''')
        print("✓ Added consultation_scheduled_at")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed_at TIMESTAMP;
        ''')
        print("✓ Added consultation_completed_at")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_requested BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_requested")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_generated")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_sent BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_sent")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_id VARCHAR(100);
        ''')
        print("✓ Added ai_report_id")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated_at TIMESTAMP;
        ''')
        print("✓ Added ai_report_generated_at")
        
        # Check if lead_id column exists and remove it (it's not in the model)
        result = await conn.fetchval('''
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'leads' AND column_name = 'lead_id'
        ''')
        
        if result > 0:
            await conn.execute('ALTER TABLE leads DROP COLUMN lead_id;')
            print("✓ Removed lead_id column")
        
        print("\n✅ Production database schema updated successfully!")
        
        # Show current columns
        columns = await conn.fetch('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'leads' 
            ORDER BY ordinal_position
        ''')
        
        print("\n📋 Current leads table columns in production:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("\n🔌 Disconnected from database")

if __name__ == '__main__':
    asyncio.run(fix_production_schema())
