"""AI-powered summary generator for configuration elements."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Callable, TYPE_CHECKING, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from .llm_client import LLMClient, LLMConfig
from .prompts import (
    SYSTEM_OVERVIEW_PROMPT,
    CATEGORY_PROMPT,
    WORKFLOW_PROMPT,
    ROLE_PROMPT,
    EFORM_PROMPT,
    DICTIONARY_PROMPT,
    format_system_overview_context,
    format_category_context,
    format_workflow_context,
    format_role_context,
    format_eform_context,
    format_dictionary_context
)

if TYPE_CHECKING:
    from ..parser.models import Configuration, Category, WorkflowProcess, Role, EForm, KeywordDictionary


# Cache directory for AI summaries
CACHE_DIR = Path.home() / '.cache' / 'therefore-processor' / 'ai-summaries'


class AISummaryGenerator:
    """Generates AI-powered summaries for configuration elements with fallback support."""

    def __init__(self, llm_configs: Union[LLMConfig, List[LLMConfig]]):
        """Initialize summary generator with one or more LLM configurations.

        Args:
            llm_configs: Single LLMConfig or list of LLMConfigs (tried in order with fallback)
        """
        # Support both single config and list of configs
        if isinstance(llm_configs, LLMConfig):
            llm_configs = [llm_configs]

        self.clients = [LLMClient(config) for config in llm_configs]
        self.configs = llm_configs
        self._cache: Dict[str, str] = {}

        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _generate_cache_key(xml_content: str) -> str:
        """Generate cache key from XML content hash.

        Args:
            xml_content: Raw XML content string

        Returns:
            SHA256 hash of the content
        """
        return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given cache key.

        Args:
            cache_key: Cache key (hash)

        Returns:
            Path to cache file
        """
        return CACHE_DIR / f"{cache_key}.json"

    def load_from_cache(self, xml_content: str) -> Optional[Dict]:
        """Load summaries from cache if available.

        Args:
            xml_content: Raw XML content string

        Returns:
            Cached summaries dict or None if not found
        """
        cache_key = self._generate_cache_key(xml_content)
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Log cache hit
                generated_at = cache_data.get('generated_at', 'unknown')
                provider = cache_data.get('llm_provider', 'unknown')
                model = cache_data.get('llm_model', 'unknown')

                print("=" * 60)
                print("✓ AI Summary Cache Hit!")
                print(f"  Generated: {generated_at}")
                print(f"  Provider: {provider}")
                print(f"  Model: {model}")
                print(f"  Cache file: {cache_path.name}")
                print("=" * 60)

                return cache_data.get('summaries')
            except Exception as e:
                print(f"Failed to load cache: {e}")
                return None

        return None

    def save_to_cache(self, xml_content: str, summaries: Dict) -> None:
        """Save summaries to cache.

        Args:
            xml_content: Raw XML content string
            summaries: Generated summaries dict
        """
        cache_key = self._generate_cache_key(xml_content)
        cache_path = self._get_cache_path(cache_key)

        # Detect which provider was used (assume primary if successful)
        provider = "Unknown"
        model = "Unknown"
        if self.configs:
            config = self.configs[0]
            provider = "Azure OpenAI" if "azure.com" in config.base_url.lower() else \
                      "Ollama" if "11434" in config.base_url else "Local LLM"
            model = config.model_name

        cache_data = {
            'generated_at': datetime.now().isoformat(),
            'xml_hash': cache_key,
            'llm_provider': provider,
            'llm_model': model,
            'summaries': summaries
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)

            print(f"✓ Saved AI summaries to cache: {cache_path.name}")
        except Exception as e:
            print(f"Failed to save cache: {e}")

    @staticmethod
    def clear_cache() -> int:
        """Clear all cached summaries.

        Returns:
            Number of cache files deleted
        """
        count = 0
        if CACHE_DIR.exists():
            for cache_file in CACHE_DIR.glob('*.json'):
                try:
                    cache_file.unlink()
                    count += 1
                except Exception as e:
                    print(f"Failed to delete {cache_file}: {e}")

        print(f"✓ Cleared {count} cached summary file(s)")
        return count

    def test_connection(self) -> tuple[bool, str]:
        """Test LLM connection (tests primary LLM only).

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.clients:
            return False, "No LLM configured"
        return self.clients[0].test_connection()

    def _generate_with_fallback(self, system_prompt: str, user_prompt: str, operation_name: str = "") -> Optional[str]:
        """Try to generate completion with automatic fallback to next LLM if one fails.

        Args:
            system_prompt: System message defining behavior
            user_prompt: User message with content to summarize
            operation_name: Name of operation for logging

        Returns:
            Generated text or None if all LLMs failed
        """
        for i, client in enumerate(self.clients, 1):
            try:
                # Detect provider name for logging
                config = self.configs[i-1]
                provider = "Azure OpenAI" if "azure.com" in config.base_url.lower() else \
                           "Ollama" if "11434" in config.base_url else \
                           "Local LLM" if "localhost" in config.base_url or "127.0.0.1" in config.base_url else \
                           "Custom LLM"

                if i > 1:
                    print(f"  → Falling back to LLM #{i} ({provider})...")

                result = client.generate_completion(system_prompt, user_prompt)

                if result:
                    if i == 1:
                        # Success on primary LLM - no need to log
                        pass
                    else:
                        print(f"  ✓ Success with LLM #{i} ({provider})")
                    return result

            except Exception as e:
                print(f"  ✗ LLM #{i} failed: {str(e)}")
                continue

        print(f"  ✗ All {len(self.clients)} LLM(s) failed for {operation_name}")
        return None

    def generate_system_overview(
        self,
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate system-wide overview summary.

        Args:
            config: Full configuration object
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = "system_overview"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback("Generating system overview...")

        context = format_system_overview_context(config)
        summary = self._generate_with_fallback(
            SYSTEM_OVERVIEW_PROMPT,
            context,
            "system overview"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_category_summary(
        self,
        category: 'Category',
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate summary for a category.

        Args:
            category: Category to summarize
            config: Configuration object for cross-references
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = f"category_{category.category_no}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback(f"Summarizing category: {category.name}...")

        context = format_category_context(category, config)
        summary = self._generate_with_fallback(
            CATEGORY_PROMPT,
            context,
            f"category {category.name}"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_workflow_summary(
        self,
        workflow: 'WorkflowProcess',
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate summary for a workflow.

        Args:
            workflow: Workflow to summarize
            config: Configuration object for cross-references
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = f"workflow_{workflow.process_no}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback(f"Summarizing workflow: {workflow.name}...")

        context = format_workflow_context(workflow, config)
        summary = self._generate_with_fallback(
            WORKFLOW_PROMPT,
            context,
            f"workflow {workflow.name}"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_role_summary(
        self,
        role: 'Role',
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate summary for a role.

        Args:
            role: Role to summarize
            config: Configuration object for cross-references
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = f"role_{role.role_no}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback(f"Summarizing role: {role.name}...")

        context = format_role_context(role, config)
        summary = self._generate_with_fallback(
            ROLE_PROMPT,
            context,
            f"role {role.name}"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_eform_summary(
        self,
        eform: 'EForm',
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate summary for an eform.

        Args:
            eform: EForm to summarize
            config: Configuration object for cross-references
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = f"eform_{eform.form_no}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback(f"Summarizing eform: {eform.name}...")

        context = format_eform_context(eform, config)
        summary = self._generate_with_fallback(
            EFORM_PROMPT,
            context,
            f"eform {eform.name}"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_dictionary_summary(
        self,
        dictionary: 'KeywordDictionary',
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Generate summary for a keyword dictionary.

        Args:
            dictionary: KeywordDictionary to summarize
            config: Configuration object for cross-references
            progress_callback: Optional callback to report progress

        Returns:
            Generated summary or None if failed
        """
        cache_key = f"dictionary_{dictionary.dictionary_no}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if progress_callback:
            progress_callback(f"Summarizing dictionary: {dictionary.name}...")

        context = format_dictionary_context(dictionary, config)
        summary = self._generate_with_fallback(
            DICTIONARY_PROMPT,
            context,
            f"dictionary {dictionary.name}"
        )

        if summary:
            self._cache[cache_key] = summary

        return summary

    def generate_all_summaries_parallel(
        self,
        config: 'Configuration',
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_workers: int = 3
    ) -> Dict[str, Dict[str, str]]:
        """Generate summaries for all elements in parallel.

        Args:
            config: Full configuration object
            progress_callback: Optional callback(completed, total, current_item)
            max_workers: Maximum number of parallel workers (default: 3)

        Returns:
            Dict with keys: 'overview', 'categories', 'workflows', 'roles', etc.
        """
        result = {
            'overview': {},
            'categories': {},
            'workflows': {},
            'roles': {},
            'eforms': {},
            'dictionaries': {}
        }

        # Build list of all tasks to generate
        tasks = []

        # System overview
        tasks.append(('overview', 'system', None, config))

        # Categories
        standalone_categories = [c for c in config.categories if not c.belongs_to_case_def]
        for category in standalone_categories:
            tasks.append(('category', category.category_no, category, config))

        # Workflows
        for workflow in config.workflows:
            tasks.append(('workflow', workflow.process_no, workflow, config))

        # Roles
        for role in config.roles:
            tasks.append(('role', role.role_no, role, config))

        # EForms
        for eform in config.eforms:
            tasks.append(('eform', eform.form_no, eform, config))

        # Dictionaries
        for dictionary in config.keyword_dictionaries:
            tasks.append(('dictionary', dictionary.dictionary_no, dictionary, config))

        total_tasks = len(tasks)
        completed = 0

        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for task_type, item_id, item, cfg in tasks:
                future = executor.submit(self._generate_single_summary, task_type, item_id, item, cfg)
                future_to_task[future] = (task_type, item_id, item)

            # Process completed tasks
            for future in as_completed(future_to_task):
                task_type, item_id, item = future_to_task[future]
                try:
                    summary = future.result()
                    if summary:
                        if task_type == 'overview':
                            result['overview']['system'] = summary
                        elif task_type == 'category':
                            result['categories'][item_id] = summary
                        elif task_type == 'workflow':
                            result['workflows'][item_id] = summary
                        elif task_type == 'role':
                            result['roles'][item_id] = summary
                        elif task_type == 'eform':
                            result['eforms'][item_id] = summary
                        elif task_type == 'dictionary':
                            result['dictionaries'][item_id] = summary

                    completed += 1

                    # Report progress
                    if progress_callback:
                        item_name = getattr(item, 'name', 'system') if item else 'system'
                        progress_callback(completed, total_tasks, f"{task_type}: {item_name}")

                except Exception as e:
                    print(f"Error generating {task_type} summary: {e}")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total_tasks, f"Failed: {task_type}")

        return result

    def _generate_single_summary(self, task_type: str, item_id, item, config: 'Configuration') -> Optional[str]:
        """Generate a single summary (helper for parallel generation).

        Args:
            task_type: Type of summary ('overview', 'category', 'workflow', etc.)
            item_id: ID of the item
            item: The item to summarize
            config: Configuration object

        Returns:
            Generated summary or None
        """
        if task_type == 'overview':
            return self.generate_system_overview(config)
        elif task_type == 'category':
            return self.generate_category_summary(item, config)
        elif task_type == 'workflow':
            return self.generate_workflow_summary(item, config)
        elif task_type == 'role':
            return self.generate_role_summary(item, config)
        elif task_type == 'eform':
            return self.generate_eform_summary(item, config)
        elif task_type == 'dictionary':
            return self.generate_dictionary_summary(item, config)
        return None

    def generate_all_summaries(
        self,
        config: 'Configuration',
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Dict[str, str]]:
        """Generate summaries for all elements in configuration.

        Args:
            config: Full configuration object
            progress_callback: Optional callback to report progress

        Returns:
            Dict with keys: 'overview', 'categories', 'workflows', 'roles'
            Each value is a dict mapping element ID/key to summary text
        """
        result = {
            'overview': {},
            'categories': {},
            'workflows': {},
            'roles': {},
            'eforms': {},
            'dictionaries': {}
        }

        # System overview
        overview = self.generate_system_overview(config, progress_callback)
        if overview:
            result['overview']['system'] = overview

        # Categories
        standalone_categories = [c for c in config.categories if not c.belongs_to_case_def]
        for category in standalone_categories:
            summary = self.generate_category_summary(category, config, progress_callback)
            if summary:
                result['categories'][category.category_no] = summary

        # Workflows
        for workflow in config.workflows:
            summary = self.generate_workflow_summary(workflow, config, progress_callback)
            if summary:
                result['workflows'][workflow.process_no] = summary

        # Roles
        for role in config.roles:
            summary = self.generate_role_summary(role, config, progress_callback)
            if summary:
                result['roles'][role.role_no] = summary

        # EForms
        for eform in config.eforms:
            summary = self.generate_eform_summary(eform, config, progress_callback)
            if summary:
                result['eforms'][eform.form_no] = summary

        # Dictionaries
        for dictionary in config.keyword_dictionaries:
            summary = self.generate_dictionary_summary(dictionary, config, progress_callback)
            if summary:
                result['dictionaries'][dictionary.dictionary_no] = summary

        return result
