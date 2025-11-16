# Home Departure Board – Product Requirements Document (PRD)
**Version:** 1.0  
**Author:** Ranbir (with ChatGPT)  
**Date:** 2025-11-15  

## 1. Overview

The **Home Departure Board** is a wall-mounted or tablet-displayed web dashboard that shows everything needed to leave the house in under 5 seconds of glance time.

It consolidates:

- Real-time transit departures (STM buses / Métro)
- BIXI bike availability
- Local weather
- Air quality (AQI)
- Sunrise/sunset time
- Alerts (STM disruptions, weather warnings)
- A “Leave-Now” indicator based on walking time to the stop

The board is a **lightweight client-side web app** powered by a **simple backend** that fetches data from public real-time feeds.

## 2. Goals

### Primary Goal
Provide all necessary “leave-the-house” information at a glance to minimize decision friction.

### Secondary Goals
- Run on ultra-cheap hardware (budget tablet or Raspberry Pi)
- Simple to maintain and extend
- Fast-loading, low CPU usage
- Flexible enough to add new widgets later

## 3. Non-Goals

- No trip-planning / routing features  
- No mobile app required  
- No user accounts or personal data  
- No complex map rendering  

## 4. Users

### Primary User
- Ranbir — Montréal parent commuting via STM/BIXI

### Secondary Users
- Family members  
- Guests visiting the home  

## 5. Core Features

### 5.1 Real-Time Transit Departatures (STM)
- List of next departures for chosen stop(s)
- Each row includes:
  - Route number
  - Route/headsign
  - Stop name + code
  - Arrival time (in minutes)
- Source: STM GTFS-Realtime feed (trip updates)

### 5.2 BIXI Station Status
- For selected stations:
  - Bikes available
  - Docks available
  - Station name + ID
- Source: BIXI GBFS API (station_status + station_information)

### 5.3 Weather Overview
- Temperature
- Feels-like temperature
- Condition (rain/snow/sun)
- Wind speed + direction
- Precipitation probability
- Source: Open-Meteo or Environment Canada

### 5.4 Air Quality (AQI)
- Current AQI value
- Category label (Good, Moderate, etc.)
- Source: Open-Meteo or Canadian AQHI

### 5.5 Sunrise / Sunset
- Today’s sunrise time
- Today’s sunset time

### 5.6 Leave-Now Indicator
A dynamic indicator using:
- Soonest upcoming departure
- User-configured walking time (minutes)
- User-configured buffer time  
- Output: “Leave now” or “Leave in X minutes”  

### 5.7 Alerts (STM + Weather)
- Show STM service issues or weather alerts
- Each includes:
  - Source (STM/EC)
  - Title
  - Severity (`info`, `warning`, `critical`)

## 6. System Architecture

```
[ Front-End Web App ] 
        | fetches JSON
        v
[ Local/Cloud Backend API ]
        |
        +--> STM GTFS-Realtime
        +--> BIXI GBFS
        +--> Weather API
        +--> AQI API
        +--> Alerts sources
```

### 6.1 Front-End
- File: `index.html`
- Pure HTML/CSS/JS
- Auto-refresh ~30 seconds
- High-contrast dark mode
- Responsive layout

### 6.2 Backend Endpoints (JSON)
(Endpoints definitions omitted for brevity.)

## 7. Hardware Requirements

- Cheap Android tablets  
- Amazon Fire HD  
- Raspberry Pi + HDMI  
- Smart frames with browsers  

## 8. User Configuration

Editable values:
- Transit stop IDs  
- BIXI station IDs  
- Walking time  
- Buffer time  
- API URLs  
- Refresh interval  
- Units  

## 9. UX Requirements

- One-screen dashboard  
- Large text  
- High contrast  
- Urgency colors  
- Responsive  

## 10. Technical Requirements

Front-End:
- Vanilla JS  
- `fetch()`  
- Auto-refresh  

Backend:
- Python Flask  
- Fetch and transform STM/BIXI/Weather/AQI/Alerts  

## 11. Future Enhancements

- Baby clothing guidance  
- Calendar integration  
- Garbage pickup  
- “Should I bike?”  
- Modular widgets  

## 12. Deliverables

- `index.html`  
- `app.py`  
- `config.yaml`  
- Setup guides  

