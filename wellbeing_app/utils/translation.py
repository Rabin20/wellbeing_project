class BulkTranslator:
    """Fallback translation system when no API is available"""
    def __init__(self):
        # Basic Māori translations dictionary
        self.translations = {
            "Wellbeing App": "Taupānga Hauora",
            "Home": "Kāinga",
            "Mood Tracker": "Pūrongo Āhua",
            "Journal": "Pukapuka",
            "Whānau Support": "Tautoko Whānau",
            "Resources": "Rauemi",
            "Logout": "Whakaputa",
            "Login": "Takiuru",
            "Community Wellbeing App - Supporting Māori and Multicultural Youth": "Taupānga Hauora Hapori - Tautoko i ngā Taiohi Māori me ngā Taiohi Ahurea Maha",
            "He waka eke noa - We're all in this together": "He waka eke noa - Kei roto tātou katoa i tēnei"
        }
    
    def translate_bulk(self, texts, target_lang='mi'):
        """Simple dictionary-based translation"""
        if target_lang == 'mi':
            return [self.translations.get(text, text) for text in texts]
        return texts