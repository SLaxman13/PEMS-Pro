PEMS Pro stands for Personalized Environmental Monitoring System.
It is designed to continuously monitor the environment around a person and understand how it affects their health over time.
Instead of just showing raw sensor values like temperature or air quality, PEMS Pro goes one step further by calculating an Exposure Score. This score represents how safe or risky the environment is, based on multiple factors like air quality, temperature, noise, UV levels, and even the user’s activity.
The main idea is simple:
 Not just measure the environment, but interpret it in a meaningful way for the user.
So, PEMS Pro helps users quickly understand:
Whether their environment is safe
When conditions are becoming risky
When they should take action (like moving to a safer place)
🔄 Data Flow in PEMS Pro
The system works in a simple flow from hardware to app.
First, the ESP32 device collects data from all the sensors. These include air quality, temperature, noise, UV, and motion. It processes this data and calculates the exposure score in real time.
Then, the ESP32 sends all this data to the ThingSpeak cloud using WiFi. This happens continuously, so the latest data is always available online.
Next, the Streamlit application fetches this data from ThingSpeak. It keeps updating every few seconds and displays everything in a dashboard format.
In the dashboard, the user can see all the values clearly along with the exposure score. The app also shows whether the condition is safe, low risk, moderate, or high risk, so the user doesn’t have to interpret raw numbers.
Finally, this dashboard is converted into a mobile app, so the user can monitor everything directly from their phone in real time.
