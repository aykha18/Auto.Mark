"""
Social media management API endpoints for client-facing platform
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.twitter_service import TwitterOAuthService, get_twitter_service
from app.models.social_account import SocialAccount, SocialPost, Engagement
from app.models.campaign import Campaign
from app.models.user import User

# Mock encryption functions for now - replace with actual implementation
def encrypt_data(data: str) -> str:
    return data  # TODO: Implement proper encryption

def decrypt_data(data: str) -> str:
    return data  # TODO: Implement proper decryption

router = APIRouter()


# Pydantic models
class ConnectAccountRequest(BaseModel):
    platform: str = Field(..., description="Platform to connect (twitter, linkedin, etc.)")
    authorization_code: str = Field(..., description="OAuth authorization code")
    code_verifier: str = Field(..., description="PKCE code verifier")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    platforms: List[str] = Field(default_factory=list, description="Platforms to use")
    schedule_config: Dict[str, Any] = Field(default_factory=dict, description="Scheduling configuration")
    content_templates: List[Dict[str, Any]] = Field(default_factory=list, description="Content templates")
    engagement_rules: Dict[str, Any] = Field(default_factory=dict, description="Engagement rules")


class PostContentRequest(BaseModel):
    content: str = Field(..., description="Content to post")
    platforms: List[str] = Field(default_factory=list, description="Platforms to post to")
    scheduled_at: Optional[datetime] = Field(None, description="When to post")
    campaign_id: Optional[int] = Field(None, description="Associated campaign")


class EngagementRequest(BaseModel):
    platform: str = Field(..., description="Platform for engagement")
    target_type: str = Field(..., description="Type of engagement target")
    target_id: str = Field(..., description="Target ID to engage with")
    engagement_type: str = Field(..., description="Type of engagement (like, comment, follow)")
    comment_text: Optional[str] = Field(None, description="Comment text if applicable")


# Dependencies
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Get current authenticated user"""
    # For now, return a mock user - in production this would validate JWT tokens
    # TODO: Implement proper JWT authentication
    user_id = getattr(request.state, 'user_id', 1)  # Default to user ID 1 for development

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/auth/{platform}/url")
async def get_oauth_url(platform: str, user_id: int = Query(1, description="User ID")):
    """Get OAuth authorization URL for a platform"""
    try:
        if platform == "twitter":
            # For development/demo purposes, return a mock OAuth URL if credentials are not configured
            try:
                oauth_service = TwitterOAuthService()
                auth_url, code_verifier, state = oauth_service.get_authorization_url()
            except ValueError as e:
                # Twitter credentials not configured - return demo URL
                import secrets
                code_verifier = secrets.token_urlsafe(32)[:43]
                state = secrets.token_urlsafe(16)

                # Return a demo URL that shows the OAuth flow would work
                auth_url = f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id=demo&redirect_uri=http://localhost:3000/auth/twitter/callback&scope=tweet.read%20tweet.write%20users.read%20offline.access&state={state}&code_challenge=demo&code_challenge_method=S256"

                return {
                    "auth_url": auth_url,
                    "code_verifier": code_verifier,
                    "state": state,
                    "platform": platform,
                    "demo_mode": True,
                    "message": "Twitter API credentials not configured. This is a demo OAuth URL."
                }

            return {
                "auth_url": auth_url,
                "code_verifier": code_verifier,
                "state": state,
                "platform": platform,
                "demo_mode": False
            }
        else:
            raise HTTPException(status_code=400, detail=f"Platform '{platform}' not supported yet")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")


