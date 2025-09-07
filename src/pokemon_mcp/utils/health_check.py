# src/pokemon_mcp/utils/health_check.py
import time
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class HealthStatus:
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: Optional[float]
    error: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class HealthChecker:
    """Health check system for monitoring dependencies"""
    
    def __init__(self, config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=5.0)
        
    async def check_pokeapi(self) -> HealthStatus:
        """Check if PokeAPI is accessible"""
        start_time = time.time()
        
        try:
            response = await self.client.get(f"{self.config.pokeapi_base_url}/pokemon/1")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return HealthStatus(
                    service="pokeapi",
                    status="healthy",
                    response_time_ms=response_time
                )
            else:
                return HealthStatus(
                    service="pokeapi",
                    status="degraded",
                    response_time_ms=response_time,
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            return HealthStatus(
                service="pokeapi",
                status="unhealthy",
                response_time_ms=None,
                error=str(e)
            )
    
    async def check_cache(self) -> HealthStatus:
        """Check cache system health"""
        from ..data.cache import PokemonCache
        
        try:
            cache = PokemonCache(self.config.cache_directory)
            # Try a simple cache operation
            await cache.set("health_check", {"test": True})
            result = await cache.get("health_check")
            
            if result and result.get("test"):
                return HealthStatus(
                    service="cache",
                    status="healthy",
                    response_time_ms=0
                )
            else:
                return HealthStatus(
                    service="cache",
                    status="degraded",
                    response_time_ms=0,
                    error="Cache read/write failed"
                )
                
        except Exception as e:
            return HealthStatus(
                service="cache",
                status="unhealthy",
                response_time_ms=None,
                error=str(e)
            )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        checks = [
            self.check_pokeapi(),
            self.check_cache()
        ]
        
        results = []
        for check in checks:
            try:
                result = await check
                results.append(asdict(result))
            except Exception as e:
                results.append({
                    "service": "unknown",
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time()
                })
        
        # Determine overall status
        statuses = [r["status"] for r in results]
        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "timestamp": time.time(),
            "checks": results,
            "version": self.config.server_version
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()