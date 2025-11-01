#!/usr/bin/env python3
"""
Configure Railway URLs for frontend and backend communication
"""

import os
import re

def configure_railway_urls():
    """Configure Railway URLs for deployment"""
    print("Railway URL Configuration")
    print("=" * 50)
    
    # Get Railway URLs from user
    print("Please provide your Railway service URLs:")
    print("(You can find these in your Railway dashboard)")
    print()
    
    backend_url = input("Enter your Railway BACKEND URL (e.g., https://web-production-xxxx.up.railway.app): ").strip()
    if not backend_url:
        print("❌ Backend URL is required")
        return False
    
    # Validate URL format
    if not backend_url.startswith('https://'):
        print("❌ Backend URL should start with https://")
        return False
    
    print(f"✅ Backend URL: {backend_url}")
    
    # Update frontend .env.railway file
    env_railway_path = "frontend/.env.railway"
    if os.path.exists(env_railway_path):
        with open(env_railway_path, 'r') as f:
            content = f.read()
        
        # Replace the placeholder URLs
        content = re.sub(
            r'REACT_APP_API_URL=https://web-production-XXXX\.up\.railway\.app',
            f'REACT_APP_API_URL={backend_url}',
            content
        )
        content = re.sub(
            r'REACT_APP_WS_URL=wss://web-production-XXXX\.up\.railway\.app/ws',
            f'REACT_APP_WS_URL={backend_url.replace("https://", "wss://")}/ws',
            content
        )
        
        with open(env_railway_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {env_railway_path}")
    
    # Update frontend .env.production file
    env_prod_path = "frontend/.env.production"
    if os.path.exists(env_prod_path):
        with open(env_prod_path, 'r') as f:
            content = f.read()
        
        # Replace the placeholder URL
        content = re.sub(
            r'REACT_APP_API_URL=https://your-backend-service\.railway\.app',
            f'REACT_APP_API_URL={backend_url}',
            content
        )
        content = re.sub(
            r'REACT_APP_WS_URL=wss://your-backend-service\.railway\.app/ws',
            f'REACT_APP_WS_URL={backend_url.replace("https://", "wss://")}/ws',
            content
        )
        
        with open(env_prod_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {env_prod_path}")
    
    print("\n🎉 Railway URLs configured successfully!")
    print("\nNext steps:")
    print("1. Commit and push the changes:")
    print("   git add frontend/.env.railway frontend/.env.production")
    print("   git commit -m 'configure Railway URLs for API communication'")
    print("   git push origin master")
    print("\n2. Redeploy your Railway frontend service")
    print("\n3. Test the API connection")
    
    return True

def main():
    """Main function"""
    try:
        configure_railway_urls()
    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()