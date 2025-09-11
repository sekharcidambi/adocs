#!/usr/bin/env python3
"""
Configuration Service for ADocS - Manages repository-specific configurations.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class InjectionStrategy(Enum):
    """Strategy for injecting custom sections."""
    PREPEND = "prepend"  # Add custom sections at the beginning
    APPEND = "append"    # Add custom sections at the end
    REPLACE = "replace"  # Replace generated sections with custom ones
    MERGE = "merge"      # Merge custom sections with generated ones

@dataclass
class CustomSection:
    """Represents a custom section configuration."""
    name: str
    gcs_path: str
    priority: int = 1
    description: str = ""
    icon: str = "📄"
    enabled: bool = True

@dataclass
class RepositoryConfig:
    """Represents repository-specific configuration."""
    repo_url: str
    custom_sections: List[CustomSection]
    gcs_path_override: Optional[str] = None
    custom_metadata: Dict[str, Any] = None
    enabled: bool = True

class ConfigService:
    """Service for managing repository configurations."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Configuration Service.
        
        Args:
            config_path: Path to the configuration file
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'repository_config.yaml')
        
        self.config_path = Path(config_path)
        self._config_cache = None
        self._last_modified = None
        
        logger.info(f"ConfigService initialized with config: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with caching."""
        try:
            # Check if file exists
            if not self.config_path.exists():
                logger.warning(f"Configuration file not found: {self.config_path}")
                return self._get_default_config()
            
            # Check if file has been modified
            current_mtime = self.config_path.stat().st_mtime
            if (self._config_cache is not None and 
                self._last_modified is not None and 
                current_mtime <= self._last_modified):
                return self._config_cache
            
            # Load configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Cache the configuration
            self._config_cache = config
            self._last_modified = current_mtime
            
            logger.info(f"Configuration loaded from: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file is not available."""
        return {
            "repositories": {},
            "global_config": {
                "custom_docs_bucket": "adocs-custom-docs",
                "fallback_to_generated": True,
                "cache_ttl": 3600,
                "enable_custom_sections": True,
                "injection_strategy": "prepend"
            },
            "section_templates": {}
        }
    
    def get_repository_config(self, repo_url: str) -> Optional[RepositoryConfig]:
        """
        Get configuration for a specific repository.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            RepositoryConfig or None if not found
        """
        try:
            config = self._load_config()
            repositories = config.get('repositories', {})
            
            # Look for exact match first
            if repo_url in repositories:
                repo_config = repositories[repo_url]
                return self._parse_repository_config(repo_url, repo_config)
            
            # Look for pattern matching (e.g., wildcards)
            for pattern, repo_config in repositories.items():
                if self._matches_pattern(repo_url, pattern):
                    return self._parse_repository_config(repo_url, repo_config)
            
            logger.debug(f"No custom configuration found for repository: {repo_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting repository config for {repo_url}: {e}")
            return None
    
    def _parse_repository_config(self, repo_url: str, config: Dict[str, Any]) -> RepositoryConfig:
        """Parse repository configuration from YAML."""
        custom_sections = []
        
        # Parse custom sections
        sections_config = config.get('custom_sections', [])
        for section_config in sections_config:
            section = CustomSection(
                name=section_config.get('name', ''),
                gcs_path=section_config.get('gcs_path', ''),
                priority=section_config.get('priority', 1),
                description=section_config.get('description', ''),
                icon=section_config.get('icon', '📄'),
                enabled=section_config.get('enabled', True)
            )
            custom_sections.append(section)
        
        # Sort sections by priority
        custom_sections.sort(key=lambda x: x.priority)
        
        return RepositoryConfig(
            repo_url=repo_url,
            custom_sections=custom_sections,
            gcs_path_override=config.get('gcs_path_override'),
            custom_metadata=config.get('custom_metadata', {}),
            enabled=config.get('enabled', True)
        )
    
    def _matches_pattern(self, repo_url: str, pattern: str) -> bool:
        """Check if repository URL matches a pattern."""
        # Simple pattern matching - can be extended for more complex patterns
        if '*' in pattern:
            # Convert wildcard pattern to regex
            import re
            regex_pattern = pattern.replace('*', '.*')
            return bool(re.match(regex_pattern, repo_url))
        
        return repo_url == pattern
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        config = self._load_config()
        return config.get('global_config', {})
    
    def get_section_templates(self) -> Dict[str, Any]:
        """Get section templates."""
        config = self._load_config()
        return config.get('section_templates', {})
    
    def is_custom_sections_enabled(self) -> bool:
        """Check if custom sections are enabled globally."""
        global_config = self.get_global_config()
        return global_config.get('enable_custom_sections', True)
    
    def get_injection_strategy(self) -> InjectionStrategy:
        """Get the injection strategy."""
        global_config = self.get_global_config()
        strategy = global_config.get('injection_strategy', 'prepend')
        try:
            return InjectionStrategy(strategy)
        except ValueError:
            logger.warning(f"Invalid injection strategy: {strategy}, using prepend")
            return InjectionStrategy.PREPEND
    
    def get_custom_docs_bucket(self) -> str:
        """Get the custom docs bucket name."""
        global_config = self.get_global_config()
        return global_config.get('custom_docs_bucket', 'adocs-custom-docs')
    
    def should_fallback_to_generated(self) -> bool:
        """Check if should fallback to generated sections when custom ones are not found."""
        global_config = self.get_global_config()
        return global_config.get('fallback_to_generated', True)
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL for custom sections."""
        global_config = self.get_global_config()
        return global_config.get('cache_ttl', 3600)
    
    def reload_config(self):
        """Force reload configuration from file."""
        self._config_cache = None
        self._last_modified = None
        logger.info("Configuration reloaded")
    
    def validate_config(self) -> List[str]:
        """
        Validate the configuration file.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            config = self._load_config()
            
            # Validate repositories
            repositories = config.get('repositories', {})
            for repo_url, repo_config in repositories.items():
                # Validate required fields
                if 'custom_sections' in repo_config:
                    for i, section in enumerate(repo_config['custom_sections']):
                        if not section.get('name'):
                            errors.append(f"Repository {repo_url}: Section {i} missing name")
                        if not section.get('gcs_path'):
                            errors.append(f"Repository {repo_url}: Section {i} missing gcs_path")
            
            # Validate global config
            global_config = config.get('global_config', {})
            valid_strategies = [s.value for s in InjectionStrategy]
            if global_config.get('injection_strategy') not in valid_strategies:
                errors.append(f"Invalid injection_strategy: {global_config.get('injection_strategy')}")
            
        except Exception as e:
            errors.append(f"Configuration validation error: {e}")
        
        return errors
