# API Quick Reference - NO AUTHENTICATION (TEMPORARY)

## 🚀 Quick Start

**Base URL**: `http://localhost:8000/api/v1/`

## ⚠️ **AUTHENTICATION TEMPORARILY DISABLED**

All endpoints are currently accessible **WITHOUT authentication tokens** for testing purposes.

## 📊 Most Used Endpoints (No Auth Required)

### 1. Get All Active Campaigns
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=active"
```

### 2. Get All Campaigns
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/"
```

### 3. Get Campaign Details
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/"
```

### 4. Create New Campaign
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "company_name": "Test Company",
    "status": "draft",
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "daily_budget": "100.00",
    "total_budget": "3000.00"
  }'
```

### 5. Update Campaign Status
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/ \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### 6. Request Mobile Ad
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

### 7. Get Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/"
```

## 🎯 Campaign Management (No Auth)

### List all campaigns with pagination
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?page=1&page_size=5"
```

### Filter campaigns by status
```bash
# Available statuses: draft, active, paused, completed, archived
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=active"
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/?status=draft"
```

### Update entire campaign
```bash
curl -X PUT http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Campaign Name",
    "company_name": "Updated Company",
    "status": "active",
    "start_date": "2025-06-01T00:00:00Z",
    "end_date": "2025-06-30T23:59:59Z",
    "daily_budget": "200.00",
    "total_budget": "6000.00"
  }'
```

### Delete campaign
```bash
curl -X DELETE http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/
```

## 🎨 Creative Management (No Auth)

### List creatives for a campaign
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/"
```

### Create creative with JSON data
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Banner",
    "type": "banner",
    "title": "Great Product!",
    "description": "Amazing deal",
    "call_to_action": "Buy Now",
    "destination_url": "https://example.com",
    "width": 320,
    "height": 50,
    "is_active": true
  }'
```

### Create creative with image upload
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/ \
  -F "name=Image Banner" \
  -F "type=banner" \
  -F "title=Great Product!" \
  -F "call_to_action=Buy Now" \
  -F "destination_url=https://example.com" \
  -F "image=@banner.jpg"
```

### Get creative details
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/{creative_id}/"
```

### Update creative
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/{creative_id}/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "is_active": false}'
```

### Delete creative
```bash
curl -X DELETE http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/creatives/{creative_id}/
```

## 🎯 Targeting Management (No Auth)

### List targets for a campaign
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/targets/"
```

### Create targeting rules
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/targets/ \
  -H "Content-Type: application/json" \
  -d '{
    "os_android": true,
    "os_ios": true,
    "gender": "all",
    "age_min": 18,
    "age_max": 65,
    "countries": ["US", "CA"],
    "regions": ["California", "New York"],
    "cities": ["San Francisco", "New York City"],
    "interests": ["technology", "gaming"]
  }'
```

### Update targeting
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/campaigns/{campaign_id}/targets/{target_id}/ \
  -H "Content-Type: application/json" \
  -d '{"age_min": 25, "age_max": 45}'
```

## 🏢 Placement Management (No Auth)

### List all placements
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/placements/"
```

### Create new placement
```bash
curl -X POST http://localhost:8000/api/v1/advertising/placements/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile Banner Bottom",
    "code": "mobile_banner_bottom",
    "description": "Bottom banner for mobile apps",
    "recommended_width": 320,
    "recommended_height": 50,
    "is_active": true
  }'
```

### Get placement details
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/placements/{placement_id}/"
```

### Update placement
```bash
curl -X PATCH http://localhost:8000/api/v1/advertising/placements/{placement_id}/ \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

## 📱 Mobile Ad Serving (No Auth)

### Request specific ad types
```bash
# Request banner ads only
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.test.app",
    "app_version": "1.0.0",
    "os": "android",
    "os_version": "12.0",
    "device_type": "phone",
    "ad_types": ["banner"],
    "limit": 1
  }'

# Request multiple ad types
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.test.app",
    "os": "ios",
    "device_type": "tablet",
    "ad_types": ["banner", "interstitial", "native"],
    "limit": 3
  }'
```

### Request with targeting data
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.test.app",
    "os": "android",
    "device_type": "phone",
    "country": "US",
    "region": "California", 
    "city": "San Francisco",
    "gender": "male",
    "age": 30,
    "interests": ["technology", "gaming"],
    "ad_types": ["banner"]
  }'
```

### Log ad click
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/{ad_id}/click/ \
  -H "Content-Type: application/json"
```

## 📊 Analytics & Reports (No Auth)

### Get overall analytics
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/"
```

### Get campaign-specific analytics
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/campaigns/{campaign_id}/"
```

### Get analytics with date filtering
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/analytics/?start_date=2025-05-01&end_date=2025-05-31"
```

## ⚡ Quick Testing Commands

### 1. Test API is running
```bash
curl -X GET http://localhost:8000/api/v1/advertising/placements/ | jq '.'
```

### 2. Create a test campaign
```bash
curl -X POST http://localhost:8000/api/v1/advertising/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign ' $(date +%s) '",
    "company_name": "Test Company",
    "status": "active",
    "start_date": "2025-05-26T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "daily_budget": "100.00",
    "total_budget": "10000.00"
  }' | jq '.'
```

### 3. Test mobile ad serving
```bash
curl -X POST http://localhost:8000/api/v1/advertising/mobile/ads/ \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "test.app.$(date +%s)",
    "os": "android",
    "device_type": "phone"
  }' | jq '.'
```

### 4. Get campaign list with pretty output
```bash
curl -X GET "http://localhost:8000/api/v1/advertising/campaigns/" | jq '.results[] | {id, name, status, is_active}'
```

## 🛠️ Query Parameters

### Pagination
- `?page=2` - Get page 2
- `?page_size=20` - 20 items per page (max 100)

### Campaign Filtering
- `?status=active` - Only active campaigns
- `?status=draft` - Only draft campaigns

## 🔄 Response Examples

### Campaign List Response
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Test Campaign",
      "company_name": "Test Company",
      "status": "active",
      "start_date": "2025-05-26T00:00:00Z",
      "end_date": "2025-12-31T23:59:59Z",
      "daily_budget": "100.00",
      "total_budget": "10000.00",
      "budget_exceeded_action": "pause_day",
      "created_at": "2025-05-26T10:00:00Z",
      "is_active": true
    }
  ]
}
```

### Mobile Ad Response
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
    "ad_type": "banner",
    "title": "Great Product!",
    "description": "Amazing deal",
    "image_url": "http://localhost:8000/media/ad_creatives/banner.jpg",
    "video_url": null,
    "cta": "Buy Now",
    "action_url": "https://example.com",
    "width": 320,
    "height": 50,
    "placement_code": "mobile_banner_top"
  }
]
```

## 🚨 Common Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

## 🔧 **Re-enabling Authentication**

When you're ready to restore authentication, run:

```bash
# Restore the original views file
cp apps/advertising/views_backup.py apps/advertising/views.py

# Or manually uncomment the authentication lines and comment out AllowAny
```

## 💡 Pro Tips for Testing

1. **Use jq for pretty JSON**: Add `| jq '.'` to curl commands
2. **Save IDs**: Store campaign/creative IDs in variables for reuse
3. **Test incrementally**: Create campaign → add creative → add targeting → test ads
4. **Check responses**: Always verify the response structure matches expectations
5. **Use timestamps**: Add timestamps to test data to avoid duplicates

---

**⚠️ Remember**: This is for TESTING ONLY. Re-enable authentication before production! 