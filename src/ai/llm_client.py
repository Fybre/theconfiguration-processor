"""OpenAI-compatible LLM client for local models (Ollama, LM Studio, LocalAI) and Azure OpenAI."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class LLMConfig:
    """Configuration for LLM connection."""
    base_url: str = "http://localhost:11434/v1"  # Default Ollama
    model_name: str = "llama3.2"
    api_key: str = "not-needed"  # Most local LLMs don't need this
    timeout: int = 60
    max_tokens: int = 500
    temperature: float = 0.4  # Lower for more consistent technical documentation


class LLMClient:
    """Client for OpenAI-compatible LLM APIs (local models and Azure OpenAI)."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM client with configuration.

        Args:
            config: LLM configuration settings
        """
        self.config = config
        self._client = None

    def _get_client(self):
        """Lazy initialize OpenAI client.

        Returns:
            OpenAI or AzureOpenAI client instance

        Raises:
            ImportError: If openai package is not installed
        """
        if self._client is None:
            try:
                # Detect if this is an Azure OpenAI endpoint
                is_azure = "azure.com" in self.config.base_url.lower()

                if is_azure:
                    from openai import AzureOpenAI

                    # Parse Azure endpoint and deployment from base_url
                    # Format: https://{resource}.{domain}/openai/deployments/{deployment}
                    import re
                    match = re.match(r'(https://[^/]+)', self.config.base_url)
                    if not match:
                        raise ValueError(f"Invalid Azure OpenAI base_url: {self.config.base_url}")

                    azure_endpoint = match.group(1)

                    # Extract deployment name from URL if present
                    deployment_match = re.search(r'/deployments/([^/]+)', self.config.base_url)
                    deployment = deployment_match.group(1) if deployment_match else self.config.model_name

                    self._client = AzureOpenAI(
                        azure_endpoint=azure_endpoint,
                        api_key=self.config.api_key,
                        api_version="2024-02-15-preview",  # Stable API version
                        timeout=self.config.timeout
                    )
                    # Store deployment name for later use
                    self._azure_deployment = deployment
                else:
                    from openai import OpenAI
                    self._client = OpenAI(
                        base_url=self.config.base_url,
                        api_key=self.config.api_key,
                        timeout=self.config.timeout
                    )
                    self._azure_deployment = None

            except ImportError:
                raise ImportError(
                    "OpenAI client not installed. "
                    "Install with: pip install openai"
                )
        return self._client

    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to LLM.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            client = self._get_client()
            # Use deployment name for Azure, model name for others
            model = self._azure_deployment if hasattr(self, '_azure_deployment') and self._azure_deployment else self.config.model_name

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True, "Connection successful"
        except ImportError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """Generate completion from LLM.

        Args:
            system_prompt: System message defining behavior
            user_prompt: User message with content to summarize

        Returns:
            Generated text or None if failed
        """
        try:
            client = self._get_client()
            # Use deployment name for Azure, model name for others
            model = self._azure_deployment if hasattr(self, '_azure_deployment') and self._azure_deployment else self.config.model_name

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM generation error: {e}")
            return None
