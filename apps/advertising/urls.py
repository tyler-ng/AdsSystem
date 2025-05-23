from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Create a router for the main viewsets
router = routers.DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')

# Create nested routers for campaign resources
campaign_router = routers.NestedDefaultRouter(router, r'campaigns', lookup='campaign')
campaign_router.register(r'creatives', views.CreativeViewSet, basename='campaign-creative')
campaign_router.register(r'targets', views.TargetViewSet, basename='campaign-target')

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    path('', include(campaign_router.urls)),
    
    # Mobile-specific ad serving endpoints
    path('mobile/ads/', views.MobileAdServingView.as_view(), name='mobile-ad-serving'),
    path('mobile/ads/<uuid:ad_id>/click/', views.LogAdClickView.as_view(), name='mobile-ad-click'),
    
    # Analytics endpoints
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('analytics/campaigns/<uuid:campaign_id>/', views.AnalyticsView.as_view(), name='campaign-analytics'),
] 