import requests
from fastapi import HTTPException

# Placeholder: Government schemes database
gov_schemes = {
    "Wheat": ["PM-KISAN", "Crop Insurance Scheme"],
    "Rice": ["PM-KISAN", "National Mission for Sustainable Agriculture"],
    "Maize": ["PM-KISAN", "Soil Health Card Scheme"],
    "Barley": ["PM-KISAN", "Crop Insurance Scheme"]
}

# Placeholder: Mock translation function (replace with real API like Google Translate)
def translate_text(text: str, target_language: str) -> str:
    # Mock translations for common Indian languages
    translations = {
        "hi": f"[Hindi] {text}",  # Replace with actual translation
        "ta": f"[Tamil] {text}",
        "te": f"[Telugu] {text}",
        "mr": f"[Marathi] {text}"
    }
    return translations.get(target_language, text)  # Default to English if language not found

def get_chat_response(message: str, context: dict = None, language: str = "en"):
    try:
        # Extract crop from context if available
        crop = context.get("crop", None) if context else None
        schemes = gov_schemes.get(crop, ["PM-KISAN"]) if crop else ["PM-KISAN"]
        
        # Mock LLM response with scheme integration
        response = (
            f"Based on your query '{message}', I recommend checking soil health and consulting local agricultural guidelines. "
            f"Relevant government schemes for {'your crop' if crop else 'general farming'}: {', '.join(schemes)}."
        )
        
        # Translate response to target language
        translated_response = translate_text(response, language)
        
        # Uncomment for real LLM integration
        """
        payload = {
            "prompt": f"Farmer query: {message}. Context: {context if context else 'No context provided'}. "
                      f"Include these government schemes: {', '.join(schemes)}",
            "max_tokens": 100,
            "temperature": 0.7
        }
        response = requests.post("YOUR_LLM_API_ENDPOINT", json=payload, headers={"Authorization": "Bearer YOUR_API_KEY"})
        response.raise_for_status()
        translated_response = translate_text(response.json()["reply"], language)
        """
        
        return translated_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")