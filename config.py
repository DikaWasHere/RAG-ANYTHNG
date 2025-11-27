"""
Configuration management untuk RAG system
Centralized config untuk easy tuning
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ModelConfig:
    """Model configuration"""
    # Embedding
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    embedding_max_tokens: int = 512
    embedding_batch_size: int = 32
    
    # LLM
    llm_model: str = "openai/gpt-4o-mini"
    vision_model: str = "openai/gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_timeout: int = 60
    
    # API
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

@dataclass
class RAGConfig:
    """RAG system configuration"""
    working_dir: str = "./rag_storage"
    output_dir: str = "./output"
    parser: str = "mineru"
    parse_method: str = "auto"
    
    # Processing flags
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True
    
    # Query settings
    default_query_mode: str = "hybrid"
    top_k: int = 5
    enable_rerank: bool = False

@dataclass
class CacheConfig:
    """Cache configuration"""
    enable_embedding_cache: bool = True
    enable_query_cache: bool = True
    enable_llm_cache: bool = True
    
    # Cache sizes (LRU)
    embedding_cache_size: int = 1000
    query_cache_size: int = 100
    llm_cache_size: int = 500
    
    # TTL in seconds
    cache_ttl: int = 3600  # 1 hour

@dataclass
class PerformanceConfig:
    """Performance & monitoring configuration"""
    enable_monitoring: bool = True
    enable_profiling: bool = False
    log_queries: bool = True
    
    # Timeouts
    query_timeout: int = 120
    preprocessing_timeout: int = 600
    
    # Concurrency
    max_concurrent_queries: int = 5
    max_concurrent_embeddings: int = 10

class Config:
    """Master configuration"""
    def __init__(self):
        self.model = ModelConfig()
        self.rag = RAGConfig()
        self.cache = CacheConfig()
        self.performance = PerformanceConfig()
    
    def to_dict(self):
        """Convert config to dictionary"""
        return {
            "model": self.model.__dict__,
            "rag": self.rag.__dict__,
            "cache": self.cache.__dict__,
            "performance": self.performance.__dict__,
        }
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        config = cls()
        
        # Override dari environment jika ada
        if os.getenv("LLM_MODEL"):
            config.model.llm_model = os.getenv("LLM_MODEL")
        if os.getenv("VISION_MODEL"):
            config.model.vision_model = os.getenv("VISION_MODEL")
        if os.getenv("WORKING_DIR"):
            config.rag.working_dir = os.getenv("WORKING_DIR")
            
        return config

# Global config instance
CONFIG = Config.from_env()
