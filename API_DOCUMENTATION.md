# Advertising System API Documentation

## Overview

This is a comprehensive REST API for an advertising system built with Django REST Framework. The system manages advertising campaigns, creatives, targeting, placements, and provides analytics.

**Base URL**: `http://localhost:8000/api/v1/`

## Table of Contents

1. [Authentication](#authentication)
2. [Campaign Management](#campaign-management)
3. [Creative Management](#creative-management)
4. [Targeting Management](#targeting-management)
5. [Placement Management](#placement-management)
6. [Mobile Ad Serving](#mobile-ad-serving)
7. [Analytics](#analytics)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Get Access Token

**Endpoint**: `POST /token/`

**Description**: Obtain JWT access token for authentication.

**Request Body**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### Refresh Token

**Endpoint**: `POST /token/refresh/`

**Description**: Refresh expired access token.

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Campaign Management

All campaign endpoints require authentication. Regular users can only access their own campaigns, while admin users can access all campaigns.

### List Campaigns

**Endpoint**: `GET /advertising/campaigns/`

**Description**: Retrieve a paginated list of campaigns.

**Query Parameters**:
- `page` (integer): Page number
- `page_size` (integer): Number of items per page (max 100)
- `status` (string): Filter by campaign status (`draft`, `active`, `paused`, `completed`, `archived`)

**Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Response**:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/advertising/campaigns/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Summer Sale Campaign",
      "company_name": "TechCorp Inc.",
      "status": "active",
      "start_date": "2025-05-26T10:00:00Z",
      "end_date": "2025-06-30T23:59:59Z",
      "daily_budget": "500.00",
      "total_budget": "15000.00",
      "budget_exceeded_action": "pause_day",
      "created_at": "2025-05-26T09:00:00Z",
      "is_active": true
    }
  ]
}
```

**Example**:
```bash
# Get all active campaigns
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=active" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get campaigns with pagination
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Campaign Details

**Endpoint**: `GET /advertising/campaigns/{campaign_id}/`

**Description**: Retrieve detailed information about a specific campaign including creatives and targets.

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Summer Sale Campaign",
  "company_name": "TechCorp Inc.",
  "advertiser": 1,
  "status": "active",
  "start_date": "2025-05-26T10:00:00Z",
  "end_date": "2025-06-30T23:59:59Z",
  "daily_budget": "500.00",
  "total_budget": "15000.00",
  "budget_exceeded_action": "pause_day",
  "budget_exceeded_frequency_cap": 1,
  "opportunity_sampling_rate": 5.0,
  "description": "Summer promotional campaign for mobile apps",
  "created_at": "2025-05-26T09:00:00Z",
  "updated_at": "2025-05-26T09:00:00Z",
  "is_active": true,
  "targets": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "os_android": true,
      "os_ios": true,
      "os_version_min": "",
      "os_version_max": "",
      "gender": "all",
      "age_min": 18,
      "age_max": 65,
      "countries": ["US", "CA", "GB"],
      "regions": [],
      "cities": [],
      "interests": ["technology", "gaming"],
      "created_at": "2025-05-26T09:00:00Z",
      "updated_at": "2025-05-26T09:00:00Z"
    }
  ],
  "creatives": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "Banner Creative 1",
      "type": "banner",
      "placement": "880e8400-e29b-41d4-a716-446655440003",
      "placement_details": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "name": "Mobile Banner Top",
        "code": "mobile_banner_top",
        "description": "Top banner placement for mobile apps",
        "recommended_width": 320,
        "recommended_height": 50,
        "is_active": true,
        "created_at": "2025-05-26T09:00:00Z",
        "updated_at": "2025-05-26T09:00:00Z"
      },
      "title": "Save 50% This Summer!",
      "description": "Limited time offer on all products",
      "image": "/media/ad_creatives/summer_banner.jpg",
      "video": null,
      "call_to_action": "Shop Now",
      "destination_url": "https://example.com/summer-sale",
      "width": 320,
      "height": 50,
      "is_active": true,
      "created_at": "2025-05-26T09:00:00Z",
      "updated_at": "2025-05-26T09:00:00Z"
    }
  ]
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Campaign

