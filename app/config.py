from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    database_url: str = Field(default='sqlite:///./automation.db', alias='DATABASE_URL')
    app_env: str = Field(default='dev', alias='APP_ENV')

    web_access_mode: Literal['offline', 'allowlist', 'open'] = Field(default='allowlist', alias='WEB_ACCESS_MODE')
    web_allowlist_domains: str = Field(default='', alias='WEB_ALLOWLIST_DOMAINS')

    whatsapp_verify_token: str = Field(default='', alias='WHATSAPP_VERIFY_TOKEN')
    whatsapp_phone_number_id: str = Field(default='', alias='WHATSAPP_PHONE_NUMBER_ID')
    whatsapp_access_token: str = Field(default='', alias='WHATSAPP_ACCESS_TOKEN')
    whatsapp_allowed_to: str = Field(default='', alias='WHATSAPP_ALLOWED_TO')

    llm_provider: str = Field(default='ollama', alias='LLM_PROVIDER')
    ollama_base_url: str = Field(default='http://localhost:11434', alias='OLLAMA_BASE_URL')
    ollama_model: str = Field(default='llama3.1:8b', alias='OLLAMA_MODEL')
    ollama_vision_model: str = Field(default='llava:7b', alias='OLLAMA_VISION_MODEL')
    openai_base_url: str = Field(default='', alias='OPENAI_BASE_URL')
    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')

    media_storage_dir: str = Field(default='data/media', alias='MEDIA_STORAGE_DIR')

    @property
    def media_storage_path(self) -> Path:
        return Path(self.media_storage_dir)


settings = Settings()
