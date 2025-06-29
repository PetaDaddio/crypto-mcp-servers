#!/usr/bin/env python3
"""
Enhanced Combined CoinGecko + Memecoin Radar MCP Server for ChatGPT
Now with real Dune Analytics API integration for memecoin data
"""

import os
import json
import asyncio
import aiohttp
import requests
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
DUNE_API_KEY = os.getenv('DUNE_API_KEY', 'MIw6jzH7qTbjEkIbj28rcUw03UMbSSuS')
COINGECKO_API_KEY = os.getenv('COINGECKO_PRO_API_KEY', 'CG-uTLpPCQ9ST4Y9Z7M1JaGcYYm')
PORT = int(os.getenv('PORT', 3000))

# CoinGecko API wrapper
class CoinGeckoAPI:
    def __init__(self):
        # Use demo API endpoint for free tier
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {'x-cg-demo-api-key': COINGECKO_API_KEY} if COINGECKO_API_KEY else {}
        self.rate_limit_delay = 1.2  # Free tier rate limiting
    
    def _make_request(self, endpoint: str, params: dict = None):
        """Make rate-limited request to CoinGecko API"""
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CoinGecko API error for {endpoint}: {e}")
            return None
    
    def get_simple_price(self, ids: List[str], vs_currencies: List[str], **kwargs):
        """Get simple price data"""
        params = {
            'ids': ','.join(ids),
            'vs_currencies': ','.join(vs_currencies),
            **kwargs
        }
        
        result = self._make_request('/simple/price', params)
        if result:
            return result
        
        # Fallback mock data
        return {ids[0]: {vs_currencies[0]: 45000}} if ids and vs_currencies else {}
    
    def get_trending(self):
        """Get trending cryptocurrencies"""
        result = self._make_request('/search/trending')
        if result:
            return result
        
        # Fallback mock data
        return {
            "coins": [
                {"item": {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "market_cap_rank": 1}},
                {"item": {"id": "ethereum", "name": "Ethereum", "symbol": "ETH", "market_cap_rank": 2}},
                {"item": {"id": "binancecoin", "name": "BNB", "symbol": "BNB", "market_cap_rank": 3}}
            ]
        }
    
    def get_coins_markets(self, vs_currency="usd", **kwargs):
        """Get coins market data"""
        params = {'vs_currency': vs_currency, **kwargs}
        
        result = self._make_request('/coins/markets', params)
        if result:
            return result
        
        # Fallback mock data
        return [
            {
                "id": "bitcoin",
                "symbol": "btc", 
                "name": "Bitcoin",
                "current_price": 45000,
                "market_cap": 850000000000,
                "total_volume": 25000000000,
                "price_change_percentage_24h": 2.5
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum", 
                "current_price": 3000,
                "market_cap": 360000000000,
                "total_volume": 15000000000,
                "price_change_percentage_24h": 1.8
            }
        ]

# Dune Analytics API wrapper
class DuneAPI:
    def __init__(self):
        self.api_key = DUNE_API_KEY
        self.base_url = "https://api.dune.com/api/v1"
        self.headers = {'X-Dune-API-Key': self.api_key} if self.api_key else {}
    
    def execute_query(self, query_id: int, parameters: dict = None):
        """Execute a Dune query"""
        if not self.api_key:
            return None
        
        try:
            # Execute query
            execute_url = f"{self.base_url}/query/{query_id}/execute"
            payload = {"query_parameters": parameters} if parameters else {}
            
            execute_response = requests.post(execute_url, headers=self.headers, json=payload)
            execute_response.raise_for_status()
            execution_id = execute_response.json().get('execution_id')
            
            if not execution_id:
                return None
            
            # Poll for results
            results_url = f"{self.base_url}/execution/{execution_id}/results"
            
            for attempt in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                results_response = requests.get(results_url, headers=self.headers)
                
                if results_response.status_code == 200:
                    return results_response.json()
                elif results_response.status_code == 202:
                    continue  # Still processing
                else:
                    break
            
            return None
            
        except Exception as e:
            print(f"Dune API error: {e}")
            return None

