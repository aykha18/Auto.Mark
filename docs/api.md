# API Documentation

## Overview

The AI Marketing Agents API provides RESTful endpoints for event tracking, user management, content generation, campaign management, and analytics. All endpoints require API key authentication and support JSON request/response formats.

## Authentication

All API requests must include the `X-API-Key` header with a valid API key.

```bash
curl -H "X-API-Key: your_api_key" https://api.marketing-agents.com/api/v1/events/track
```

## Rate Limiting

- **Free Tier**: 1,000 requests/day
- **Pro Tier**: 100,000 requests/day
- **Enterprise**: Unlimited

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

## Error Handling

All errors return appropriate HTTP status codes with JSON error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "user_id",
      "reason": "Required field missing"
    }
  }
}
```

### Error Codes

- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Invalid API key
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service temporarily unavailable

## Event Tracking API

### Track Event

Record user behavior events for personalization and analytics.

```http
POST /api/v1/events/track
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "user_id": "string (required)",
  "event": "string (required)",
  "properties": {
    "additionalProp1": "string",
    "additionalProp2": "number",
    "additionalProp3": "boolean"
  },
  "timestamp": "2024-01-01T00:00:00Z (optional)",
  "session_id": "string (optional)"
}
```

**Response (201):**
```json
{
  "event_id": "uuid",
  "status": "tracked",
  "processed_at": "2024-01-01T00:00:00Z"
}
```

**Example:**
```bash
curl -X POST https://api.marketing-agents.com/api/v1/events/track \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "user_id": "user_123",
    "event": "product_viewed",
    "properties": {
      "product_id": "prod_456",
      "category": "electronics",
      "price": 299.99
    }
  }'
