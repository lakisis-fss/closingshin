import os
from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
from dotenv import load_dotenv

load_dotenv()

PB_URL = "http://localhost:8090"
PB_EMAIL = "admin@example.com"
PB_PASSWORD = "admin1234"

pb = PocketBase(PB_URL)

def authenticate():
    try:
        pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)
        print(f"Connecting to {PB_URL}...")
        print("Authenticated successfully.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        exit(1)

def create_collection(name, schema, indexes=None):
    try:
        pb.collections.create({
            "name": name,
            "type": "base",
            "fields": schema,
            "indexes": indexes or []
        })
        print(f"Collection '{name}' created successfully.")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Collection '{name}' already exists. Skipping.")
        else:
            print(f"Failed to create collection '{name}': {e}")

if __name__ == "__main__":
    authenticate()

    # VCP Reports
    create_collection("vcp_reports", [
        {"name": "date", "type": "date", "required": True, "id": "vcp_date"},
        {"name": "code", "type": "text", "required": True, "id": "vcp_code"},
        {"name": "name", "type": "text", "id": "vcp_name"},
        {"name": "score", "type": "number", "id": "vcp_score"},
        {"name": "pivot_price", "type": "number", "id": "vcp_pivot"},
        {"name": "chart_image", "type": "file", "options": {"maxSelect": 1, "maxSize": 5242880}, "id": "vcp_chart"}
    ], ["CREATE INDEX idx_vcp_date ON vcp_reports (date)", "CREATE INDEX idx_vcp_code ON vcp_reports (code)"])

    # News Analysis
    create_collection("news_analysis", [
        {"name": "date", "type": "date", "required": True, "id": "news_date"},
        {"name": "code", "type": "text", "id": "news_code"},
        {"name": "title", "type": "text", "id": "news_title"},
        {"name": "link", "type": "url", "id": "news_link"},
        {"name": "sentiment_score", "type": "number", "id": "news_sentiment"},
        {"name": "summary", "type": "text", "id": "news_summary"}
    ], ["CREATE INDEX idx_news_date ON news_analysis (date)"])

    # Raw News
    create_collection("news", [
        {"name": "date", "type": "date", "required": True, "id": "raw_news_date"},
        {"name": "code", "type": "text", "id": "raw_news_code"},
        {"name": "ticker", "type": "text", "id": "raw_news_ticker"},
        {"name": "name", "type": "text", "id": "raw_news_name"},
        {"name": "title", "type": "text", "id": "raw_news_title"},
        {"name": "link", "type": "url", "id": "raw_news_link"},
        {"name": "pub_date", "type": "text", "id": "raw_news_pub_date"},
        {"name": "description", "type": "text", "id": "raw_news_desc"},
        {"name": "score", "type": "number", "id": "raw_news_score"}
    ], ["CREATE INDEX idx_raw_news_date ON news (date)"])

    # Stock Information
    create_collection("stock_infos", [
        {"name": "code", "type": "text", "unique": True, "required": True, "id": "stock_code"},
        {"name": "name", "type": "text", "id": "stock_name"},
        {"name": "market", "type": "text", "id": "stock_market"},
        {"name": "sector", "type": "text", "id": "stock_sector"},
        {"name": "info", "type": "json", "id": "stock_info"}
    ])

    # Portfolio
    create_collection("portfolio", [
        {"name": "code", "type": "text", "required": True, "id": "port_code"},
        {"name": "name", "type": "text", "id": "port_name"},
        {"name": "market", "type": "text", "id": "port_market"},
        {"name": "buy_date", "type": "date", "id": "port_buy_date"},
        {"name": "buy_price", "type": "number", "id": "port_buy_price"},
        {"name": "quantity", "type": "number", "id": "port_qty"},
        {"name": "status", "type": "text", "id": "port_status"},
        {"name": "memo", "type": "text", "id": "port_memo"},
        {"name": "exit_conditions", "type": "json", "id": "port_exit"},
        {"name": "simulation_data", "type": "json", "id": "port_sim"},
        {"name": "initial_scores", "type": "json", "id": "port_score"},
        {"name": "legacy_id", "type": "text", "unique": True, "id": "port_legacy"}
    ], ["CREATE INDEX idx_port_code ON portfolio (code)"])

    # Market Status
    create_collection("market_status", [
        {"name": "date", "type": "date", "required": True, "unique": True, "id": "ms_date"},
        {"name": "data", "type": "json", "id": "ms_data"}
    ])

    # Target Lists
    create_collection("target_lists", [
        {"name": "date", "type": "date", "required": True, "id": "tl_date"},
        {"name": "codes", "type": "json", "id": "tl_codes"},
        {"name": "description", "type": "text", "id": "tl_desc"}
    ])

    # Settings
    create_collection("settings", [
        {"name": "key", "type": "text", "required": True, "unique": True, "id": "set_key"},
        {"name": "value", "type": "json", "id": "set_val"}
    ])

    # OHLCV (Price History)
    create_collection("ohlcv", [
        {"name": "code", "type": "text", "required": True, "id": "ohlcv_code"},
        {"name": "date", "type": "date", "required": True, "id": "ohlcv_date"},
        {"name": "open", "type": "number", "id": "ohlcv_open"},
        {"name": "high", "type": "number", "id": "ohlcv_high"},
        {"name": "low", "type": "number", "id": "ohlcv_low"},
        {"name": "close", "type": "number", "id": "ohlcv_close"},
        {"name": "volume", "type": "number", "id": "ohlcv_vol"},
        {"name": "change", "type": "number", "id": "ohlcv_change"},
        {"name": "uid", "type": "text", "required": True, "unique": True, "id": "ohlcv_uid"}
    ], [
        "CREATE INDEX idx_ohlcv_code ON ohlcv (code)",
        "CREATE INDEX idx_ohlcv_date ON ohlcv (date)",
        "CREATE UNIQUE INDEX idx_ohlcv_uid ON ohlcv (uid)"
    ])

    print("\nAll data schemas have been initialized!")
