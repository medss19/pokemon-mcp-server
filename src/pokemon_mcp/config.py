# src/pokemon_mcp/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    # API Configuration
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    request_timeout: int = 10
    max_retries: int = 3
    
    # Cache Configuration
    cache_duration: int = 3600  # 1 hour
    cache_directory: str = "cache"
    memory_cache_size: int = 1000
    
    # Battle Configuration
    max_battle_turns: int = 200
    battle_timeout: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server Configuration
    server_name: str = "pokemon-battle-server"
    server_version: str = "1.0.0"
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Load configuration from environment variables"""
        return cls(
            pokeapi_base_url=os.getenv('POKEAPI_BASE_URL', cls.pokeapi_base_url),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', cls.request_timeout)),
            max_retries=int(os.getenv('MAX_RETRIES', cls.max_retries)),
            cache_duration=int(os.getenv('CACHE_DURATION', cls.cache_duration)),
            cache_directory=os.getenv('CACHE_DIRECTORY', cls.cache_directory),
            memory_cache_size=int(os.getenv('MEMORY_CACHE_SIZE', cls.memory_cache_size)),
            max_battle_turns=int(os.getenv('MAX_BATTLE_TURNS', cls.max_battle_turns)),
            battle_timeout=int(os.getenv('BATTLE_TIMEOUT', cls.battle_timeout)),
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', cls.rate_limit_per_minute)),
            rate_limit_burst=int(os.getenv('RATE_LIMIT_BURST', cls.rate_limit_burst)),
            log_level=os.getenv('LOG_LEVEL', cls.log_level),
            log_file=os.getenv('LOG_FILE'),
            server_name=os.getenv('SERVER_NAME', cls.server_name),
            server_version=os.getenv('SERVER_VERSION', cls.server_version),
        )