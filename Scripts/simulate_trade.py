import sys
import json
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

def simulate(data):
    try:
        ticker = data.get('ticker')
        buy_date_str = data.get('buyDate') # YYYY-MM-DD
        buy_price = float(data.get('buyPrice'))
        exit_conditions = data.get('exitConditions', {})
        
        # Parse dates
        buy_date = pd.to_datetime(buy_date_str)
        today = datetime.now()
        
        # Determine Market for FDR
        # Assuming 'market' is passed or we try both. FDR handles ticker usually.
        # For KRX, ticker is usually 6 digits.
        
        # Fetch OHLCV Data
        # Fetch from buy_date to today
        df = fdr.DataReader(ticker, buy_date, today)
        
        if df.empty:
            return {
                "status": "ERROR",
                "message": "No data found for ticker"
            }
            
        # Simulation State
        status = "OPEN"
        exit_date = None
        exit_price = None
        exit_reason = None
        highest_price = 0
        
        # Conditions
        stop_loss_pct = exit_conditions.get('stopLossPercent') # e.g. 7.0
        take_profit_pct = exit_conditions.get('takeProfitPercent') # e.g. 15.0
        trailing_stop_pct = exit_conditions.get('trailingStopPercent') # e.g. 10.0
        time_cut_days = exit_conditions.get('timeCutDays')
        
        # Iterate daily starting from the day AFTER buy_date
        # Logic: If we buy at the Close of buy_date, we only start monitoring for exits from the NEXT trading day.
        # This avoids immediate exits on the buy date due to intraday volatility that happened before/during purchase.
        
        # Filter dataframe to only include days after buy_date
        df_simulation = df[df.index > buy_date]
        
        if df_simulation.empty:
            # Still on the buy date or no subsequent data
            current_price = df.iloc[-1]['Close']
            return {
                "status": "OPEN",
                "exitDate": None,
                "exitPrice": current_price,
                "exitReason": None,
                "realizedPnl": (current_price - buy_price) * float(data.get('quantity', 0)),
                "realizedPnlPercent": ((current_price - buy_price) / buy_price) * 100.0,
            }

        days_held = 1 # Already spent the buy day
        
        for date, row in df_simulation.iterrows():
            current_date_str = date.strftime('%Y-%m-%d')
            
            # Skip buy date itself if data includes it? 
            # Usually we assume buy happens at some point on buy date.
            # Let's verify end-of-day for buy date or start checking next day?
            # Conservative: Check next day Open? 
            # Aggressive: Check buy date Low/High if Buy Price is within range?
            # Let's assume we check from the Buy Date itself (intraday movement after buy)
            
            open_price = row['Open']
            high_price = row['High']
            low_price = row['Low']
            close_price = row['Close']
            
            # Update Highest Price for Trailing Stop
            if high_price > highest_price:
                highest_price = high_price
            
            # 1. Stop Loss Check
            if stop_loss_pct:
                stop_price = buy_price * (1 - stop_loss_pct / 100.0)
                if low_price <= stop_price:
                    status = "CLOSED"
                    # Slippage model: If Open < Stop Price (Gap Down), exit at Open. Else Stop Price.
                    exit_price = open_price if open_price < stop_price else stop_price
                    exit_date = current_date_str
                    exit_reason = f"Stop Loss (-{stop_loss_pct}%)"
                    break
            
            # 2. Take Profit Check
            if take_profit_pct:
                target_price = buy_price * (1 + take_profit_pct / 100.0)
                if high_price >= target_price:
                    status = "CLOSED"
                    # Slippage: If Open > Target (Gap Up), exit at Open. Else Target.
                    exit_price = open_price if open_price > target_price else target_price
                    exit_date = current_date_str
                    exit_reason = f"Take Profit (+{take_profit_pct}%)"
                    break
            
            # 3. Trailing Stop Check
            if trailing_stop_pct and highest_price > buy_price:
                trail_price = highest_price * (1 - trailing_stop_pct / 100.0)
                # Only activate if trail_price > buy_price? Or always?
                # Usually TS is to protect profit, so trail_price > buy_price
                if trail_price > buy_price:
                    if low_price <= trail_price:
                        status = "CLOSED"
                        exit_price = open_price if open_price < trail_price else trail_price
                        exit_date = current_date_str
                        exit_reason = f"Trailing Stop (-{trailing_stop_pct}% from peak)"
                        break

            # 4. Time Cut Check
            # Check at END of day
            if time_cut_days:
                # Simple day count
                if days_held >= int(time_cut_days):
                   status = "CLOSED"
                   exit_price = close_price
                   exit_date = current_date_str
                   exit_reason = f"Time Cut ({time_cut_days} days)"
                   break
            
            days_held += 1

        # Calculate Final Result
        if status == "CLOSED":
            realized_pnl = (exit_price - buy_price) * float(data.get('quantity', 0))
            realized_pnl_percent = ((exit_price - buy_price) / buy_price) * 100.0
        else:
            # Still Open
            current_price = df.iloc[-1]['Close']
            realized_pnl = (current_price - buy_price) * float(data.get('quantity', 0))
            realized_pnl_percent = ((current_price - buy_price) / buy_price) * 100.0
            exit_price = current_price # Current price for display
            
        return {
            "status": status,
            "exitDate": exit_date,
            "exitPrice": exit_price,
            "exitReason": exit_reason,
            "realizedPnl": realized_pnl,
            "realizedPnlPercent": realized_pnl_percent,
        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    try:
        # Read all input from stdin
        input_str = sys.stdin.read()
        
        if not input_str or input_str.strip() == "":
            print(json.dumps({"status": "ERROR", "message": "No input data received"}))
            sys.exit(1)
            
        data = json.loads(input_str)
        result = simulate(data)
        
        # Ensure only JSON is printed
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "ERROR", "message": f"Invalid JSON input: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "ERROR", "message": f"Unexpected error: {str(e)}"}))
        sys.exit(1)