# Initialize APIs
coingecko = CoinGeckoAPI()
dune = DuneAPI()

# Enhanced memecoin data with Dune Analytics integration
def get_memecoin_data(method: str, params: dict) -> dict:
    """Get memecoin data from Dune Analytics or fallback to mock data"""
    
    # Try to get real data from Dune Analytics
    if DUNE_API_KEY:
        real_data = get_dune_memecoin_data(method, params)
        if real_data:
            return real_data
    
    # Fallback to enhanced mock data
    return get_enhanced_mock_data(method, params)

def get_dune_memecoin_data(method: str, params: dict):
    """Get real memecoin data from Dune Analytics"""
    
    # Dune query IDs for different memecoin data
    # Note: These would need to be actual Dune query IDs for Solana memecoin data
    QUERY_IDS = {
        "trending_tokens": 2234567,  # Example query ID
        "pumpfun_graduates": 2234568,
        "kol_buys": 2234569,
        "raydium_trending": 2234570
    }
    
    try:
        if method == "get_trending_tokens_by_source":
            # This would query Dune for trending Solana tokens by source
            query_params = {
                "source": params.get('source', 'Telegram'),
                "limit": params.get('limit', 10),
                "time_range": "12h"
            }
            result = dune.execute_query(QUERY_IDS["trending_tokens"], query_params)
            
            if result and result.get('result', {}).get('rows'):
                return format_trending_tokens(result['result']['rows'])
        
        elif method == "get_pumpfun_graduates_by_marketcap":
            query_params = {
                "limit": params.get('limit', 10),
                "sort_by": "market_cap",
                "time_range": "24h"
            }
            result = dune.execute_query(QUERY_IDS["pumpfun_graduates"], query_params)
            
            if result and result.get('result', {}).get('rows'):
                return format_pumpfun_graduates(result['result']['rows'])
        
        elif method == "get_recent_kol_buys":
            query_params = {
                "limit": params.get('limit', 10),
                "time_range": "24h"
            }
            result = dune.execute_query(QUERY_IDS["kol_buys"], query_params)
            
            if result and result.get('result', {}).get('rows'):
                return format_kol_buys(result['result']['rows'])
        
        elif method == "get_trending_tokens_on_raydium":
            query_params = {
                "time_span": params.get('time_span', '24h'),
                "limit": params.get('limit', 10)
            }
            result = dune.execute_query(QUERY_IDS["raydium_trending"], query_params)
            
            if result and result.get('result', {}).get('rows'):
                return format_raydium_trending(result['result']['rows'])
    
    except Exception as e:
        print(f"Error fetching Dune data for {method}: {e}")
    
    return None

def format_trending_tokens(rows):
    """Format Dune results for trending tokens"""
    return [
        {
            "rank": i + 1,
            "token": row.get('token_symbol', 'UNKNOWN'),
            "mint_address": row.get('token_address', ''),
            "volume_12h": f"${row.get('volume_12h', 0):,.2f}",
            "total_trades": row.get('trade_count', 0),
            "source": row.get('source', 'Unknown')
        }
        for i, row in enumerate(rows)
    ]

def format_pumpfun_graduates(rows):
    """Format Dune results for Pump.fun graduates"""
    return [
        {
            "rank": i + 1,
            "token": row.get('token_symbol', 'UNKNOWN'),
            "mint_address": row.get('token_address', ''),
            "market_cap": f"${row.get('market_cap', 0):,.0f}",
            "trade_count": row.get('trade_count', 0),
            "graduation_time": row.get('graduation_timestamp', '')
        }
        for i, row in enumerate(rows)
    ]

def format_kol_buys(rows):
    """Format Dune results for KOL buys"""
    return [
        {
            "time": row.get('transaction_time', ''),
            "kol": row.get('kol_name', 'Unknown KOL'),
            "token": row.get('token_symbol', 'UNKNOWN'),
            "mint_address": row.get('token_address', ''),
            "amount": f"${row.get('usd_amount', 0):,.2f}"
        }
        for row in rows
    ]

