# Wise Sandbox Setup Guide

## Wise Sandbox Requirements

### 1. Account Setup
- Create a Wise Business account
- Apply for API access through Wise Developer Portal
- Get approved for sandbox access

### 2. API Token Requirements
For Wise sandbox, you need:
- **API Token**: Generated from your Wise Business account
- **Profile ID**: Your business profile ID
- **Webhook Secret**: For webhook verification

### 3. Sandbox Environment
- Base URL: `https://api.sandbox.transferwise.tech`
- Different from production: `https://api.wise.com`

### 4. Authentication
Wise uses Bearer token authentication:
```
Authorization: Bearer YOUR_API_TOKEN
```

### 5. Common Issues
1. **Invalid Token Error**: 
   - Token might be expired
   - Token might be for production instead of sandbox
   - Token might not have proper permissions

2. **Profile ID Issues**:
   - Must use the correct business profile ID
   - Personal profile IDs won't work for business operations

### 6. Testing Steps
1. First test: Get profile information
2. Second test: Create a quote
3. Third test: Create a recipient
4. Fourth test: Create a transfer

### 7. Required Permissions
Your API token needs these permissions:
- Read profile information
- Create quotes
- Create recipients
- Create transfers
- Read transfer status

## Next Steps
1. Verify your Wise account has API access enabled
2. Check if your API token is for sandbox environment
3. Confirm your profile ID is correct
4. Test with a simple profile lookup first