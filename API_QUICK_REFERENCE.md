# API Quick Reference - Advertising System

## 🚀 Quick Start

**Base URL**: `http://localhost:8000/api/v1/`

## 🔐 Authentication

```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

## 📊 Most Used Endpoints

### 1. Get All Active Campaigns
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=active" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Get Campaign Details
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Create New Campaign
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Campaign",
    "company_name": "My Company",
    "status": "draft",
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "daily_budget": "100.00",
    "total_budget": "3000.00"
  }'
```

### 4. Update Campaign Status
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### 5. Request Mobile Ad (No Auth Required)
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.example.myapp",
    "os": "android",
    "device_type": "phone",
    "ad_types": ["banner"]
  }'
```

### 6. Get Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🎯 Campaign Management Quick Commands

### List all campaigns
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Filter campaigns by status
```bash
# Available statuses: draft, active, paused, completed, archived
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=active" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Pause a campaign
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

## 🎨 Creative Management

### List creatives for a campaign
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create creative with image upload
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "name=Banner Creative" \
  -F "type=banner" \
  -F "title=Great Product!" \
  -F "call_to_action=Buy Now" \
  -F "destination_url=https://example.com" \
  -F "image=@banner.jpg"
```

## 🎯 Targeting

### Create targeting rules
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/targets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "os_android": true,
    "os_ios": true,
    "gender": "all",
    "age_min": 18,
    "age_max": 65,
    "countries": ["US", "CA"],
    "interests": ["technology", "gaming"]
  }'
```

## 📱 Mobile Ad Serving

### Request banner ad
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.example.app",
    "app_version": "1.0.0",
    "os": "android",
    "os_version": "12.0",
    "device_type": "phone",
    "ad_types": ["banner"],
    "limit": 1
  }'
```

### Log ad click
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/{ad_id}/click/ \
  -H "Content-Type: application/json"
```

## 📊 Analytics & Reports

### Get campaign analytics
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/campaigns/{campaign_id}/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get analytics with date range
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/?start_date=2025-05-01&end_date=2025-05-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🏢 Placement Management

### List available placements
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/placements/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create new placement
```bash
curl -X POST http://localhost:8000/api/v1/advertising/placements/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile Banner Bottom",
    "code": "mobile_banner_bottom",
    "description": "Bottom banner for mobile apps",
    "recommended_width": 320,
    "recommended_height": 50
  }'
```

## 🛠️ Common Query Parameters

### Pagination
- `?page=2&page_size=20` - Get page 2 with 20 items

### Filtering Campaigns
- `?status=active` - Only active campaigns
- `?status=draft` - Only draft campaigns
- `?status=paused` - Only paused campaigns

### Date Filtering (Analytics)
- `?start_date=2025-05-01` - From specific date
- `?end_date=2025-05-31` - Until specific date

## ⚡ Testing Your Setup

### 1. Check if the API is running
```bash
curl -X GET http://localhost:8000/api/v1/advertising/placements/
```

### 2. Test authentication
```bash
# This should return 401 Unauthorized
curl -X GET http://localhost:8000/api/v1/advertising/campaigns/
```

### 3. Test mobile ad serving (should work without auth)
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "test.app",
    "os": "android",
    "device_type": "phone"
  }'
```

## 🚨 Common Error Codes

- `401` - Missing or invalid authentication token
- `403` - Insufficient permissions
- `404` - Campaign/resource not found
- `400` - Invalid request data
- `422` - Validation errors

## 💡 Pro Tips

1. **Save your token**: Store the access token after login for subsequent requests
2. **Use jq for JSON parsing**: `| jq '.'` for pretty-printing responses
3. **Check campaign is_active**: The `is_active` field shows real-time campaign status
4. **Monitor daily budgets**: Check spending before serving ads
5. **Use pagination**: Large datasets are paginated (default: 10 items per page)

---

For detailed documentation, see `API_DOCUMENTATION.md` 