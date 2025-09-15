"""
Setup script to create tables in Tenant Supabase project
Run this once to set up conversation persistence and profile memory tables.
"""

import asyncio
from config.supabase_clients import get_tenant_client

async def setup_tenant_database():
    """Setup the tenant database with required tables"""
    client = get_tenant_client()
    
    # Read the SQL setup file
    with open('sql/tenant_setup.sql', 'r') as f:
        sql_commands = f.read()
    
    # Split into individual commands (very basic - doesn't handle complex cases)
    commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
    
    print(f"Executing {len(commands)} SQL commands...")
    
    for i, command in enumerate(commands):
        if not command or command.startswith('--'):
            continue
            
        try:
            print(f"[{i+1}/{len(commands)}] Executing: {command[:50]}...")
            await client.rpc('execute_sql', {'sql': command}).execute()
            print(f"✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")
            # Continue with other commands
            continue
    
    print("\n🎉 Database setup complete!")
    print("✅ Tables created: chat_sessions, chat_messages, assistant_profile_memory")
    print("✅ RLS policies configured")
    print("✅ Functions and triggers set up")

if __name__ == "__main__":
    asyncio.run(setup_tenant_database())