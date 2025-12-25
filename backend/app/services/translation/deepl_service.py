import deepl
from app.core.config import settings
from typing import Optional


class DeepLTranslationService:
    def __init__(self):
        self.translator = deepl.Translator(settings.DEEPL_API_KEY)
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Optional[str]:
        """Translate text using DeepL"""
        try:
            # Map language codes to DeepL format
            source_lang = self._map_language_code(source_language)
            target_lang = self._map_language_code(target_language)
            
            if source_lang == target_lang:
                return text
            
            result = self.translator.translate_text(
                text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            return result.text
        except Exception as e:
            print(f"DeepL translation error: {e}")
            return None
    
    def _map_language_code(self, lang_code: str) -> str:
        """Map language codes to DeepL format"""
        lang_map = {
            "en": "EN",
            "es": "ES",
            "pt": "PT",
            "fr": "FR",
            "de": "DE",
            "it": "IT",
            "ru": "RU",
            "zh": "ZH",
            "ja": "JA",
            "ar": "AR",
            "ht": "EN",  # Haitian Creole - DeepL doesn't support, will use fallback
        }
        return lang_map.get(lang_code.lower(), "EN")

