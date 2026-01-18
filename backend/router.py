import time

def call_model(model, prompt):

    # REAL SYSTEM WOULD CALL API HERE
    # Hackathon-safe deterministic stub

    time.sleep(0.2)

    if "Architect" in prompt:
        return """AI + IoT ARCHITECTURE

Edge Layer
• OCPP telemetry
• 30s heartbeat
• fault streams

AI Layer
• availability prediction
• queue ETA
• demand forecast

Platform
• routing
• payments
• fleet APIs"""

    if "Market" in prompt:
        return """TAM/SAM/SOM – EV INDIA

TAM: $2.1B  
SAM: $420M  
SOM: $65M (3yr)

Assumptions:
6M EVs by 2027  
ARPU $6/month"""

    if "Data Analyst" in prompt:
        return """CSV INSIGHTS

• Peak: 6–9pm  
• 38% failures  
• Avg 41min  
• Top city: Bangalore"""

    return "AUTONOMOUS OUTPUT"