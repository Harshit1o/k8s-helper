"""
Configuration management for k8s-helper
"""

import os
from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class K8sConfig:
    """Configuration class for k8s-helper"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self._config = self._load_config()
    
    def _get_default_config_file(self) -> str:
        """Get the default config file path"""
        home_dir = Path.home()
        return str(home_dir / ".k8s-helper" / "config.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'default_namespace': 'default',
            'output_format': 'table',  # table, yaml, json
            'timeout': 300,
            'auto_wait': True,
            'verbose': False,
            'kube_config_path': None,  # Use default kubectl config
            'contexts': {}
        }
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self._config[key] = value
    
    def get_namespace(self) -> str:
        """Get the default namespace"""
        return self.get('default_namespace', 'default')
    
    def set_namespace(self, namespace: str) -> None:
        """Set the default namespace"""
        self.set('default_namespace', namespace)
    
    def get_output_format(self) -> str:
        """Get the output format"""
        return self.get('output_format', 'table')
    
    def set_output_format(self, format_type: str) -> None:
        """Set the output format"""
        if format_type in ['table', 'yaml', 'json']:
            self.set('output_format', format_type)
        else:
            raise ValueError("Output format must be 'table', 'yaml', or 'json'")
    
    def get_timeout(self) -> int:
        """Get the default timeout"""
        return self.get('timeout', 300)
    
    def set_timeout(self, timeout: int) -> None:
        """Set the default timeout"""
        self.set('timeout', timeout)
    
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled"""
        return self.get('verbose', False)
    
    def set_verbose(self, verbose: bool) -> None:
        """Set verbose mode"""
        self.set('verbose', verbose)
    
    def get_kube_config_path(self) -> Optional[str]:
        """Get the kubectl config path"""
        return self.get('kube_config_path')
    
    def set_kube_config_path(self, path: str) -> None:
        """Set the kubectl config path"""
        self.set('kube_config_path', path)
    
    def add_context(self, name: str, namespace: str, cluster: str = None) -> None:
        """Add a context configuration"""
        contexts = self.get('contexts', {})
        contexts[name] = {
            'namespace': namespace,
            'cluster': cluster
        }
        self.set('contexts', contexts)
    
    def get_context(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a context configuration"""
        contexts = self.get('contexts', {})
        return contexts.get(name)
    
    def list_contexts(self) -> Dict[str, Any]:
        """List all configured contexts"""
        return self.get('contexts', {})
    
    def remove_context(self, name: str) -> bool:
        """Remove a context configuration"""
        contexts = self.get('contexts', {})
        if name in contexts:
            del contexts[name]
            self.set('contexts', contexts)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Get the full configuration as a dictionary"""
        return self._config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = self._get_default_config()


# Global configuration instance
_global_config = None


def get_config() -> K8sConfig:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = K8sConfig()
    return _global_config


def set_config_file(config_file: str) -> None:
    """Set a custom config file path"""
    global _global_config
    _global_config = K8sConfig(config_file)


# Environment variable overrides
def get_env_override(key: str, default: Any = None) -> Any:
    """Get configuration from environment variables"""
    env_mapping = {
        'default_namespace': 'K8S_HELPER_NAMESPACE',
        'output_format': 'K8S_HELPER_OUTPUT_FORMAT',
        'timeout': 'K8S_HELPER_TIMEOUT',
        'verbose': 'K8S_HELPER_VERBOSE',
        'kube_config_path': 'KUBECONFIG'
    }
    
    env_key = env_mapping.get(key)
    if env_key and env_key in os.environ:
        value = os.environ[env_key]
        
        # Convert string values to appropriate types
        if key == 'timeout':
            try:
                return int(value)
            except ValueError:
                return default
        elif key == 'verbose':
            return value.lower() in ('true', '1', 'yes', 'on')
        else:
            return value
    
    return default


def load_config_with_env_overrides() -> Dict[str, Any]:
    """Load configuration with environment variable overrides"""
    config = get_config()
    
    # Apply environment overrides
    for key in ['default_namespace', 'output_format', 'timeout', 'verbose', 'kube_config_path']:
        env_value = get_env_override(key)
        if env_value is not None:
            config.set(key, env_value)
    
    return config.to_dict()
