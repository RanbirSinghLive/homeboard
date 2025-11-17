# How Google Maps Calculates Transit Delays

## Google's Approach

Google Maps uses **multiple data sources** and **sophisticated algorithms** to calculate live delays:

### 1. **GTFS-Realtime Feeds** (Same as we use)
- Trip Updates feed (what we're using)
- Vehicle Positions feed (GPS locations)
- Alerts feed (service disruptions)

### 2. **Combining Data Sources**

Google likely:
1. **Matches vehicles to trips** - Uses Vehicle Positions to find which bus is on which trip
2. **Calculates delays from GPS** - Compares where the bus is vs where it should be according to schedule
3. **Uses historical data** - Learns typical delays for routes/times
4. **Machine learning** - Predicts delays based on patterns

### 3. **Why STM Feed Has No Delays**

The STM GTFS-Realtime feed provides:
- ✅ Trip Updates (scheduled times)
- ✅ Vehicle Positions (GPS locations)
- ❌ **No pre-calculated delays**

Google calculates delays themselves by:
- Matching Vehicle Positions → Trip Updates
- Comparing actual position to scheduled position
- Using historical patterns and traffic data

## What We Can Do

### Option 1: Keep Current (Simplest)
- Show all times as scheduled (black)
- Accept that STM doesn't provide delay data
- Most accurate to what the API provides

### Option 2: Calculate Delays from Vehicle Positions (Complex)
- Match vehicles to trips using trip_id
- Compare vehicle's current stop sequence to scheduled stop sequence
- Calculate delay based on position
- **Challenges:**
  - Need to match vehicles to trips accurately
  - Need to know scheduled stop sequence
  - Less accurate than pre-calculated delays
  - Complex to implement

### Option 3: Use Google's Transit API (If Available)
- Google provides a Transit API
- But it's not free and requires API key
- May have rate limits

## Recommendation

**Keep current behavior** - Show all times as scheduled (black) because:
1. STM doesn't provide delay data in their feed
2. Calculating delays from GPS is complex and error-prone
3. Google has massive resources (ML, historical data, traffic data) we don't have
4. Scheduled times are still useful information

