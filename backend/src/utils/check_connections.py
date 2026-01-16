#!/usr/bin/env python3
"""
CryptoPulse - Script para verificar conexões com serviços
Uso: python -m src.utils.check_connections
"""

import asyncio
import sys
from datetime import datetime

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    print(f"""
{Colors.BLUE}╔═══════════════════════════════════════════════════════════╗
║       🔍 CryptoPulse - Connection Checker                   ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
""")


def print_result(service: str, success: bool, message: str = ""):
    status = f"{Colors.GREEN}✅ OK{Colors.END}" if success else f"{Colors.RED}❌ FALHOU{Colors.END}"
    print(f"  {service:.<40} {status}")
    if message and not success:
        print(f"     {Colors.YELLOW}└─ {message}{Colors.END}")


async def check_postgres():
    """Verifica conexão com PostgreSQL"""
    try:
        import asyncpg
        from src.config.settings import settings
        
        db_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = await asyncpg.connect(db_url)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        
        return True, f"PostgreSQL {version.split(',')[0].replace('PostgreSQL ', '')}"
    except Exception as e:
        return False, str(e)


async def check_redis():
    """Verifica conexão com Redis"""
    try:
        import redis.asyncio as redis
        from src.config.settings import settings
        
        client = redis.from_url(settings.redis_url)
        pong = await client.ping()
        info = await client.info("server")
        await client.aclose()  # Corrigido: usar aclose() ao invés de close()
        
        return True, f"Redis {info.get('redis_version', 'unknown')}"
    except Exception as e:
        return False, str(e)


async def check_binance_api():
    """Verifica acesso à API da Binance"""
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.binance.com/api/v3/ping")
            
            if response.status_code == 200:
                ticker = await client.get(
                    "https://api.binance.com/api/v3/ticker/price",
                    params={"symbol": "BTCUSDT"}
                )
                if ticker.status_code == 200:
                    price = ticker.json().get("price", "N/A")
                    return True, f"BTC/USDT: ${float(price):,.2f}"
        
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)


async def check_coingecko_api():
    """Verifica acesso à API do CoinGecko"""
    try:
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.coingecko.com/api/v3/ping")
            
            if response.status_code == 200:
                return True, "API disponível"
        
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, str(e)


async def main():
    print_header()
    print(f"  {Colors.BLUE}Timestamp:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(f"  {Colors.BOLD}📦 Infraestrutura Local:{Colors.END}")
    
    success, msg = await check_postgres()
    print_result("PostgreSQL", success, msg)
    
    success, msg = await check_redis()
    print_result("Redis", success, msg)
    
    print()
    
    print(f"  {Colors.BOLD}🌐 APIs Externas:{Colors.END}")
    
    success, msg = await check_binance_api()
    print_result("Binance API", success, msg)
    
    success, msg = await check_coingecko_api()
    print_result("CoinGecko API", success, msg)
    
    print()
    print(f"  {Colors.BLUE}─────────────────────────────────────────────{Colors.END}")
    print()


if __name__ == "__main__":
    sys.path.insert(0, str(__file__).replace("/src/utils/check_connections.py", ""))
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n  Verificação cancelada.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {Colors.RED}Erro: {e}{Colors.END}")
        sys.exit(1)
