import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import KnowledgeItem
from app.services.logging_service import write_log
from app.services.web_policy import enforce_url_access


def internet_search(query: str) -> list[dict]:
    if settings.web_access_mode == 'offline':
        raise ValueError('Internet access is disabled')

    url = f'https://duckduckgo.com/?q={query}&ia=web'
    enforce_url_access(url)
    return [{'title': 'Search dispatched', 'url': url, 'snippet': 'Open this URL in your approved browser automation flow.'}]


def generate_content(db: Session, prompt: str, category: str = 'general') -> dict:
    knowledge = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.category == category)
        .order_by(KnowledgeItem.created_at.desc())
        .limit(5)
        .all()
    )
    context_text = '\n'.join(item.unstructured_text for item in knowledge if item.unstructured_text)

    if settings.llm_provider == 'ollama':
        payload = {
            'model': settings.ollama_model,
            'prompt': f'Context:\n{context_text}\n\nUser prompt:\n{prompt}',
            'stream': False,
        }
        with httpx.Client(timeout=60) as client:
            response = client.post(f'{settings.ollama_base_url}/api/generate', json=payload)
            response.raise_for_status()
            text = response.json().get('response', '')
    else:
        text = f'[stubbed response] {prompt}'

    write_log(db, action='agent.generate_content', details='Generated content with provider', extra_data={'provider': settings.llm_provider})
    return {'content': text, 'provider': settings.llm_provider}
