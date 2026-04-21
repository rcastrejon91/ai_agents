import os

def call_llm(system: str, messages: list, max_tokens: int = 500) -> str:
    """Call Claude with automatic Groq fallback on rate limit/quota errors."""
    # Try Claude first
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        return response.content[0].text.strip()
    except Exception as e:
        err = str(e).lower()
        # Fallback to Groq on quota/rate limit errors
        if 'limit' in err or '429' in err or '400' in err or 'usage' in err:
            return _groq_fallback(system, messages, max_tokens)
        raise

def _groq_fallback(system: str, messages: list, max_tokens: int = 500) -> str:
    """Use Groq (free) as fallback when Claude is unavailable."""
    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        groq_messages = [{'role': 'system', 'content': system}] + messages
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=groq_messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'I am temporarily unavailable. Please try again shortly. ({str(e)})'
