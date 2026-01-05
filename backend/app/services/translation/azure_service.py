from app.core.config import settings
from typing import Optional

# Azure Translator is optional - make import optional
try:
    from azure.ai.translation.text import TranslatorClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    TranslatorClient = None
    AzureKeyCredential = None


class AzureTranslationService:
    def __init__(self):
        self.client = None
        
        if not AZURE_AVAILABLE:
            return
            
        if not all([settings.AZURE_TRANSLATOR_KEY, settings.AZURE_TRANSLATOR_ENDPOINT]):
            return
            
        try:
            credential = AzureKeyCredential(settings.AZURE_TRANSLATOR_KEY)
            self.client = TranslatorClient(
                endpoint=settings.AZURE_TRANSLATOR_ENDPOINT,
                credential=credential
            )
        except Exception as e:
            print(f"Failed to initialize Azure Translator: {e}")
            self.client = None
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Optional[str]:
        """Translate text using Azure Translator"""
        if not self.client:
            return None
        
        try:
            response = self.client.translate(
                content=[text],
                to=[target_language],
                from_parameter=source_language
            )
            
            if response and len(response) > 0:
                translation = response[0]
                if translation.translations and len(translation.translations) > 0:
                    return translation.translations[0].text
        except Exception as e:
            print(f"Azure translation error: {e}")
            return None
        
        return None

