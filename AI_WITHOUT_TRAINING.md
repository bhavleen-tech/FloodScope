# FloodScope AI without model training

This release supports an optional **pretrained hosted LLM** to explain computed results. No PyTorch, training, or model weights are required. Without credentials, the assistant works in transparent **grounded local rules** mode; it is not generative AI in that mode.

To enable a hosted pretrained AI (optional), set these environment variables before starting the backend:

- `FLOODSCOPE_LLM_API_KEY` = your provider API key (never put it in frontend code or Git)
- `FLOODSCOPE_LLM_URL` = HTTPS OpenAI-compatible chat completions endpoint (default `https://api.openai.com/v1/chat/completions`)
- `FLOODSCOPE_LLM_MODEL` = provider's pretrained chat model ID (default `gpt-4o-mini`)

The provider may charge fees and requires an appropriate account. The browser does not receive the key. Only numeric computed assessment context is shared with the provider; questions are sent to the provider when enabled. Do not upload private/sensitive material.

**Scientific integrity:** This assistant explains results; it does not generate flood masks or replace a validated flood segmentation model. The existing Sentinel-2 NDWI and Sentinel-1 threshold methods are rule-based. Raw Sentinel-1 SAFE preprocessing and independent real-event validation are not completed.
