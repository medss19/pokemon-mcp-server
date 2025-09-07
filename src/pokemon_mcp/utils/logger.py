# src/pokemon_mcp/utils/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional

class PokemonLogger:
    """Centralized logging setup for Pokemon MCP Server"""
    
    _loggers = {}
    
    @classmethod
    def setup_logger(cls, name: str, level: str = "INFO", 
                    log_file: Optional[str] = None, 
                    log_format: str = None) -> logging.Logger:
        """Setup and return a configured logger"""
        
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        if log_format is None:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get existing logger or create with default settings"""
        if name in cls._loggers:
            return cls._loggers[name]
        return cls.setup_logger(name)