**Endpoint**: `POST /advertising/campaigns/`

**Description**: Create a new advertising campaign.

**Request Body**:
```json
{
  "name": "Winter Holiday Campaign",
  "company_name": "RetailCorp",
  "status": "draft",
  "start_date": "2025-12-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "daily_budget": "1000.00",
  "total_budget": "31000.00",
  "budget_exceeded_action": "pause_day",
  "budget_exceeded_frequency_cap": 1,
  "opportunity_sampling_rate": 10.0,
  "description": "Holiday promotional campaign"
}
```

**Response**: Returns the created campaign object (same format as GET).

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Winter Holiday Campaign",
    "company_name": "RetailCorp",
    "status": "draft",
    "start_date": "2025-12-01T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "daily_budget": "1000.00",
    "total_budget": "31000.00",
    "description": "Holiday promotional campaign"
  }'
```

### Update Campaign

**Endpoint**: `PUT /advertising/campaigns/{campaign_id}/`

**Description**: Update an existing campaign.

**Request Body**: Same as create campaign.

**Example**:
```bash
curl -X PUT http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Campaign Name",
    "status": "active"
  }'
```

### Partial Update Campaign

**Endpoint**: `PATCH /advertising/campaigns/{campaign_id}/`

**Description**: Partially update campaign fields.

**Example**:
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "paused"
  }'
```

### Delete Campaign

**Endpoint**: `DELETE /advertising/campaigns/{campaign_id}/`

**Description**: Delete a campaign.

**Response**: `204 No Content`

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Creative Management

Creatives are associated with campaigns and define the actual ad content.

### List Creatives for Campaign

**Endpoint**: `GET /advertising/campaigns/{campaign_id}/creatives/`

**Description**: List all creatives for a specific campaign.

**Response**:
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Banner Creative 1",
    "type": "banner",
    "placement": "880e8400-e29b-41d4-a716-446655440003",
    "placement_details": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "name": "Mobile Banner Top",
      "code": "mobile_banner_top",
      "description": "Top banner placement for mobile apps",
      "recommended_width": 320,
      "recommended_height": 50,
      "is_active": true,
      "created_at": "2025-05-26T09:00:00Z",
      "updated_at": "2025-05-26T09:00:00Z"
    },
    "title": "Save 50% This Summer!",
    "description": "Limited time offer on all products",
    "image": "/media/ad_creatives/summer_banner.jpg",
    "video": null,
    "call_to_action": "Shop Now",
    "destination_url": "https://example.com/summer-sale",
    "width": 320,
    "height": 50,
    "is_active": true,
    "created_at": "2025-05-26T09:00:00Z",
    "updated_at": "2025-05-26T09:00:00Z"
  }
]
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/creatives/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Creative

**Endpoint**: `POST /advertising/campaigns/{campaign_id}/creatives/`

**Description**: Create a new creative for a campaign.

**Request Body** (multipart/form-data for file uploads):
```json
{
  "name": "New Banner Creative",
  "type": "banner",
  "placement": "880e8400-e29b-41d4-a716-446655440003",
  "title": "Amazing Product!",
  "description": "Check out our latest product",
  "call_to_action": "Learn More",
  "destination_url": "https://example.com/product",
  "width": 320,
  "height": 50,
  "is_active": true
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/creatives/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "name=New Banner Creative" \
  -F "type=banner" \
  -F "title=Amazing Product!" \
  -F "call_to_action=Learn More" \
  -F "destination_url=https://example.com/product" \
  -F "image=@/path/to/banner.jpg"
```

### Get Creative Details

**Endpoint**: `GET /advertising/campaigns/{campaign_id}/creatives/{creative_id}/`

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/creatives/770e8400-e29b-41d4-a716-446655440002/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update Creative

**Endpoint**: `PUT /advertising/campaigns/{campaign_id}/creatives/{creative_id}/`

### Delete Creative

**Endpoint**: `DELETE /advertising/campaigns/{campaign_id}/creatives/{creative_id}/`

---

## Targeting Management

Targeting defines the audience criteria for campaigns.

