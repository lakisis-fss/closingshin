import json
import subprocess
import os

# Sample data
data = {
    "ticker": "005930", # Samsung
    "buyDate": "2024-03-25",
    "buyPrice": 78000,
    "quantity": 10,
    "exitConditions": {
        "stopLossPercent": 5,
        "takeProfitPercent": 10
    }
}

script_path = os.path.abspath("Scripts/simulate_trade.py")
print(f"Running simulation script: {script_path}")

process = subprocess.Popen(
    ["python", script_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = process.communicate(input=json.dumps(data))

print("Return Code:", process.returncode)
print("Stdout:", stdout)
print("Stderr:", stderr)
