import json
import subprocess
import os

data = {
    "ticker": "005930",
    "buyDate": "2026-03-27",
    "buyPrice": 75000,
    "quantity": 100,
    "exitConditions": {
        "stopLossPercent": 7
    }
}

script_path = os.path.join(os.getcwd(), "Scripts", "simulate_trade.py")

process = subprocess.Popen(["python", script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate(input=json.dumps(data))

print("Exit Code:", process.returncode)
print("Stdout:", stdout)
print("Stderr:", stderr)
