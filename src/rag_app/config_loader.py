"""
TOML-based configuration loader
"""
import os
import tomli
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration manager using TOML"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config.toml file
        """
        if config_path is None:
            # Look for config.toml in current directory or project root
            current_dir = Path.cwd()
            project_root = Path(__file__).parent.parent.parent
            
            if (current_dir / "config.toml").exists():
                config_path = current_dir / "config.toml"
            elif (project_root / "config.toml").exists():
                config_path = project_root / "config.toml"
            else:
                raise FileNotFoundError(
                    "config.toml not found. Please create one in the project root."
                )
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        with open(self.config_path, "rb") as f:
            return tomli.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'milvus.host')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section
        
        Args:
            section: Section name (e.g., 'milvus')
            
        Returns:
            Section dictionary
        """
        return self._config.get(section, {})
    
    @property
    def app(self):
        """App configuration"""
        return self.get_section('app')
    
    @property
    def milvus(self):
        """Milvus configuration"""
        return self.get_section('milvus')
    
    @property
    def embedding(self):
        """Embedding configuration"""
        return self.get_section('embedding')
    
    @property
    def ollama(self):
        """Ollama configuration"""
        return self.get_section('ollama')
    
    @property
    def document_processing(self):
        """Document processing configuration"""
        return self.get_section('document_processing')
    
    @property
    def retrieval(self):
        """Retrieval configuration"""
        return self.get_section('retrieval')
    
    @property
    def server(self):
        """Server configuration"""
        return self.get_section('server')
    
    @property
    def paths(self):
        """Paths configuration"""
        return self.get_section('paths')
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()


# Global configuration instance
_config = None


def get_config(config_path: str = None) -> Config:
    """
    Get global configuration instance
    
    Args:
        config_path: Path to config file (only used on first call)
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config():
    """Reload global configuration"""
    global _config
    if _config is not None:
        _config.reload()

# Made with Bob
