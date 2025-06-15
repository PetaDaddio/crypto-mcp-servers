# Memecoin Radar MCP

Real-time radar for Solana memecoins, Pump.fun launches, and KOL trades.

![GitHub License](https://img.shields.io/github/license/kukapay/memecoin-radar-mcp) 
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## Features

- **Trending Tokens by Source**: Retrieve top-traded tokens on platforms like Telegram, Web, or Mobile over the last 12 hours.
- **Pump.fun Graduates**: Track tokens launched on Pump.fun, sorted by market capitalization or trading volume, and view recent graduates.
- **KOL Activity**: Monitor recent buys and trending tokens by memecoin influencers (KOLs).
- **Raydium & PumpSwap Trends**: Analyze tokens with the highest trading volume on Raydium and PumpSwap over customizable time spans (5h, 12h, 24h).
- **Customizable Limits**: Configure the number of results returned for each query (default: 100).
- **Formatted Output**: Results are presented in clean, tabular format using the `tabulate` library.

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended package manager)
- A Dune Analytics API key (obtainable from [Dune Analytics](https://dune.com))

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/kukapay/memecoin-radar-mcp.git
   cd memecoin-radar-mcp
   ```

2. **Install Dependencies**

   ```bash
   uv sync  
   ```

3. **Installing to Claude Desktop**:

    Install the server as a Claude Desktop application:
    ```bash
    uv run mcp install main.py --name "Memcoin Radar"
    ```

    Configuration file as a reference:

    ```json
    {
       "mcpServers": {
           "Memecoin Radar": {
               "command": "uv",
               "args": [ "--directory", "/path/to/memecoin-radar-mcp", "run", "main.py" ],
               "env": { "DUNE_API_KEY": "dune_api_key"}               
           }
       }
    }
    ```
    Replace `/path/to/memecoin-radar-mcp` with your actual installation path, and `dune_api_key` with your API key from Dune Analytics.

## Usage

Below is a detailed description of each tool, including its purpose, a natural language prompt example, and a sample table output.

### `get_trending_tokens_by_source`

**Description**: Retrieves the top traded tokens on a specified platform (Telegram, Web, or Mobile) over the last 12 hours. Useful for identifying trending memecoins by platform.

**Parameters**:
- `source` (str): Platform to query ('Telegram', 'Web', or 'Mobile'). Default: 'Telegram'.
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "Show me the top 3 trending tokens on Telegram in the last 12 hours."
- **Output**:
```
# Top 3 Trending Tokens on Telegram - Last 12 Hours

Rank  Token    Mint Address                                Volume(12h)  Total Trades
----  -------  ------------------------------------------  -----------  ------------
1     MOON     0x1234abcd5678efgh9012ijkl3456mnop7890       $10000.00            150
2     STAR     0x5678efgh9012ijkl3456mnop7890qrst1234       $7500.00             120
3     RISE     0x9abc3456mnop7890qrst1234uvwx5678yzab       $5000.00              80
```

### `get_pumpfun_graduates_by_marketcap`

**Description**: Lists Pump.fun tokens with the highest market capitalization in the last 24 hours, ideal for spotting successful token launches.

**Parameters**:
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "List the top 3 Pump.fun tokens by market cap in the last 24 hours."
- **Output**:
```
# Top 3 Pump.fun Graduates by MarketCap - Last 24 Hours

Rank  Token    Mint Address                                MarketCap    Trade Count
----  -------  ------------------------------------------  -----------  -----------
1     PUMP     0x1234abcd5678efgh9012ijkl3456mnop7890      $500000.00           200
2     BUMP     0x5678efgh9012ijkl3456mnop7890qrst1234      $400000.00           180
3     JUMP     0x9abc3456mnop7890qrst1234uvwx5678yzab      $300000.00           150
```

### `get_pumpfun_graduates_by_trading_volume`

**Description**: Shows Pump.fun tokens with the highest trading volume in the last 24 hours, highlighting active trading tokens.

**Parameters**:
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "Show the top 3 Pump.fun tokens by trading volume in the last 24 hours."
- **Output**:
```
# Top 3 Pump.fun Graduates by Trading Volume - Last 24 Hours

Rank  Token    Mint Address                                Volume(12h)  Graduation Time
----  -------  ------------------------------------------  -----------  ---------------
1     VOLT     0x1234abcd5678efgh9012ijkl3456mnop7890      $20000.00    2025-06-14 10:00
2     SPARK    0x5678efgh9012ijkl3456mnop7890qrst1234      $15000.00    2025-06-14 09:30
3     BLAZE    0x9abc3456mnop7890qrst1234uvwx5678yzab      $10000.00    2025-06-14 08:45
```

### `get_recent_pumpfun_graduates`

**Description**: Displays the most recently graduated Pump.fun tokens in the last 24 hours, useful for tracking new market entries.

**Parameters**:
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "Get the 3 most recent Pump.fun graduates."
- **Output**:
```
# Recent 3 Pump.fun Graduates - Last 24 Hours

Graduation Time      Token    Mint Address                                Market Cap   Trade Count
-------------------  -------  ------------------------------------------  ----------   -----------
2025-06-14 12:00     NEW1     0x1234abcd5678efgh9012ijkl3456mnop7890      $250000.00          100
2025-06-14 11:30     NEW2     0x5678efgh9012ijkl3456mnop7890qrst1234      $200000.00           90
2025-06-14 11:00     NEW3     0x9abc3456mnop7890qrst1234uvwx5678yzab      $150000.00           80
```

### `get_recent_kol_buys`

**Description**: Tracks recent token purchases by memecoin Key Opinion Leaders (KOLs), providing insights into influencer activity.

**Parameters**:
- `limit` (int): Maximum number of buy transactions to return. Default: 100.

**Example**:
- **Prompt**: "Show the 3 most recent KOL buys."
- **Output**:
```
# Recent 3 Buys by Memecoin KOLs

Time                 KOL       Token    Mint Address                                Amount
-------------------  --------  -------  ------------------------------------------  --------
2025-06-14 10:00     CryptoGuru  KOL1   0x1234abcd5678efgh9012ijkl3456mnop7890      $5000.00
2025-06-14 09:45     MoonKing    KOL2   0x5678efgh9012ijkl3456mnop7890qrst1234      $3000.00
2025-06-14 09:30     TokenStar   KOL3   0x9abc3456mnop7890qrst1234uvwx5678yzab      $2000.00
```

### `get_trending_tokens_by_kol_trading_volume`

**Description**: Lists tokens with the highest trading volume by KOLs, highlighting influencer-driven market trends.

**Parameters**:
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "List the top 3 tokens by KOL trading volume."
- **Output**:
```
# Top 3 Trending Tokens by KOL Trading Volume

Token    Mint Address                                Unique KOL Buys  Total Buys  Total Volume
-------  ------------------------------------------  --------------  ----------  ------------
KOL1     0x1234abcd5678efgh9012ijkl3456mnop7890                5            50     $25000.00
KOL2     0x5678efgh9012ijkl3456mnop7890qrst1234                4            40     $18000.00
KOL3     0x9abc3456mnop7890qrst1234uvwx5678yzab                3            30     $12000.00
```

### `get_trending_tokens_on_raydium`

**Description**: Retrieves tokens with the highest trading volume on Raydium over a specified time span (5h, 12h, or 24h).

**Parameters**:
- `time_span` (str): Time period ('5h', '12h', or '24h'). Default: '5h'.
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "Show the top 3 trending tokens on Raydium in the last 24 hours."
- **Output**:
```
# Top 3 Trending Tokens on Raydium - Last 24h

Token    Mint Address                                Volume
-------  ------------------------------------------  --------
RAY1     0x1234abcd5678efgh9012ijkl3456mnop7890      $30000.00
RAY2     0x5678efgh9012ijkl3456mnop7890qrst1234      $25000.00
RAY3     0x9abc3456mnop7890qrst1234uvwx5678yzab      $20000.00
```

### `get_trending_tokens_on_pumpswap`

**Description**: Retrieves tokens with the highest trading volume on PumpSwap over a specified time span (5h, 12h, or 24h).

**Parameters**:
- `time_span` (str): Time period ('5h', '12h', or '24h'). Default: '5h'.
- `limit` (int): Maximum number of tokens to return. Default: 100.

**Example**:
- **Prompt**: "Get the top 3 trending tokens on PumpSwap in the last 12 hours."
- **Output**:
```
# Top 3 Trending Tokens on PumpSwap - Last 12h

Mint Address                                Trading Volume
------------------------------------------  --------------
0x1234abcd5678efgh9012ijkl3456mnop7890      $15000.00
0x5678efgh9012ijkl3456mnop7890qrst1234      $12000.00
0x9abc3456mnop7890qrst1234uvwx5678yzab      $10000.00
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

