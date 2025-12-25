from .deepl_service import DeepLTranslationService
from .azure_service import AzureTranslationService
from typing import Optional

__all__ = ["DeepLTranslationService", "AzureTranslationService", "TranslationService"]


class TranslationService:
    """Unified translation service with fallback"""
    
    def __init__(self):
        self.deepl = DeepLTranslationService()
        self.azure = AzureTranslationService()
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Optional[str]:
        """Translate text with DeepL primary and Azure fallback"""
        # Try DeepL first
        result = await self.deepl.translate(text, source_language, target_language)
        
        if result:
            return result
        
        # Fallback to Azure
        if self.azure.client:
            result = await self.azure.translate(text, source_language, target_language)
            if result:
                return result
        
        return None