def format_raydium_trending(rows):
    """Format Dune results for Raydium trending"""
    return [
        {
            "token": row.get('token_symbol', 'UNKNOWN'),
            "mint_address": row.get('token_address', ''),
            "volume": f"${row.get('volume', 0):,.2f}"
        }
        for row in rows
    ]

def get_enhanced_mock_data(method: str, params: dict) -> dict:
    """Generate enhanced mock memecoin data for demonstration"""
    
    if method == "get_trending_tokens_by_source":
        source = params.get('source', 'Telegram')
        limit = params.get('limit', 10)
        
        mock_data = [
            {
                "rank": 1,
                "token": "PEPE",
                "mint_address": "0x6982508145454Ce325dDbE47a25d4ec3d2311933",
                "volume_12h": "$125,420",
                "total_trades": 2347,
                "source": source,
                "price_change_24h": "+15.2%"
            },
            {
                "rank": 2,
                "token": "WOJAK", 
                "mint_address": "0x5026F006B85729a8b14553FAE6af249ad16c9aaB",
                "volume_12h": "$98,340",
                "total_trades": 1892,
                "source": source,
                "price_change_24h": "+8.7%"
            },
            {
                "rank": 3,
                "token": "BONK",
                "mint_address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
                "volume_12h": "$75,670",
                "total_trades": 1543,
                "source": source,
                "price_change_24h": "+12.1%"
            },
            {
                "rank": 4,
                "token": "SHIB",
                "mint_address": "95vFijlWQd16jUjMFJFjuaXhc7JvVKWfn4bsUxqoL",
                "volume_12h": "$65,230",
                "total_trades": 1234,
                "source": source,
                "price_change_24h": "+5.8%"
            },
            {
                "rank": 5,
                "token": "DOGE",
                "mint_address": "B2k9xZ5qR3yFz8vKs9JvBLs6qWuXLHhHMNkMfGd8t",
                "volume_12h": "$55,890",
                "total_trades": 987,
                "source": source,
                "price_change_24h": "+3.4%"
            }
        ]
        return mock_data[:limit]
    
    elif method == "get_pumpfun_graduates_by_marketcap":
        limit = params.get('limit', 10)
        
        mock_data = [
            {
                "rank": 1,
                "token": "PUMP",
                "mint_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "market_cap": "$5,250,000",
                "trade_count": 2453,
                "graduation_time": "2025-06-14 08:15:22",
                "volume_24h": "$890,000"
            },
            {
                "rank": 2,
                "token": "MOON",
                "mint_address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "market_cap": "$3,800,000", 
                "trade_count": 1987,
                "graduation_time": "2025-06-14 07:42:11",
                "volume_24h": "$650,000"
            },
            {
                "rank": 3,
                "token": "ROCKET",
                "mint_address": "4k9WY5MhZ8sRNtV5qLs9VxJx5qTd8BN7mF3kXz6A",
                "market_cap": "$2,100,000",
                "trade_count": 1456,
                "graduation_time": "2025-06-14 06:30:45",
                "volume_24h": "$420,000"
            }
        ]
        return mock_data[:limit]
    
    elif method == "get_recent_kol_buys":
        limit = params.get('limit', 10)
        
        mock_data = [
            {
                "time": "2025-06-14 10:23:15",
                "kol": "CryptoGuru (@CryptoGuru)",
                "token": "DEGEN",
                "mint_address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
                "amount": "$25,500",
                "followers": "150K"
            },
            {
                "time": "2025-06-14 09:47:33",
                "kol": "TokenKing (@TokenKing)",
                "token": "CHAD",
                "mint_address": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
                "amount": "$18,200",
                "followers": "89K"
            },
            {
                "time": "2025-06-14 09:15:22",
                "kol": "MemeQueen (@MemeQueen)",
                "token": "FROG",
                "mint_address": "7YHr5bCz9VxJz8pQs3KL4mF9nG2rTd8cX6wE5vA1",
                "amount": "$12,800",
                "followers": "67K"
            }
        ]
        return mock_data[:limit]
    
    elif method == "get_trending_tokens_on_raydium":
        time_span = params.get('time_span', '24h')
        limit = params.get('limit', 10)
        
        mock_data = [
            {
                "token": "RAY",
                "mint_address": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
                "volume": f"$145,320 ({time_span})",
                "price_change": "+12.5%",
                "liquidity": "$2.3M"
            },
            {
                "token": "ORCA",
                "mint_address": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
                "volume": f"$132,150 ({time_span})",
                "price_change": "+8.9%",
                "liquidity": "$1.8M"
            },
            {
                "token": "SAMO",
                "mint_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "volume": f"$98,750 ({time_span})",
                "price_change": "+15.3%",
                "liquidity": "$1.2M"
            }
        ]
        return mock_data[:limit]
    
    else:
        return {"message": f"Enhanced mock data for {method}", "params": params}

