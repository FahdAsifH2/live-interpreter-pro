from azure.ai.translator import TranslatorClient
from azure.core.credentials import AzureKeyCredential
from app.core.config import settings
from typing import Optional


class AzureTranslationService:
    def __init__(self):
        if not all([settings.AZURE_TRANSLATOR_KEY, settings.AZURE_TRANSLATOR_ENDPOINT]):
            self.client = None
        else:
            credential = AzureKeyCredential(settings.AZURE_TRANSLATOR_KEY)
            self.client = TranslatorClient(
                endpoint=settings.AZURE_TRANSLATOR_ENDPOINT,
                credential=credential
            )
    
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