### List Targets for Campaign

**Endpoint**: `GET /advertising/campaigns/{campaign_id}/targets/`

**Response**:
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "os_android": true,
    "os_ios": true,
    "os_version_min": "10.0",
    "os_version_max": "",
    "gender": "all",
    "age_min": 18,
    "age_max": 65,
    "countries": ["US", "CA", "GB"],
    "regions": ["California", "Ontario"],
    "cities": ["San Francisco", "Toronto"],
    "interests": ["technology", "gaming", "sports"],
    "created_at": "2025-05-26T09:00:00Z",
    "updated_at": "2025-05-26T09:00:00Z"
  }
]
```

### Create Target

**Endpoint**: `POST /advertising/campaigns/{campaign_id}/targets/`

**Request Body**:
```json
{
  "os_android": true,
  "os_ios": false,
  "os_version_min": "8.0",
  "gender": "male",
  "age_min": 25,
  "age_max": 45,
  "countries": ["US"],
  "interests": ["technology", "business"]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/550e8400-e29b-41d4-a716-446655440000/targets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "os_android": true,
    "os_ios": false,
    "gender": "male",
    "age_min": 25,
    "age_max": 45,
    "countries": ["US"],
    "interests": ["technology"]
  }'
```

---

## Placement Management

Placements define where ads can be displayed.

### List Placements

**Endpoint**: `GET /advertising/placements/`

**Response**:
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "name": "Mobile Banner Top",
    "code": "mobile_banner_top",
    "description": "Top banner placement for mobile apps",
    "recommended_width": 320,
    "recommended_height": 50,
    "is_active": true,
    "created_at": "2025-05-26T09:00:00Z",
    "updated_at": "2025-05-26T09:00:00Z"
  }
]
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/placements/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Placement

**Endpoint**: `POST /advertising/placements/`

**Request Body**:
```json
{
  "name": "Mobile Interstitial",
  "code": "mobile_interstitial",
  "description": "Full-screen interstitial ad",
  "recommended_width": 320,
  "recommended_height": 480,
  "is_active": true
}
```

---

## Mobile Ad Serving

Public endpoints for serving ads to mobile applications.

### Request Ads

**Endpoint**: `POST /advertising/mobile/ads/`

**Description**: Request ads for mobile app placement. No authentication required.

**Request Body**:
```json
{
  "app_id": "com.example.myapp",
  "app_version": "1.2.3",
  "os": "android",
  "os_version": "12.0",
  "device_type": "phone",
  "width": 320,
  "height": 50,
  "country": "US",
  "region": "California",
  "city": "San Francisco",
  "gender": "male",
  "age": 30,
  "interests": ["technology", "gaming"],
  "ad_types": ["banner", "interstitial"],
  "limit": 1
}
```

**Response**:
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
    "ad_type": "banner",
    "title": "Save 50% This Summer!",
    "description": "Limited time offer on all products",
    "image_url": "http://localhost:8000/media/ad_creatives/summer_banner.jpg",
    "video_url": null,
    "cta": "Shop Now",
    "action_url": "https://example.com/summer-sale",
    "width": 320,
    "height": 50,
    "placement_code": "mobile_banner_top"
  }
]
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.example.myapp",
    "app_version": "1.2.3",
    "os": "android",
    "os_version": "12.0",
    "device_type": "phone",
    "ad_types": ["banner"],
    "limit": 1
  }'
```

### Log Ad Click

**Endpoint**: `POST /advertising/mobile/ads/{ad_id}/click/`

**Description**: Log when a user clicks on an ad. No authentication required.

**Response**:
```json
{
  "success": true,
  "message": "Click logged successfully"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/770e8400-e29b-41d4-a716-446655440002/click/ \
  -H "Content-Type: application/json"
```

---

## Analytics

Analytics endpoints for campaign performance data.

### Get Overall Analytics

**Endpoint**: `GET /advertising/analytics/`

**Description**: Get overall analytics for all user's campaigns.

**Query Parameters**:
- `start_date` (string): Start date in ISO format (YYYY-MM-DD)
- `end_date` (string): End date in ISO format (YYYY-MM-DD)