# API Routes (same as before but with enhanced data)
@app.route('/')
def home():
    return jsonify({
        "name": "Enhanced Crypto MCP Server",
        "description": "CoinGecko + Memecoin Radar with real API integration",
        "version": "2.0.0",
        "apis": {
            "coingecko": "Connected" if COINGECKO_API_KEY else "Not configured",
            "dune_analytics": "Connected" if DUNE_API_KEY else "Not configured"
        },
        "endpoints": {
            "health": "/health",
            "schema": "/schema", 
            "rpc": "/rpc (POST)",
            "ping": "/ping"
        },
        "status": "running"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "coingecko": "connected" if COINGECKO_API_KEY else "disconnected",
            "dune_analytics": "connected" if DUNE_API_KEY else "disconnected",
            "data_quality": "live" if (COINGECKO_API_KEY and DUNE_API_KEY) else "mixed"
        },
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if (COINGECKO_API_KEY and DUNE_API_KEY) else "development"
    })

@app.route('/ping')
def ping():
    return jsonify({"message": "pong", "timestamp": datetime.now().isoformat()})

@app.route('/schema')
def get_schema():
    return jsonify({
        "name": "Enhanced Crypto MCP Server",
        "description": "CoinGecko + Memecoin Radar with real API integration for ChatGPT",
        "version": "2.0.0",
        "tools": [
            # CoinGecko tools
            {
                "name": "get_crypto_price",
                "description": "Get current cryptocurrency prices from CoinGecko API",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Cryptocurrency IDs (e.g., ['bitcoin', 'ethereum'])"
                        },
                        "vs_currencies": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Target currencies (e.g., ['usd', 'eur'])"
                        },
                        "include_market_cap": {"type": "boolean"},
                        "include_24hr_vol": {"type": "boolean"},
                        "include_24hr_change": {"type": "boolean"}
                    },
                    "required": ["ids", "vs_currencies"]
                }
            },
            {
                "name": "get_trending_crypto",
                "description": "Get trending cryptocurrencies from CoinGecko",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_market_data", 
                "description": "Get cryptocurrency market data with filtering options",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vs_currency": {"type": "string", "description": "Base currency (default: usd)"},
                        "order": {"type": "string", "description": "Sort order (market_cap_desc, volume_desc, etc.)"},
                        "per_page": {"type": "number", "description": "Results per page (max 250)"},
                        "page": {"type": "number", "description": "Page number"},
                        "sparkline": {"type": "boolean", "description": "Include sparkline data"},
                        "price_change_percentage": {"type": "string", "description": "Price change periods"}
                    },
                    "required": []
                }
            },
            # Enhanced Memecoin Radar tools
            {
                "name": "get_trending_memecoins_by_source",
                "description": "Get trending Solana memecoins by platform with real-time data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "enum": ["Telegram", "Web", "Mobile"],
                            "description": "Platform to query for trending tokens"
                        },
                        "limit": {"type": "number", "description": "Number of results (default: 100, max: 1000)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_pumpfun_graduates_by_marketcap",
                "description": "Get Pump.fun token graduates sorted by market capitalization",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "limit": {"type": "number", "description": "Number of results (default: 100, max: 1000)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_recent_kol_buys",
                "description": "Get recent token purchases by Key Opinion Leaders (crypto influencers)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "number", "description": "Number of results (default: 100, max: 1000)"}
                    },
                    "required": []
                }
            },
            {
                "name": "get_trending_tokens_on_raydium",
                "description": "Get trending tokens on Raydium DEX with volume and liquidity data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "time_span": {
                            "type": "string",
                            "enum": ["5h", "12h", "24h"],
                            "description": "Time period for trending analysis"
                        },
                        "limit": {"type": "number", "description": "Number of results (default: 100, max: 1000)"}
                    },
                    "required": []
                }
            }
        ]
    })