```

### Batch Track Events

Track multiple events in a single request for better performance.

```http
POST /api/v1/events/batch
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "events": [
    {
      "user_id": "string",
      "event": "string",
      "properties": {},
      "timestamp": "2024-01-01T00:00:00Z (optional)"
    }
  ]
}
```

**Response (201):**
```json
{
  "events_tracked": 10,
  "status": "batch_processed",
  "processed_at": "2024-01-01T00:00:00Z"
}
```

## User Management API

### Identify User

Create or update user profiles with traits for segmentation and personalization.

```http
POST /api/v1/users/identify
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "user_id": "string (required)",
  "traits": {
    "email": "string",
    "name": "string",
    "company": "string",
    "job_title": "string",
    "industry": "string",
    "company_size": "string",
    "plan": "string",
    "signup_date": "2024-01-01T00:00:00Z"
  },
  "timestamp": "2024-01-01T00:00:00Z (optional)"
}
```

**Response (200):**
```json
{
  "user_id": "string",
  "status": "identified",
  "segment": "enterprise",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get User Profile

Retrieve user profile and behavioral data.

```http
GET /api/v1/users/{user_id}
X-API-Key: your_api_key
```

**Response (200):**
```json
{
  "user_id": "string",
  "traits": {},
  "segment": "string",
  "last_seen": "2024-01-01T00:00:00Z",
  "event_count": 150,
  "ltv_prediction": 2500.00,
  "churn_risk": 0.15,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Content Generation API

### Generate Content

Create marketing content using AI agents with RAG-enhanced context.

```http
POST /api/v1/content/generate
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "type": "blog_post | social_media | email | ad_copy | landing_page (required)",
  "topic": "string (required)",
  "audience": "string (optional)",
  "tone": "professional | casual | persuasive | educational (optional)",
  "length": "short | medium | long (optional)",
  "keywords": ["string"] (optional),
  "brand_guidelines": {
    "voice": "string",
    "avoid_words": ["string"],
    "required_phrases": ["string"]
  } (optional)
}
```

**Response (200):**
```json
{
  "content_id": "uuid",
  "type": "blog_post",
  "title": "10 AI Marketing Trends for 2024",
  "content": "Full content here...",
  "metadata": {
    "word_count": 1200,
    "reading_time": 6,
    "seo_score": 85,
    "keywords_used": ["AI", "marketing", "automation"],
    "generated_by": "content_creator_agent",
    "generation_time": 2.3
  },
  "variants": [
    {
      "variant_id": "uuid",
      "title": "Alternative title...",
      "content": "Alternative content...",
      "metadata": {}
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Content Variants

Generate multiple variations of content for A/B testing.

```http
POST /api/v1/content/variants
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "content_id": "uuid (required)",
  "count": 3,
  "variations": {
    "tone": ["professional", "casual"],
    "length": ["short", "medium"],
    "focus": ["benefits", "features"]
  }
}
```

## Campaign Management API

### Create Campaign

Launch automated marketing campaigns across multiple channels.

```http
POST /api/v1/campaigns/create
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "name": "Q4 Lead Generation Campaign (required)",
  "type": "lead_gen | content | retention | ad (required)",
  "budget": 5000.00,
  "target_audience": {
    "industry": ["technology", "finance"],
    "company_size": "50-200",
    "job_titles": ["CTO", "VP Engineering", "Director"],
    "location": ["United States", "Canada"],
    "behavioral_signals": {
      "visited_pricing": true,
      "downloaded_whitepaper": true,
      "time_on_site": ">300"
    }
  },
  "channels": ["google_ads", "linkedin", "content"],
  "goals": {
    "leads": 100,
    "conversions": 20,
    "cost_per_lead": 50.00
  },
  "schedule": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "daily_budget": 150.00
  },
  "content_strategy": {
    "themes": ["AI automation", "ROI improvement"],
    "content_types": ["blog", "social", "email"],
    "brand_voice": "professional"
  }
}
```

**Response (201):**
```json
{
  "campaign_id": "uuid",
  "name": "Q4 Lead Generation Campaign",
  "status": "created",
  "agents_assigned": ["lead_gen", "content_creator", "ad_manager"],
  "estimated_completion": "2024-01-02T10:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Campaign Status

Monitor campaign performance and agent activity.

```http
GET /api/v1/campaigns/{campaign_id}
X-API-Key: your_api_key
```

**Response (200):**
```json
{
  "campaign_id": "uuid",
  "name": "Q4 Lead Generation Campaign",
  "status": "active",
  "progress": {
    "leads_generated": 45,
    "content_created": 12,
    "ads_launched": 8,
    "conversions": 5
  },
  "performance": {
    "budget_spent": 2250.00,
    "budget_remaining": 2750.00,
    "cost_per_lead": 50.00,
    "conversion_rate": 11.1,
    "roi": 2.8
  },
  "agent_activity": [
    {
      "agent": "lead_gen",
      "status": "active",
      "last_action": "Generated 15 leads from LinkedIn",
      "next_action": "Qualify leads with email outreach"
    },
    {
      "agent": "content_creator",
      "status": "idle",
      "last_action": "Created blog post: 'AI Marketing Trends'",
      "next_action": "Generate social media posts"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Pause Campaign

Temporarily stop campaign execution.

```http
POST /api/v1/campaigns/{campaign_id}/pause
X-API-Key: your_api_key
```

### Resume Campaign

Restart a paused campaign.

```http
POST /api/v1/campaigns/{campaign_id}/resume
X-API-Key: your_api_key
```

### Stop Campaign

Permanently end campaign execution.

```http
POST /api/v1/campaigns/{campaign_id}/stop
X-API-Key: your_api_key
```

## Personalization API

### Get Recommendations

Retrieve personalized content and product recommendations.

```http
GET /api/v1/recommendations/{user_id}?context=homepage&limit=5
X-API-Key: your_api_key
```

**Query Parameters:**
- `context`: homepage | product_page | checkout | email
- `limit`: Number of recommendations (default: 5)
- `content_types`: blog | product | offer (comma-separated)

**Response (200):**
```json
{
  "user_id": "string",
  "context": "homepage",
  "recommendations": [
    {
      "type": "content",
      "id": "uuid",
      "title": "AI Marketing Automation Guide",
      "url": "/blog/ai-marketing-automation",
      "relevance_score": 0.95,
      "reason": "Based on recent product page visits"
    },
    {
      "type": "product",
      "id": "uuid",
      "name": "Advanced Analytics Add-on",
      "price": 99.00,
      "relevance_score": 0.87,
      "reason": "Complements current plan features"
    }
  ],
  "segment": "enterprise",
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### Get Personalized Content

Generate content tailored to user behavior and preferences.

```http
POST /api/v1/content/personalize
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "user_id": "string (required)",
  "content_type": "email | landing_page | recommendation",
  "context": "welcome | reengagement | upsell",
  "constraints": {
    "max_length": 500,
    "include_elements": ["cta_button", "social_proof"],
    "avoid_topics": ["pricing"]
  }
}
```

## Analytics API

### Get Dashboard Metrics

Retrieve real-time marketing metrics and KPIs.

```http
GET /api/v1/analytics/dashboard?period=30d&segment=all
X-API-Key: your_api_key
```

**Query Parameters:**
- `period`: 7d | 30d | 90d | 1y
- `segment`: all | enterprise | startup | individual

**Response (200):**
```json
{
  "period": "30d",
  "metrics": {
    "users": {
      "total": 15420,
      "active": 8920,
      "new": 1240,
      "churned": 180
    },
    "events": {
      "total": 45680,
      "page_views": 23450,
      "signups": 340,
      "purchases": 125
    },
    "campaigns": {
      "active": 8,
      "total_spent": 12500.00,
      "leads_generated": 450,
      "conversions": 89,
      "roi": 3.2
    },
    "content": {
      "pieces_created": 45,
      "total_views": 12800,
      "avg_engagement": 4.2,
      "conversion_rate": 2.8
    }
  },
  "trends": {
    "user_growth": 12.5,
    "conversion_rate": 8.3,
    "cost_per_lead": -5.2
  },
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### Get Campaign Analytics

Detailed performance metrics for specific campaigns.

```http
GET /api/v1/analytics/campaigns/{campaign_id}?period=30d
X-API-Key: your_api_key
```

### Get Content Analytics

Performance metrics for generated content.

```http
GET /api/v1/analytics/content/{content_id}?period=30d
X-API-Key: your_api_key
```

## Lead Management API

### Get Leads

Retrieve qualified leads generated by AI agents.

```http
GET /api/v1/leads?status=qualified&limit=50&offset=0
X-API-Key: your_api_key
```

**Query Parameters:**
- `status`: new | contacted | qualified | converted
- `score_min`: Minimum lead score (0.0-1.0)
- `source`: google_ads | linkedin | content | referral
- `limit`: Number of leads to return (default: 50)
- `offset`: Pagination offset (default: 0)

**Response (200):**
```json
{
  "leads": [
    {
      "lead_id": "uuid",
      "email": "john@techcorp.com",
      "name": "John Smith",
      "company": "TechCorp Inc.",
      "job_title": "CTO",
      "score": 0.92,
      "status": "qualified",
      "source": "linkedin",
      "properties": {
        "industry": "technology",
        "company_size": "100-500",
        "linkedin_url": "https://linkedin.com/in/johnsmith"
      },
      "qualified_at": "2024-01-01T00:00:00Z",
      "last_contacted": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Update Lead Status

Update lead qualification status and add notes.

```http
PUT /api/v1/leads/{lead_id}
Content-Type: application/json
X-API-Key: your_api_key
```

**Request Body:**
```json
{
  "status": "contacted",
  "notes": "Reached out via email, positive response",
  "next_action": "schedule_demo",
  "next_action_date": "2024-01-05"
}
```

## WebSocket API

### Real-time Updates

Subscribe to real-time campaign updates and agent activity.

```javascript
const ws = new WebSocket('wss://api.marketing-agents.com/ws/realtime?api_key=your_api_key');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};

// Subscribe to campaign updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'campaigns',
  campaign_id: 'uuid'
}));
```

**Message Types:**
- `campaign_update`: Campaign status and performance changes
- `agent_activity`: Agent actions and decisions
- `lead_generated`: New qualified leads
- `content_created`: New content generation completion

## SDK Integration Examples

### Python SDK

```python
from ai_marketing_sdk import MarketingClient

client = MarketingClient(
    api_key="your_api_key",
    base_url="https://api.marketing-agents.com"
)

# Track events
client.track("user_123", "product_viewed", {
    "product_id": "prod_456",
    "category": "electronics"
})

# Identify users
client.identify("user_123", {
    "email": "user@example.com",
    "plan": "pro"
})

# Generate content
content = client.generate_content(
    type="blog_post",
    topic="AI Marketing Trends 2024",
    audience="marketing_professionals"
)

# Create campaign
campaign = client.create_campaign({
    "name": "Q4 Lead Gen",
    "budget": 5000,
    "channels": ["google_ads", "facebook", "linkedin", "producthunt"]
})

# Get recommendations
recommendations = client.get_recommendations("user_123", context="homepage")
```

### JavaScript SDK

```javascript
import { MarketingSDK } from 'ai-marketing-sdk';

const sdk = new MarketingSDK({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.marketing-agents.com'
});

// Track events
sdk.track('user_123', 'button_clicked', {
  button_id: 'signup_cta',
  page: 'landing'
});

// Identify users
sdk.identify('user_123', {
  email: 'user@example.com',
  plan: 'pro'
});

// Generate content
const content = await sdk.generateContent({
  type: 'social_media',
  topic: 'Product launch announcement',
  tone: 'excited'
});

// Real-time updates
sdk.on('campaign_update', (update) => {
  console.log('Campaign update:', update);
});
```

## Rate Limits and Best Practices

### Rate Limiting
- Implement exponential backoff for rate-limited requests
- Use batch endpoints for high-volume event tracking
- Cache frequently accessed data

### Best Practices
- Validate data before sending to reduce error rates
- Use appropriate content types for different contexts
- Monitor API usage and set up alerts for anomalies
- Implement proper error handling and retries

### Optimization Tips
- Batch events when possible (up to 100 events per batch)
- Use WebSocket for real-time features instead of polling
- Compress request payloads for large content generation
- Cache user profiles and recommendations when appropriate