**Response**:
```json
{
  "total_campaigns": 5,
  "active_campaigns": 3,
  "total_impressions": 125000,
  "total_clicks": 2500,
  "total_spending": "5250.00",
  "average_ctr": 2.0,
  "campaigns": [
    {
      "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
      "campaign_name": "Summer Sale Campaign",
      "impressions": 50000,
      "clicks": 1000,
      "spending": "2500.00",
      "ctr": 2.0
    }
  ]
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/?start_date=2025-05-01&end_date=2025-05-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Campaign-Specific Analytics

**Endpoint**: `GET /advertising/analytics/campaigns/{campaign_id}/`

**Description**: Get detailed analytics for a specific campaign.

**Response**:
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "campaign_name": "Summer Sale Campaign",
  "status": "active",
  "impressions": 50000,
  "clicks": 1000,
  "spending": "2500.00",
  "ctr": 2.0,
  "daily_stats": [
    {
      "date": "2025-05-26",
      "impressions": 2000,
      "clicks": 40,
      "spending": "100.00",
      "ctr": 2.0
    }
  ]
}
```

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/campaigns/550e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format.

### Error Response Format

```json
{
  "detail": "Error message",
  "code": "error_code",
  "field_errors": {
    "field_name": ["Field-specific error message"]
  }
}
```

### Common Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Example Error Responses

**Authentication Error**:
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Validation Error**:
```json
{
  "name": ["This field is required."],
  "daily_budget": ["Ensure this value is greater than or equal to 0."]
}
```

---

## Rate Limiting

The API includes built-in rate limiting:

- **Authenticated requests**: 1000 requests per hour
- **Anonymous requests** (mobile ad serving): 10000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

---

## Campaign Status and Budget Management

### Campaign Status Values

- `draft` - Campaign is being prepared
- `active` - Campaign is running
- `paused` - Campaign is temporarily stopped
- `completed` - Campaign has finished
- `archived` - Campaign is archived

### Budget Exceeded Actions

When daily budget is exceeded, the system can take different actions:

- `pause_day` - Pause serving ads for the rest of the day
- `pause_campaign` - Pause the entire campaign
- `continue_limited` - Continue with reduced frequency
- `stop_immediately` - Stop serving ads immediately
- `email_notify` - Send notification but continue serving

### Key Properties

- `is_active` - Automatically calculated based on status, dates, and budget
- `impressions_today` - Number of impressions served today
- `display_rate_today` - Percentage of opportunities where ads were shown

---

## Best Practices

1. **Always include authentication headers** for protected endpoints
2. **Use HTTPS in production** to secure API communications
3. **Handle rate limiting** by checking response headers
4. **Cache responses** when appropriate to reduce API calls
5. **Use proper HTTP methods** (GET for reading, POST for creating, etc.)
6. **Validate data** before sending requests
7. **Handle errors gracefully** with appropriate user feedback

---

## SDK and Integration Examples

### Python Example

```python
import requests

class AdvertisingAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_active_campaigns(self):
        response = requests.get(
            f"{self.base_url}/advertising/campaigns/?status=active",
            headers=self.headers
        )
        return response.json()
    
    def request_mobile_ad(self, app_id, os, device_type):
        data = {
            "app_id": app_id,
            "os": os,
            "device_type": device_type,
            "ad_types": ["banner"]
        }
        response = requests.post(
            f"{self.base_url}/advertising/mobile/ads/",
            json=data
        )
        return response.json()
```

### JavaScript Example

```javascript
class AdvertisingAPI {
    constructor(baseUrl, accessToken) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getActiveCampaigns() {
        const response = await fetch(`${this.baseUrl}/advertising/campaigns/?status=active`, {
            headers: this.headers
        });
        return response.json();
    }
    
    async requestMobileAd(appId, os, deviceType) {
        const response = await fetch(`${this.baseUrl}/advertising/mobile/ads/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                app_id: appId,
                os: os,
                device_type: deviceType,
                ad_types: ['banner']
            })
        });
        return response.json();
    }
}
```

---

For more information or support, please refer to the project repository or contact the development team. 