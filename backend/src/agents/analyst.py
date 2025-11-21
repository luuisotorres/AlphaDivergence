import os
import requests
import time
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

class AnalystAgent:
    def __init__(self, etherscan_api_key: str = None):
        self.name = "The Analyst"
        # Priority: Passed key → Environment variable
        self.etherscan_api_key = etherscan_api_key or os.getenv("ETHERSCAN_API_KEY")

    def _fetch_dexscreener_data(self, token_symbol: str):
        """Fetches real-time data from DexScreener."""
        logger.info(f"[{self.name}] Querying DexScreener for ${token_symbol}...")
        
        try:
            url = f"https://api.dexscreener.com/latest/dex/search?q={token_symbol}"
            response = requests.get(url)
            data = response.json()
            
            if not data.get("pairs"):
                logger.warning(f"[{self.name}] No pairs found for {token_symbol}.")
                return None

            # Prioritize Ethereum pairs for whale tracking
            eth_pair = None
            highest_liquidity_pair = None
            
            for pair in data["pairs"]:
                if pair.get("chainId") == "ethereum":
                    if not eth_pair or pair.get("liquidity", {}).get("usd", 0) > eth_pair.get("liquidity", {}).get("usd", 0):
                        eth_pair = pair
                
                if not highest_liquidity_pair or pair.get("liquidity", {}).get("usd", 0) > highest_liquidity_pair.get("liquidity", {}).get("usd", 0):
                    highest_liquidity_pair = pair
            
            # Use Ethereum pair if available, otherwise use highest liquidity
            pair = eth_pair if eth_pair else highest_liquidity_pair
            
            logger.info(f"[{self.name}] Selected pair: {pair.get('chainId')} (Liquidity: ${pair.get('liquidity', {}).get('usd', 0):,.0f})")
            
            return {
                "chain_id": pair.get("chainId"),
                "pair_address": pair.get("pairAddress"),
                "base_token_address": pair.get("baseToken", {}).get("address"),
                "price_usd": float(pair.get("priceUsd", 0)),
                "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
                "volume_24h": pair.get("volume", {}).get("h24", 0),
                "fdv": pair.get("fdv", 0),
                "pair_url": pair.get("url"),
                "txns_24h": pair.get("txns", {}).get("h24", {})
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error fetching DexScreener data: {e}")
            return None

    def _fetch_etherscan_whales(self, token_address: str, pair_address: str, price_usd: float):
        """
        Fetches recent transfers from Etherscan to detect Whale Buys/Sells.
        """
        if not self.etherscan_api_key:
            logger.warning(f"[{self.name}] Etherscan API Key missing. Skipping Whale Tracking.")
            return None

        logger.info(f"[{self.name}] Fetching Etherscan data for Whale Tracking...")
        
        try:
            # Use V2 API endpoint
            url = "https://api.etherscan.io/v2/api"
            params = {
                "chainid": 1,  # Ethereum mainnet
                "module": "account",
                "action": "tokentx",
                "contractaddress": token_address,
                "page": 1,
                "offset": 100,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] != "1":
                logger.error(f"[{self.name}] Etherscan Error: {data.get('message')} - {data.get('result')}")
                return None

            whale_buys = 0
            whale_sells = 0
            whale_tx_count = 0
            
            WHALE_THRESHOLD_USD = 100000 # Define a whale as > $100k trade

            for tx in data["result"]:
                # Check if interaction is with the Liquidity Pool (Pair Address)
                is_buy = tx["from"].lower() == pair_address.lower()
                is_sell = tx["to"].lower() == pair_address.lower()
                
                if not (is_buy or is_sell):
                    continue # Ignore transfers between wallets

                amount = float(tx["value"]) / (10 ** int(tx["tokenDecimal"]))
                value_usd = amount * price_usd
                
                if value_usd > WHALE_THRESHOLD_USD:
                    whale_tx_count += 1
                    if is_buy:
                        whale_buys += value_usd
                    else:
                        whale_sells += value_usd

            return {
                "whale_buys_usd": whale_buys,
                "whale_sells_usd": whale_sells,
                "whale_tx_count": whale_tx_count
            }

        except Exception as e:
            logger.error(f"[{self.name}] Error analyzing Etherscan data: {e}")
            return None

    def analyze_onchain_data(self, token_symbol: str):
        """
        Queries DexScreener and optionally Etherscan for Smart Money tracking.
        """
        logger.info(f"[{self.name}] Checking on-chain data for {token_symbol}...")
        
        dex_data = self._fetch_dexscreener_data(token_symbol)
        
        if not dex_data:
            return {
                "token": token_symbol,
                "net_smart_money_flow": "Unknown",
                "whale_concentration": 0,
                "details": {"error": "Token not found on DexScreener"}
            }
        
        # Default Flow Signal (Volume Proxy)
        buys = dex_data["txns_24h"].get("buys", 0)
        sells = dex_data["txns_24h"].get("sells", 0)
        volume = dex_data["volume_24h"]
        
        net_flow_signal = "Neutral"
        net_flow_usd = 0
        
        whale_data = None
        tracking_type = "Volume Analysis"
        
        # If Ethereum, try True Whale Tracking
        if dex_data["chain_id"] == "ethereum":
            whale_data = self._fetch_etherscan_whales(
                dex_data["base_token_address"], 
                dex_data["pair_address"], 
                dex_data["price_usd"]
            )
            if whale_data:
                tracking_type = "Deep Whale Analysis"
            
        if whale_data and whale_data["whale_tx_count"] > 0:
            # Override with True Whale Data
            net_flow_usd = whale_data["whale_buys_usd"] - whale_data["whale_sells_usd"]
            
            if net_flow_usd > 50000:
                net_flow_signal = "Whale Buy"
            elif net_flow_usd < -50000:
                net_flow_signal = "Whale Sell"
            else:
                net_flow_signal = "Neutral"
        else:
            # Fallback to Volume Proxy 2.0 (Estimated Flow)
            total_txns = buys + sells
            if total_txns > 0:
                avg_tx_value = volume / total_txns
                net_txns = buys - sells
                net_flow_usd = net_txns * avg_tx_value
                
                # More sensitive thresholds (1.1x instead of 1.2x)
                if buys > sells * 1.1:
                    net_flow_signal = "Buy Pressure"
                elif sells > buys * 1.1:
                    net_flow_signal = "Sell Pressure"
            else:
                net_flow_usd = 0

        return {
            "token": token_symbol,
            "net_smart_money_flow": net_flow_signal,
            "whale_concentration": 0, 
            "details": {
                "price": dex_data["price_usd"],
                "liquidity": dex_data["liquidity_usd"],
                "volume_24h": dex_data["volume_24h"],
                "fdv": dex_data["fdv"],
                "pair_url": dex_data["pair_url"],
                "whale_data": whale_data,
                "chain_id": dex_data["chain_id"],
                "tracking_type": tracking_type,
                "net_flow_usd": int(net_flow_usd) # Ensure it's sent to frontend
            }
        }
