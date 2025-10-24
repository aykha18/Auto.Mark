#!/usr/bin/env python3
"""
Simple Production Readiness Check for Phase 3 Marketing Agents
"""

import os
import sys
import subprocess
import importlib.util

def check_item(name, status, details=""):
    """Print a check item result"""
    status_icon = "[PASS]" if status else "[FAIL]"
    print(f"{status_icon} {name}")
    if details:
        print(f"      {details}")
    return status

def main():
    print("AI MARKETING AGENTS - PRODUCTION READINESS CHECK")
    print("=" * 55)

    passed_checks = 0
    total_checks = 0

    # 1. Python Version
    total_checks += 1
    version = sys.version_info
    version_ok = version.major == 3 and version.minor >= 11
    check_item("Python Version", version_ok, f"Current: {version.major}.{version.minor}.{version.micro} (need 3.11+)")
    if version_ok: passed_checks += 1

    # 2. Required Files
    total_checks += 1
    required_files = [
        'app/agents/base.py',
        'app/agents/state.py',
        'app/agents/orchestrator.py',
        'requirements.txt',
        '.env'
    ]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    files_ok = len(missing_files) == 0
    check_item("Required Files", files_ok, f"Missing: {missing_files}" if missing_files else "All files present")
    if files_ok: passed_checks += 1

    # 3. Dependencies
    total_checks += 1
    deps_ok = True
    missing_deps = []

    try:
        import fastapi
        print("      fastapi: OK")
    except ImportError:
        missing_deps.append("fastapi")
        deps_ok = False

    try:
        import sqlalchemy
        print("      sqlalchemy: OK")
    except ImportError:
        missing_deps.append("sqlalchemy")
        deps_ok = False

    try:
        import langchain_core
        print("      langchain-core: OK")
    except ImportError:
        missing_deps.append("langchain-core")
        deps_ok = False

    check_item("Core Dependencies", deps_ok, f"Missing: {missing_deps}" if missing_deps else "All core deps installed")
    if deps_ok: passed_checks += 1

    # 4. Environment Variables
    total_checks += 1
    from dotenv import load_dotenv
    load_dotenv()

    required_env = ['OPENAI_API_KEY', 'GROK_API_KEY', 'LANGCHAIN_API_KEY', 'PINECONE_API_KEY']
    missing_env = [key for key in required_env if not os.getenv(key) or os.getenv(key).startswith('your_')]

    env_ok = len(missing_env) == 0
    check_item("API Keys", env_ok, f"Missing: {missing_env}" if missing_env else "All required keys set")
    if env_ok: passed_checks += 1

    # 5. Database Configuration
    total_checks += 1
    db_url = os.getenv('DATABASE_URL', '')
    db_ok = bool(db_url) and not db_url.startswith('your_')
    check_item("Database Config", db_ok, "DATABASE_URL configured" if db_ok else "DATABASE_URL not set")
    if db_ok: passed_checks += 1

    # 6. Basic Import Test
    total_checks += 1
    import_ok = True
    try:
        from app.agents.state import MarketingAgentState
        print("      MarketingAgentState: OK")
    except Exception as e:
        print(f"      MarketingAgentState: FAIL - {e}")
        import_ok = False

    try:
        from app.agents.base import BaseAgent
        print("      BaseAgent: OK")
    except Exception as e:
        print(f"      BaseAgent: FAIL - {e}")
        import_ok = False

    check_item("Module Imports", import_ok, "Core modules import successfully" if import_ok else "Import errors detected")
    if import_ok: passed_checks += 1

    # 7. Mock Test
    total_checks += 1
    mock_ok = False
    try:
        result = subprocess.run([sys.executable, 'mock_agents.py'],
                              capture_output=True, text=True, timeout=10)
        mock_ok = result.returncode == 0
    except:
        pass

    check_item("Mock Agents Test", mock_ok, "Mock agents run successfully" if mock_ok else "Mock agents test failed")
    if mock_ok: passed_checks += 1

    # Summary
    print("\n" + "=" * 55)
    print(f"PRODUCTION READINESS: {passed_checks}/{total_checks} checks passed")

    if passed_checks == total_checks:
        print("\n[SUCCESS] System is PRODUCTION READY!")
        print("\nNext steps:")
        print("1. python -m app.main                 # Start server")
        print("2. python test_agents_api.py          # Test APIs")
        print("3. python simple_agent_test.py        # Test real agents")

    else:
        print(f"\n[ISSUES] {total_checks - passed_checks} checks failed")
        print("\nFix these issues:")

        if not version_ok:
            print("- Upgrade Python to 3.11+")

        if missing_files:
            print(f"- Create missing files: {missing_files}")

        if missing_deps:
            print(f"- Install dependencies: pip install {' '.join(missing_deps)}")
            print("  Or run: pip install -r requirements.txt")

        if missing_env:
            print(f"- Set environment variables in .env: {missing_env}")

        if not db_ok:
            print("- Configure DATABASE_URL in .env")
            print("  For development: DATABASE_URL=sqlite+aiosqlite:///./marketing.db")

        print("\nFor development testing:")
        print("python mock_agents.py                 # Test with mock agents")
        print("python simple_agent_demo.py           # Complete demo")

    print("\n" + "=" * 55)

if __name__ == "__main__":
    main()