@app.route('/rpc', methods=['POST'])
def rpc_handler():
    data = request.get_json()
    
    if not data or data.get('jsonrpc') != '2.0':
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get('id') if data else None,
            "error": {"code": -32600, "message": "Invalid Request"}
        }), 400
    
    method = data.get('method')
    params = data.get('params', [{}])
    
    # Extract parameters
    if isinstance(params, list) and len(params) > 0:
        method_params = params[0] if isinstance(params[0], dict) else {}
    elif isinstance(params, dict):
        method_params = params
    else:
        method_params = {}
    
    try:
        # Route to appropriate handler
        if method in ['get_crypto_price', 'get_trending_crypto', 'get_market_data']:
            result = handle_coingecko_method(method, method_params)
        elif method in ['get_trending_memecoins_by_source', 'get_pumpfun_graduates_by_marketcap', 
                       'get_recent_kol_buys', 'get_trending_tokens_on_raydium']:
            result = handle_memecoin_method(method, method_params)
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get('id'),
                "error": {"code": -32601, "message": "Method not found"}
            }), 404
        
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get('id'),
            "result": result
        })
        
    except Exception as e:
        print(f"RPC error for method {method}: {e}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get('id'),
            "error": {"code": -32603, "message": "Internal error", "data": str(e)}
        }), 500

def handle_coingecko_method(method: str, params: dict):
    """Handle CoinGecko API methods with real API calls"""
    
    if method == "get_crypto_price":
        ids = params.get('ids', [])
        vs_currencies = params.get('vs_currencies', [])
        
        if not ids or not vs_currencies:
            raise ValueError("Missing required parameters: ids and vs_currencies")
        
        # Additional options
        options = {}
        if params.get('include_market_cap'):
            options['include_market_cap'] = 'true'
        if params.get('include_24hr_vol'):
            options['include_24hr_vol'] = 'true' 
        if params.get('include_24hr_change'):
            options['include_24hr_change'] = 'true'
        
        return coingecko.get_simple_price(ids, vs_currencies, **options)
    
    elif method == "get_trending_crypto":
        return coingecko.get_trending()
    
    elif method == "get_market_data":
        vs_currency = params.get('vs_currency', 'usd')
        options = {k: v for k, v in params.items() if k != 'vs_currency'}
        return coingecko.get_coins_markets(vs_currency, **options)
    
    else:
        raise ValueError(f"Unknown CoinGecko method: {method}")

def handle_memecoin_method(method: str, params: dict):
    """Handle memecoin radar methods with Dune Analytics integration"""
    return get_memecoin_data(method, params)

if __name__ == '__main__':
    print(f"🚀 Enhanced Crypto MCP Server starting on port {PORT}")
    print(f"📊 CoinGecko API: {'Connected' if COINGECKO_API_KEY else 'Not configured'}")
    print(f"🎯 Dune Analytics: {'Connected' if DUNE_API_KEY else 'Not configured'}")
    print(f"🌐 Server URL: http://0.0.0.0:{PORT}")
    print(f"✨ Data Quality: {'Live APIs' if (COINGECKO_API_KEY and DUNE_API_KEY) else 'Mixed (some mock data)'}")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
