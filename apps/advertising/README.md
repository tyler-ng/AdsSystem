# Mobile Advertising API Documentation

This document provides details on how to integrate your mobile app with our advertising system.

## Ad Request API

### Endpoint

```
POST /api/v1/advertising/mobile/ads/
```

### Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "app_id": "com.example.myapp",          // Required - Your app's unique identifier
  "app_version": "1.2.3",                 // Required - Your app's version
  "os": "ios",                           // Required - "ios" or "android"
  "os_version": "16.0",                  // Required - OS version
  "device_type": "phone",                // Required - "phone" or "tablet"
  "width": 320,                          // Optional - Screen width in dp/pt
  "height": 480,                         // Optional - Screen height in dp/pt
  "country": "US",                       // Optional - ISO country code
  "region": "CA",                        // Optional - Region/state
  "city": "San Francisco",               // Optional - City name
  "gender": "male",                      // Optional - "male", "female", "other"
  "age": 25,                             // Optional - User age
  "interests": ["sports", "technology"], // Optional - User interests
  "ad_types": ["banner", "native"],      // Optional - Ad types you want to display
  "limit": 1                             // Optional - Number of ads to return (default: 1)
}
```

### Success Response

```json
[
  {
    "id": "9f8d7c6b-5a4e-3f2d-1b0c-9a8b7c6d5e4f",
    "campaign_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
    "ad_type": "banner",
    "title": "Amazing Product",
    "description": "This product will change your life!",
    "image_url": "http://example.com/media/ad_creatives/banner_image.jpg",
    "video_url": null,
    "cta": "Buy Now",
    "action_url": "https://example.com/product",
    "width": 320,
    "height": 50
  }
]
```

### Error Response

```json
{
  "detail": "No matching ads found"
}
```

## Tracking Ad Impressions

Impressions are automatically tracked when ads are served. No additional API call is needed.

## Tracking Ad Clicks

When a user clicks on an ad, you should send a click event to our API.

### Endpoint

```
POST /api/v1/advertising/mobile/ads/{ad_id}/click/
```

### Headers

```
Content-Type: application/json
```

### Success Response

```json
{
  "status": "success",
  "click_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}
```

## Implementation Guidelines

1. **Request Timing**: Request ads when your app starts or when you're about to display them, not in advance.

2. **Cache Handling**: You can cache the ad response for up to 5 minutes to reduce API calls.

3. **Error Handling**: Implement proper error handling to gracefully handle cases when no ads are available.

4. **User Privacy**: Only send user data that you have permission to share, adhering to privacy regulations like GDPR and CCPA.

5. **Testing**: Use the sandbox environment for testing by adding `?environment=sandbox` to the API endpoints.

## Ad Types and Sizes

| Ad Type      | Recommended Size (dp/pt) |
|--------------|--------------------------|
| Banner       | 320×50, 728×90           |
| Interstitial | Full screen              |
| Native       | Flexible                 |

## Support

For integration support, please contact our developer support team at dev-support@example.com 