from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv
import time
import re
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP(
    name="Memecoin Radar",
    dependencies=["httpx", "python-dotenv", "tabulate"]
)

# Configuration
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
BASE_URL = "https://api.dune.com/api/v1"
HEADERS = {"X-Dune-API-Key": DUNE_API_KEY}

def get_latest_result(query_id: int, limit: int = 1000):
    """
    Fetch the latest results from a Dune Analytics query.

    Args:
        query_id (int): The ID of the Dune query to fetch results from.
        limit (int, optional): Maximum number of rows to return. Defaults to 1000.

    Returns:
        list: A list of dictionaries containing the query results, or an empty list if the request fails.

    Raises:
        httpx.HTTPStatusError: If the API request fails due to a client or server error.
    """
    url = f"{BASE_URL}/query/{query_id}/results"
    params = {"limit": limit}
    with httpx.Client() as client:
        response = client.get(url, params=params, headers=HEADERS, timeout=300)
        response.raise_for_status()
        data = response.json()
        
    result_data = data.get("result", {}).get("rows", [])
    return result_data
    
def strip_a_tag(html):
    match = re.search(r'>(.*?)</a>', html)
    return match.group(1) if match else html
    
def a_tag_link(html):
    match = re.search(r'href="([^"]+)"', html)
    return match.group(1) if match else html

