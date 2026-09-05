# Project Context: SIH26143 - Oil Spill Detection & Vessel Correlation

## Global Frontend Constraints (The 90-Second Judge Test)
1. Zero Generic Dashboards: Every UI element must directly serve the narrative of identifying an oil spill and proving which vessel caused it.
2. The 1-Click Scenario: All code must support a "Run Demo" state that instantly loads pre-cached data, bypassing API delays.
3. Interactive Proof: Prioritize layered maps (Base -> SAR -> Spill Polygon -> AIS Tracks) and time-scrubbing sliders to show cause and effect.
4. Offline First: Wrap all network calls (map tiles, datasets) in try/except blocks with local fallbacks to /public/demo_data/ in case hackathon Wi-Fi fails.
5. Role Switcher: Incorporate UI states for different stakeholders (e.g., Coast Guard action items vs. Environmental Auditor metrics).

## Technical Output Rules
* Write clean, modular code.
* Always assume a disconnected/offline environment for the main demo track.
* Do not generate placeholder functions for core demo features; write the actual mock data logic.