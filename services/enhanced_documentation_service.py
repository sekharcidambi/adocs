#!/usr/bin/env python3
"""
Enhanced Documentation Service with Custom Section Injection.
"""

import logging
from typing import Dict, Any, Optional, List
from .base_service import BaseService
from .storage_service import CloudStorageService
from .config_service import ConfigService, RepositoryConfig, CustomSection, InjectionStrategy

logger = logging.getLogger(__name__)

class EnhancedDocumentationService(BaseService):
    """Enhanced service for retrieving documentation with custom section injection."""
    
    def __init__(self, gcs_bucket: str = None, custom_docs_bucket: str = None):
        """
        Initialize the Enhanced Documentation Service.
        
        Args:
            gcs_bucket: Main GCS bucket for generated docs
            custom_docs_bucket: GCS bucket for custom docs
        """
        super().__init__()
        
        # Initialize services
        self.storage_service = CloudStorageService(bucket_name=gcs_bucket)
        self.config_service = ConfigService()
        
        # Custom docs bucket (can be different from main bucket)
        self.custom_docs_bucket = custom_docs_bucket or self.config_service.get_custom_docs_bucket()
        if self.custom_docs_bucket != gcs_bucket:
            self.custom_storage_service = CloudStorageService(bucket_name=self.custom_docs_bucket)
        else:
            self.custom_storage_service = self.storage_service
    
    def get_documentation(self, repo_url: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get complete documentation with custom section injection.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Enhanced documentation data with custom sections
        """
        try:
            logger.info(f"Getting enhanced documentation for repo: {repo_url}, type: {docs_type}")
            
            # Get base documentation
            base_result = self._get_base_documentation(repo_url, docs_type)
            if not base_result.get('success', False):
                return base_result
            
            # Assign default priorities to generated sections
            base_result = self._assign_default_priorities(base_result)
            
            # Get repository configuration
            repo_config = self.config_service.get_repository_config(repo_url)
            
            # Inject custom sections if configuration exists
            if repo_config and repo_config.enabled and self.config_service.is_custom_sections_enabled():
                enhanced_result = self._inject_custom_sections(base_result, repo_config, docs_type)
                return enhanced_result
            
            # Return base documentation if no custom configuration
            return base_result
            
        except Exception as e:
            logger.error(f"Error getting enhanced documentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    def get_documentation_section(self, repo_url: str, section: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get a specific documentation section with custom section support.
        
        Args:
            repo_url: GitHub repository URL
            section: Section name
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Section documentation data
        """
        try:
            logger.info(f"Getting enhanced documentation section: {repo_url}/{section}")
            
            # Check if this is a custom section
            repo_config = self.config_service.get_repository_config(repo_url)
            if repo_config and repo_config.enabled:
                custom_section = self._find_custom_section(repo_config, section)
                if custom_section:
                    return self._get_custom_section_content(repo_url, custom_section, docs_type)
            
            # Fallback to regular section retrieval
            return self._get_regular_section_content(repo_url, section, docs_type)
            
        except Exception as e:
            logger.error(f"Error getting enhanced documentation section: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url,
                "section": section
            }
    
    def _get_base_documentation(self, repo_url: str, docs_type: str) -> Dict[str, Any]:
        """Get base documentation from the main storage service."""
        try:
            # Get documentation structure
            doc_structure = self.storage_service.get_documentation_structure(repo_url, docs_type)
            if not doc_structure:
                return {
                    "success": False,
                    "error": "Documentation not found in GCS",
                    "repository": repo_url
                }
            
            # Get repository metadata
            metadata = self.storage_service.get_repository_metadata(repo_url, docs_type)
            
            # Build navigation structure
            navigation = self._build_navigation_structure(doc_structure)
            
            return {
                "success": True,
                "repository": repo_url,
                "documentationStructure": doc_structure,
                "metadata": metadata,
                "navigation": navigation,
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting base documentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    def _inject_custom_sections(self, base_result: Dict[str, Any], repo_config: RepositoryConfig, docs_type: str) -> Dict[str, Any]:
        """Inject custom sections into the base documentation."""
        try:
            logger.info(f"Injecting custom sections for repository: {repo_config.repo_url}")
            
            # Get custom section contents
            custom_sections = []
            for custom_section in repo_config.custom_sections:
                if not custom_section.enabled:
                    continue
                
                section_content = self._get_custom_section_content(
                    repo_config.repo_url, custom_section, docs_type
                )
                
                if section_content.get('success', False):
                    custom_sections.append({
                        "title": custom_section.name,  # Use 'title' for documentation structure
                        "name": custom_section.name,   # Keep 'name' for compatibility
                        "content": section_content.get('content', ''),
                        "description": custom_section.description,
                        "icon": custom_section.icon,
                        "priority": custom_section.priority,
                        "is_custom": True,
                        "gcs_path": custom_section.gcs_path
                    })
                elif not self.config_service.should_fallback_to_generated():
                    logger.warning(f"Custom section not found and fallback disabled: {custom_section.name}")
            
            # Apply injection strategy
            injection_strategy = self.config_service.get_injection_strategy()
            enhanced_result = self._apply_injection_strategy(
                base_result, custom_sections, injection_strategy
            )
            
            # Add custom metadata
            if repo_config.custom_metadata:
                enhanced_result["custom_metadata"] = repo_config.custom_metadata
            
            # Add injection metadata
            enhanced_result["injection_info"] = {
                "strategy": injection_strategy.value,
                "custom_sections_count": len(custom_sections),
                "custom_docs_bucket": self.custom_docs_bucket
            }
            
            logger.info(f"Successfully injected {len(custom_sections)} custom sections")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error injecting custom sections: {e}")
            return base_result  # Return base result on error
    
    def _apply_injection_strategy(self, base_result: Dict[str, Any], custom_sections: List[Dict], strategy: InjectionStrategy) -> Dict[str, Any]:
        """Apply the injection strategy to combine base and custom sections."""
        enhanced_result = base_result.copy()
        
        if strategy == InjectionStrategy.REPLACE:
            # Replace generated sections with custom ones
            enhanced_result["documentationStructure"]["sections"] = custom_sections
            enhanced_result["navigation"] = self._build_custom_navigation(custom_sections)
        
        elif strategy == InjectionStrategy.PREPEND:
            # Add custom sections at the beginning
            existing_sections = enhanced_result.get("documentationStructure", {}).get("sections", [])
            enhanced_result["documentationStructure"]["sections"] = custom_sections + existing_sections
            enhanced_result["navigation"] = self._build_combined_navigation(custom_sections, existing_sections)
        
        elif strategy == InjectionStrategy.APPEND:
            # Add custom sections at the end
            existing_sections = enhanced_result.get("documentationStructure", {}).get("sections", [])
            enhanced_result["documentationStructure"]["sections"] = existing_sections + custom_sections
            enhanced_result["navigation"] = self._build_combined_navigation(existing_sections, custom_sections)
        
        elif strategy == InjectionStrategy.MERGE:
            # Merge custom sections with existing ones (by name)
            existing_sections = enhanced_result.get("documentationStructure", {}).get("sections", [])
            merged_sections = self._merge_sections(existing_sections, custom_sections)
            enhanced_result["documentationStructure"]["sections"] = merged_sections
            enhanced_result["navigation"] = self._build_combined_navigation(merged_sections, [])
        
        return enhanced_result
    
    def _get_custom_section_content(self, repo_url: str, custom_section: CustomSection, docs_type: str) -> Dict[str, Any]:
        """Get content for a custom section from GCS."""
        try:
            # Use custom storage service for custom docs with raw file content
            content = self.custom_storage_service.get_raw_file_content(
                custom_section.gcs_path
            )
            
            if content:
                return {
                    "success": True,
                    "content": content,
                    "section": custom_section.name,
                    "repository": repo_url,
                    "is_custom": True,
                    "gcs_path": custom_section.gcs_path
                }
            else:
                return {
                    "success": False,
                    "error": f"Custom section content not found: {custom_section.gcs_path}",
                    "section": custom_section.name,
                    "repository": repo_url
                }
                
        except Exception as e:
            logger.error(f"Error getting custom section content: {e}")
            return {
                "success": False,
                "error": str(e),
                "section": custom_section.name,
                "repository": repo_url
            }
    
    def _find_custom_section(self, repo_config: RepositoryConfig, section_name: str) -> Optional[CustomSection]:
        """Find a custom section by name."""
        for custom_section in repo_config.custom_sections:
            if custom_section.name.lower() == section_name.lower():
                return custom_section
        return None
    
    def _get_regular_section_content(self, repo_url: str, section: str, docs_type: str) -> Dict[str, Any]:
        """Get content for a regular (non-custom) section."""
        try:
            filename = f"{self._sanitize_filename(section)}.md"
            content = self.storage_service.get_markdown_file(repo_url, filename, docs_type)
            
            if content:
                return {
                    "success": True,
                    "content": content,
                    "section": section,
                    "repository": repo_url,
                    "is_custom": False
                }
            else:
                return {
                    "success": False,
                    "error": f"Section '{section}' not found",
                    "repository": repo_url,
                    "section": section
                }
                
        except Exception as e:
            logger.error(f"Error getting regular section content: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url,
                "section": section
            }
    
    def _build_custom_navigation(self, custom_sections: List[Dict]) -> List[Dict]:
        """Build navigation structure from custom sections."""
        navigation = []
        for section in custom_sections:
            navigation.append({
                "title": section["name"],
                "description": section.get("description", ""),
                "icon": section.get("icon", "📄"),
                "priority": section.get("priority", 1),
                "is_custom": True
            })
        return sorted(navigation, key=lambda x: x.get("priority", 1))
    
    def _build_combined_navigation(self, sections1: List[Dict], sections2: List[Dict]) -> List[Dict]:
        """Build combined navigation from two section lists."""
        all_sections = sections1 + sections2
        
        # Sort by priority (lower number = higher priority)
        def get_priority(section):
            priority = section.get("priority")
            if priority is None:
                return 999  # Put sections without priority at the end
            return priority
        
        return sorted(all_sections, key=get_priority)
    
    def _merge_sections(self, existing_sections: List[Dict], custom_sections: List[Dict]) -> List[Dict]:
        """Merge custom sections with existing sections by priority."""
        # Combine all sections
        all_sections = existing_sections + custom_sections
        
        # Sort by priority (lower number = higher priority)
        # Sections with null/None priority go to the end
        def get_priority(section):
            priority = section.get("priority")
            if priority is None:
                return 999  # Put sections without priority at the end
            return priority
        
        all_sections.sort(key=get_priority)
        return all_sections
    
    def _assign_default_priorities(self, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assign default priorities to generated sections."""
        try:
            sections = base_result.get("documentationStructure", {}).get("sections", [])
            
            # Define default priorities for common section titles
            default_priorities = {
                "apache ofbiz overview": 1,
                "framework architecture": 3,
                "plugin system and extensibility": 4,
                "installation and setup": 5,
                "development guide": 6,
                "enterprise process automation": 7,
                "community and contribution": 8,
                "deployment and operations": 9
            }
            
            # Assign priorities to sections
            for i, section in enumerate(sections):
                if section.get("priority") is None:
                    title = section.get("title", "").lower()
                    if title in default_priorities:
                        section["priority"] = default_priorities[title]
                    else:
                        # Assign a default priority based on position
                        section["priority"] = 10 + i
            
            # Update the result
            base_result["documentationStructure"]["sections"] = sections
            
            # Also update navigation if it exists
            if "navigation" in base_result:
                base_result["navigation"] = sections  # Navigation uses the same structure
            
            return base_result
            
        except Exception as e:
            logger.error(f"Error assigning default priorities: {e}")
            return base_result
    
    def _build_navigation_structure(self, doc_structure: Dict[str, Any]) -> List[Dict]:
        """Build navigation structure from documentation structure."""
        # This would be implemented based on your existing navigation logic
        # For now, return a simple structure
        sections = doc_structure.get("sections", [])
        navigation = []
        
        for i, section in enumerate(sections):
            navigation.append({
                "title": section.get("name", f"Section {i+1}"),
                "description": section.get("description", ""),
                "icon": section.get("icon", "📄"),
                "priority": i + 1,
                "is_custom": False
            })
        
        return navigation
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for storage."""
        import re
        # Remove invalid characters and replace with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        return sanitized.strip('_')