@mcp.tool()
def get_trending_tokens_by_source(source: str = "Telegram", limit: int = 100) -> str:
    """Retrieve top traded tokens on specified source platform in the last 12 hours.

    Args:
        source (str): The platform to query tokens from. Must be one of: 'Telegram', 'Web', 'Mobile'.
            Defaults to 'Telegram'.
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of trending tokens including rank, token name, mint address,
            trading volume, and total trades, or an error message if the query fails.

    Raises:
        ValueError: If an invalid source value is provided.
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    query_ids = {
        "Telegram": 4830187,
        "Web": 4830192,
        "Mobile": 4930328,
    }    
    try:
        query_id = query_ids.get(source)
        if query_id is None:
            raise ValueError("Invalid source value. Allowed: Telegram | Web | Mobile")
        data = get_latest_result(query_id, limit=limit)
        rows = [
            [ 
                row["rank"], 
                strip_a_tag(row["token_link"]), 
                row["token_mint_address"], 
                f'${row["total_volume_usd"]:.2f}', 
                row["total_trades"] 
            ]
            for row in data
        ]
        headers = ["Rank", "Token", "Mint Address", "Volume(12h)", "Total Trades"]    
        return f"# Top {limit} Trending Tokens on {source} - Last 12 Hours\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)

@mcp.tool()
def get_pumpfun_graduates_by_marketcap(limit: int = 100) -> str:
    """Retrieve Pump.fun token launches sorted by highest market capitalization in the last 24 hours.

    Args:
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of Pump.fun graduates including rank, token name, mint address,
            market capitalization, and trade count, or an error message if the query fails.

    Raises:
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    try:
        data = get_latest_result(4124453, limit=limit)
        rows = [
            [ 
                row["rank"], 
                strip_a_tag(row["asset_with_chart"]), 
                row["token_address"], 
                f'${row["market_cap"]:.2f}', 
                row["trade_count"] 
            ]
            for row in data
        ]
        headers = ["Rank", "Token", "Mint Address", "MarketCap", "Trade Count"]
        return f"# Top {limit} Pump.fun Graduates by MarketCap - Last 24 Hours\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_pumpfun_graduates_by_trading_volume(limit: int = 100) -> str:    
    """Retrieve Pump.fun token launches sorted by highest trading volume in the last 24 hours.

    Args:
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of Pump.fun graduates including volume rank, token name,
            mint address, trading volume, and graduation time, or an error message if the query fails.

    Raises:
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    try:
        data = get_latest_result(4832613, limit=limit)
        rows = [
            [ 
                row["volume_rank"], 
                strip_a_tag(row["asset_with_chart"]), 
                strip_a_tag(row["token_address_with_chart"]), 
                f'${row["total_volume"]:.2f}', 
                row["graduation_time"] 
            ]
            for row in data
        ]
        headers = ["Rank", "Token", "Mint Address", "Volume(12h)", "Graduation Time"]
        return f"# Top {limit} Pump.fun Graduates by Trading Volume - Last 24 Hours\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_recent_pumpfun_graduates(limit: int = 100) -> str:
    """Retrieve the most recently graduated tokens from Pump.fun in the last 24 hours.

    Args:
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of recent Pump.fun graduates including graduation time,
            token name, mint address, market capitalization, and trade count,
            or an error message if the query fails.

    Raises:
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    try:
        data = get_latest_result(4832245, limit=limit)
        rows = [
            [ 
                row["graduation_time"], 
                strip_a_tag(row["asset_with_chart"]), 
                strip_a_tag(row["token_address_with_chart"]), 
                f'${row["market_cap"]:.2f}', 
                row["trade_count"] 
            ]
            for row in data
        ]
        headers = ["Graduation Time", "Token", "Mint Address", "Market Cap", "Trade Count"]
        return f"# Recent {limit} Pump.fun Graduates - Last 24 Hours\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_recent_kol_buys(limit: int = 100) -> str:
    """Retrieve recent token purchases by memecoin Key Opinion Leaders (KOLs).

    Args:
        limit (int): Maximum number of buy transactions to return. Defaults to 100.

    Returns:
        str: A formatted table of recent KOL buys including buy time, KOL name,
            token name, mint address, and purchase amount, or an error message if the query fails.

    Raises:
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    try:
        data = get_latest_result(4832844, limit=limit)
        rows = [
            [
                row["buy_time"],
                a_tag_link(row["kol_with_link"]),
                strip_a_tag(row["token_with_chart"]),
                strip_a_tag(row["contract_with_chart"]),
                f'${row["amount_usd"]:.2f}'
            ]
            for row in data
        ]
        headers = ["Time", "KOL", "Token", "Mint Address", "Amount"]
        return f"# Recent {limit} Buys by Memecoin KOLs\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_trending_tokens_by_kol_trading_volume(limit: int = 100) -> str:
    """Retrieve tokens with the highest trading volume by memecoin KOLs.

    Args:
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of trending tokens by KOL trading volume including
            token name, mint address, unique KOL buys, total buys, and total volume,
            or an error message if the query fails.

    Raises:
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    try:
        data = get_latest_result(4838351, limit=limit)
        rows = [
            [
                row["token"],
                row["contract_address"],
                row["unique_kols"],
                row["total_buys"],
                f'${row["total_volume"]:.2f}'
            ]
            for row in data
        ]
        headers = ["Token", "Mint Address", "Unique KOL Buys", "Total Buys", "Total Volume"]
        return f"# Top {limit} Trending Tokens by KOL Trading Volume\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_trending_tokens_on_raydium(time_span: str = "5h", limit: int = 100) -> str:
    """Retrieve tokens with the highest trading volume on Raydium within a specified time span.

    Args:
        time_span (str): Time period for the query. Must be one of: '5h', '12h', '24h'.
            Defaults to '5h'.
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of trending tokens on Raydium including token name,
            mint address, and trading volume, or an error message if the query fails.

    Raises:
        ValueError: If an invalid time_span value is provided.
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    query_ids = {
        "5h": 4840714,
        "12h": 4840651, 
        "24h": 4840709,
    }
    try:
        query_id = query_ids.get(time_span)
        if query_id is None:
            raise ValueError("Invalid time_span value. Allowed: 5h | 12h | 24h")
        data = get_latest_result(query_id, limit=limit)
        rows = [
            [
                strip_a_tag(row["asset_with_chart"]),
                row["token_address"],
                f'${row.get(f"total_volume_{time_span}", 0):.2f}'
            ]
            for row in data
        ]
        headers = ["Token", "Mint Address", "Volume"]
        return f"# Top {limit} Trending Tokens on Raydium - Last {time_span}\n\n" + tabulate(rows, headers=headers) 
    except Exception as e:
        return str(e)
    
@mcp.tool()
def get_trending_tokens_on_pumpswap(time_span: str = "5h", limit: int = 100) -> str:
    """Retrieve tokens with the highest trading volume on PumpSwap within a specified time span.

    Args:
        time_span (str): Time period for the query. Must be one of: '5h', '12h', '24h'.
            Defaults to '5h'.
        limit (int): Maximum number of tokens to return. Defaults to 100.

    Returns:
        str: A formatted table of trending tokens on PumpSwap including mint address
            and trading volume, or an error message if the query fails.

    Raises:
        ValueError: If an invalid time_span value is provided.
        httpx.HTTPStatusError: If the Dune API request fails.
    """
    query_ids = {
        "5h": 4929624,
        "12h": 4929617,
        "24h": 4929607,
    }
    try:
        query_id = query_ids.get(time_span)
        if query_id is None:
            raise ValueError("Invalid time_span value. Allowed: 5h | 12h | 24h")
        data = get_latest_result(query_id, limit=limit)
        rows = [
            [
                strip_a_tag(row["contract_address"]),
                f'${row["volume_usd"]:.2f}'
            ]
            for row in data
        ]
        headers = ["Mint Address", "Trading Volume"]
        return f"# Top {limit} Trending Tokens on PumpSwap - Last {time_span}\n\n" + tabulate(rows, headers=headers)
    except Exception as e:
        return str(e)  
    
# Run the server
if __name__ == "__main__":
    mcp.run()