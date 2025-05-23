# Advertising System - Business Features Overview

## What Our Advertising System Does

Our advertising system helps businesses show their ads to mobile app users. We connect companies who want to advertise with mobile apps that can display those ads, and we track how well the ads perform.

## Core Business Features

### 1. Campaign Creation for Business Partners

When a business partner wants to advertise with us, we create a **Campaign** for them. Each campaign includes:

**Basic Campaign Information:**
- Campaign name and description
- Company name of the advertiser
- Start and end dates for when ads should run
- Budget limits (how much they want to spend per day and in total)
- Advanced daily spending controls with configurable budget exceeded actions
- Real-time budget monitoring and automatic overspend protection

**Campaign Status Management:**
- **Draft**: Campaign is being set up but not running yet
- **Active**: Campaign is live and showing ads to users
- **Paused**: Campaign is temporarily stopped
- **Completed**: Campaign has finished running
- **Archived**: Campaign is stored for historical records

### 2. Creative Ad Types

We support different types of advertisements that businesses can create:

**Banner Ads**
- Small rectangular ads that appear at the top or bottom of mobile apps
- Common sizes: 320×50 pixels (mobile banner) or 728×90 pixels (tablet banner)
- Best for brand awareness and simple promotions

**What Each Creative Ad Contains:**
- Title and description text
- Images or videos
- Link to advertiser's website or app store
- Specific dimensions for proper display

### 3. Ad Placement Management

**What is Ad Placement?**
Ad placements are specific locations within mobile apps where advertisements can appear.

**How We Manage Placements:**
- We define different spots in mobile apps where ads can be shown
- Each placement has recommended sizes for ads
- We track which placements perform better for different types of ads
- App developers can choose which placements to include in their apps

**Examples of Placements:**
- Top banner in a news app
- Between levels in a game
- Bottom of a shopping app screen
- Pop-up when opening an app

### 4. Targeting Options for Campaigns

We help businesses reach the right audience by targeting ads based on:

**Demographics:**
- Age groups (e.g., 18-25, 26-35, etc.)
- Gender (male, female, or all users)
- Geographic location (specific countries, regions, or cities)

**Device Information:**
- Type of phone or tablet (iPhone, Android, etc.)
- Operating system versions
- Screen sizes

**User Interests:**
- Categories like sports, technology, fashion, food, etc.
- Based on app usage patterns and preferences

### 5. Advertisement Performance Tracking

Our system automatically tracks how well ads are performing:

**Impression Tracking**
- **What it is**: Every time an ad is shown to a user, we count it as one "impression"
- **What we track**: 
  - How many times each ad was displayed
  - When and where it was shown
  - What type of device viewed it
  - Geographic location of viewers

**Click Tracking**
- **What it is**: When a user taps on an ad, we count it as a "click"
- **What we measure**:
  - Click-through rate (CTR): Percentage of people who click after seeing an ad
  - Which ads get clicked most often
  - What time of day gets more clicks

**Display Rate Calculation**
- **What it measures**: How often we actually show a campaign's ads when we have opportunities
- **How we calculate it**:
  1. We sample a small percentage (5%) of all ad request opportunities
  2. For these sampled opportunities, we track:
     - How many times we could have shown the campaign's ad
     - How many times we actually chose to show it
  3. Display Rate = (Times Shown ÷ Total Opportunities) × 100
- **Why this matters**: Helps businesses understand how competitive their ads are and how often users see them

**Performance Reports Include:**
- Daily impression counts
- Total clicks and click-through rates
- Display rates and opportunity metrics
- Geographic performance breakdown
- Device type performance
- Time-of-day performance patterns

### 6. Daily Spending Controls & Budget Management

Our system provides comprehensive budget protection to ensure advertisers never overspend their intended limits. This feature gives businesses complete control over their advertising costs with automatic safeguards.

**Daily Spending Limits**
- **What it does**: Prevents campaigns from exceeding their daily budget allocation
- **How it works**: 
  - System tracks every ad impression cost in real-time (currently $0.01 per impression)
  - Automatically stops serving ads when daily limit is reached
  - Resets automatically at midnight for the next day
- **Business benefit**: Protects against unexpected cost spikes and provides predictable daily spending

**Configurable Budget Exceeded Actions**

When a campaign reaches its daily spending limit, advertisers can choose from five different response actions:

1. **Pause for the Day (Default)**
   - Stops showing ads for the rest of the current day only
   - Campaign automatically resumes the next day
   - Best for: Standard campaigns with consistent daily budgets

2. **Pause Entire Campaign**
   - Completely pauses the campaign until manually reactivated by an admin
   - Sends notification to the advertiser
   - Best for: Campaigns that require manual review before continuing

3. **Continue with Limited Frequency**
   - Keeps showing ads but with significantly reduced frequency (10% of normal rate)
   - Uses configurable frequency cap settings
   - Best for: High-value campaigns that need continued exposure even after budget limits

4. **Stop Immediately**
   - Stops ads immediately for the day but keeps campaign active for tomorrow
   - More conservative approach than "pause for day"
   - Best for: Cost-sensitive campaigns requiring strict budget adherence

5. **Email Notification Only**
   - Continues serving ads normally but sends alerts to advertisers
   - Useful for monitoring high-performing campaigns
   - Best for: Campaigns where slight budget overruns are acceptable

**Real-Time Budget Monitoring**

Our admin dashboard provides comprehensive budget oversight:

**Budget Status Indicators**
- **Green**: Under 70% of daily budget spent - "GOOD"
- **Orange**: 70-90% of daily budget spent - "MODERATE" 
- **Red**: Over 90% of daily budget spent - "WARNING"
- **Red with Alert**: Budget exceeded - shows configured action taken

**Daily Spending Tracking**
- Real-time spending amounts for each campaign
- Remaining daily budget calculations
- Historical spending patterns over the last 7 days
- Budget exceeded events and actions taken

**Administrative Controls**
- View all campaign budget statuses in one dashboard
- Filter campaigns by budget status (within budget, exceeded, etc.)
- Manual budget reset capabilities for special circumstances
- Detailed spending reports with date ranges

**How Budget Controls Work:**
- **Real-time tracking**: Every ad impression immediately updates spending totals
- **Automatic enforcement**: System checks budget before serving each ad
- **Immediate response**: Configured actions trigger instantly when limits are reached
- **Daily reset**: All budget limits automatically reset at midnight
- **Notification system**: Advertisers receive alerts about budget status changes

**Cost Tracking Features:**
- Cost per impression (CPM) - currently $0.01 per impression
- Cost per click (CPC) calculation based on actual clicks
- Total campaign spending with daily breakdowns
- Budget utilization percentages
- Remaining budget alerts and projections

**Business Benefits of Daily Spending Controls:**
- **Cost Predictability**: Advertisers know exactly how much they'll spend each day
- **Overspend Protection**: Automatic safeguards prevent budget overruns
- **Flexible Response**: Five different actions accommodate various business needs
- **Real-time Visibility**: Instant budget status updates in admin dashboard
- **Historical Analysis**: Track spending patterns to optimize future campaigns
- **Risk Management**: Different protection levels for different campaign priorities

**Technical Implementation:**
- Database tracking of daily spending per campaign
- Automatic budget checks before each ad impression
- Configurable spending thresholds and actions
- Integration with ad serving system for real-time enforcement
- Admin interface for monitoring and manual controls

This comprehensive budget management system ensures that our advertising partners have complete control over their spending while providing multiple layers of protection against cost overruns. The flexible action system accommodates different business strategies, from strict cost control to performance-focused approaches.
