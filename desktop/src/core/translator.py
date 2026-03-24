import json
import os
from PyQt6.QtCore import QObject, pyqtSignal

class Translator(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self, default_lang='fr'):
        super().__init__()
        self.current_lang = default_lang
        self.translations = {}
        self._load_translations(default_lang)

    def _load_translations(self, lang):
        base_path = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_path, 'resources', 'i18n', f'{lang}.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f'Warning: Failed to load translation file for {lang}: {e}')
            self.translations = {}

    def set_language(self, lang):
        self.current_lang = lang
        self._load_translations(lang)
        self.language_changed.emit(lang)

    def translate(self, key, **kwargs):
        keys = key.split('.')
        value = self.translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key
        if isinstance(value, str):
            for k, v in kwargs.items():
                value = value.replace('{{' + k + '}}', str(v))
            return value
        return key

translator = Translator()