@router.post("/accounts/connect")
async def connect_account(
    request: ConnectAccountRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect a social media account using OAuth code"""
    try:
        if request.platform == "twitter":
            # Exchange code for tokens
            oauth_service = TwitterOAuthService()
            token_data = oauth_service.exchange_code_for_tokens(
                request.authorization_code,
                request.code_verifier
            )

            # Get account info using access token
            twitter_service = get_twitter_service(token_data['access_token'])
            account_info = twitter_service.get_account_info()

            # Encrypt sensitive tokens
            encrypted_access_token = encrypt_data(token_data['access_token'])
            encrypted_refresh_token = encrypt_data(token_data.get('refresh_token', ''))

            # Create or update social account
            existing_account = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user.id,
                    SocialAccount.platform == request.platform,
                    SocialAccount.account_id == account_info['account_id']
                )
            )
            existing_account = existing_account.scalar_one_or_none()

            if existing_account:
                # Update existing account
                existing_account.access_token = encrypted_access_token
                existing_account.refresh_token = encrypted_refresh_token
                existing_account.token_expires_at = token_data.get('expires_at')
                existing_account.account_username = account_info['username']
                existing_account.account_name = account_info['name']
                existing_account.profile_url = account_info['profile_url']
                existing_account.avatar_url = account_info['avatar_url']
                existing_account.follower_count = account_info['follower_count']
                existing_account.following_count = account_info['following_count']
                existing_account.is_active = True
                existing_account.last_synced_at = datetime.utcnow()
                account = existing_account
            else:
                # Create new account
                account = SocialAccount(
                    user_id=user.id,
                    platform=request.platform,
                    account_id=account_info['account_id'],
                    account_username=account_info['username'],
                    account_name=account_info['name'],
                    profile_url=account_info['profile_url'],
                    avatar_url=account_info['avatar_url'],
                    access_token=encrypted_access_token,
                    refresh_token=encrypted_refresh_token,
                    token_expires_at=token_data.get('expires_at'),
                    follower_count=account_info['follower_count'],
                    following_count=account_info['following_count'],
                    is_active=True,
                    last_synced_at=datetime.utcnow()
                )
                db.add(account)

            await db.commit()
            await db.refresh(account)

            return {
                "success": True,
                "account": {
                    "id": account.id,
                    "platform": account.platform,
                    "username": account.account_username,
                    "name": account.account_name,
                    "profile_url": account.profile_url,
                    "avatar_url": account.avatar_url,
                    "follower_count": account.follower_count,
                    "is_active": account.is_active
                }
            }

        else:
            raise HTTPException(status_code=400, detail=f"Platform '{request.platform}' not supported yet")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to connect account: {str(e)}")


@router.get("/accounts")
async def get_connected_accounts():
    """Get all connected social accounts for the user"""
    # This would be implemented with proper database queries
    # For now, return mock data (removed auth for development)
    return {
        "accounts": [
            {
                "id": 1,
                "platform": "twitter",
                "username": "@unitasaAI",
                "name": "Unitasa AI",
                "profile_url": "https://twitter.com/unitasaAI",
                "avatar_url": "https://example.com/avatar.jpg",
                "follower_count": 1250,
                "is_active": True,
                "last_synced_at": datetime.utcnow().isoformat()
            }
        ]
    }


@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect a social account"""
    # Implementation would revoke tokens and delete account record
    return {"success": True, "message": "Account disconnected"}


@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new social media campaign"""
    try:
        # For now, create a basic campaign - this would be expanded
        campaign = Campaign(
            user_id=user.id,
            name=request.name,
            description=request.description,
            platforms=request.platforms,
            schedule_config=request.schedule_config,
            content_templates=request.content_templates,
            engagement_rules=request.engagement_rules,
            status="draft"
        )

        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "status": campaign.status,
                "platforms": campaign.platforms,
                "created_at": campaign.created_at.isoformat()
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")


@router.get("/campaigns")
async def get_campaigns():
    """Get all campaigns for the user"""
    # Mock data for now (removed auth for development)
    return {
        "campaigns": [
            {
                "id": 1,
                "name": "B2B Marketing Automation",
                "status": "active",
                "platforms": ["twitter"],
                "total_posts": 45,
                "total_engagements": 234,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }


@router.post("/posts")
async def create_post(
    request: PostContentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create and schedule a social media post"""
    try:
        # For now, handle Twitter posting
        if "twitter" in request.platforms:
            # Get user's Twitter account
            twitter_account = await db.execute(
                select(SocialAccount).where(
                    SocialAccount.user_id == user.id,
                    SocialAccount.platform == "twitter",
                    SocialAccount.is_active == True
                )
            )
            twitter_account = twitter_account.scalar_one_or_none()

            if not twitter_account:
                raise HTTPException(status_code=400, detail="No active Twitter account connected")

            # Decrypt access token
            access_token = decrypt_data(twitter_account.access_token)

            # Post to Twitter
            twitter_service = get_twitter_service(access_token)
            result = twitter_service.post_content(request.content)

            if result['success']:
                # Save post record
                post = SocialPost(
                    user_id=user.id,
                    social_account_id=twitter_account.id,
                    campaign_id=request.campaign_id,
                    platform="twitter",
                    platform_post_id=result['post_id'],
                    post_url=result['url'],
                    content=request.content,
                    status="posted",
                    posted_at=datetime.utcnow()
                )
                db.add(post)
                await db.commit()

                return {
                    "success": True,
                    "post": {
                        "id": post.id,
                        "platform": post.platform,
                        "url": post.post_url,
                        "status": post.status,
                        "posted_at": post.posted_at.isoformat()
                    }
                }
            else:
                raise HTTPException(status_code=500, detail=f"Failed to post: {result.get('error', 'Unknown error')}")

        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.post("/engagement")
async def perform_engagement(
    request: EngagementRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform engagement action on social media"""
    try:
        # Get the social account
        account = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user.id,
                SocialAccount.platform == request.platform,
                SocialAccount.is_active == True
            )
        )
        account = account.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=400, detail=f"No active {request.platform} account connected")

        # For Twitter engagement
        if request.platform == "twitter":
            access_token = decrypt_data(account.access_token)
            twitter_service = get_twitter_service(access_token)

            # Perform the engagement
            result = twitter_service.perform_engagement(
                target={'tweet_id': request.target_id, 'author_id': 'target_author'},
                engagement_type=request.engagement_type,
                custom_comment=request.comment_text
            )

            if result['success']:
                # Save engagement record
                engagement = Engagement(
                    user_id=user.id,
                    social_account_id=account.id,
                    platform=request.platform,
                    engagement_type=request.engagement_type,
                    target_post_id=request.target_id,
                    comment_text=request.comment_text,
                    status="completed"
                )
                db.add(engagement)
                await db.commit()

                return {"success": True, "engagement": result}
            else:
                raise HTTPException(status_code=500, detail=f"Engagement failed: {result.get('error')}")

        else:
            raise HTTPException(status_code=400, detail="Platform not supported for engagement")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Engagement failed: {str(e)}")


@router.get("/analytics")
async def get_analytics(
    platform: Optional[str] = None,
    days: int = 7
):
    """Get social media analytics"""
    # Mock analytics data for now (removed auth for development)
    return {
        "summary": {
            "total_posts": 45,
            "total_engagements": 234,
            "total_followers_gained": 89,
            "engagement_rate": 5.2
        },
        "platform_breakdown": {
            "twitter": {
                "posts": 45,
                "engagements": 234,
                "followers_gained": 89,
                "engagement_rate": 5.2
            }
        },
        "performance_trend": [
            {"date": "2024-01-01", "posts": 5, "engagements": 25},
            {"date": "2024-01-02", "posts": 7, "engagements": 35},
            # ... more data points
        ]
    }