# Poe - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://poe.com/api

---

Poe offers an interesting model for developers, acting as a gateway to various LLMs from different providers (OpenAI, Anthropic, Google, Meta, Mistral, Cohere, etc.) through a unified API.

---

## Poe LLM API Provider Details (As of Today)

**URL:** `https://developer.poe.com/` (redirects from `https://poe.com/api`)

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Poe API operates on an "**always free with limits**" model. Every model available through the API has a daily token quota that resets every 24 hours. Once you exceed this quota for a specific model, you'll need to wait for the reset or upgrade to a paid tier (Poe Pro) to continue using that model without limits.
    You can monitor your daily token usage and remaining quota for each model on your Poe account page (`poe.com/account`).

*   **What are the rate limits?**
    *   **Token Limits:** Daily token limits vary significantly by model. High-end models (e.g., GPT-4o, Claude 3 Opus) will have much lower free daily token limits than smaller, more efficient models (e.g., Llama 3 8B, GPT-3.5 Turbo). Poe does *not* publicly list specific daily token limits for each model; these are dynamic and displayed on your individual account page.
    *   **RPM (Requests Per Minute) / TPM (Tokens Per Minute):** Poe does not explicitly publish global RPM/TPM limits for the free tier in its documentation. However, standard API best practices suggest there are internal rate limits to prevent abuse. Hitting daily token caps is the primary limitation for free users.
    *   **Daily Caps:** Yes, there are daily token caps for *each individual model*.

*   **Does it require a credit card?**
    **No**, a credit card is **not required** to sign up for a Poe account and use the free API tier. You only need to provide a credit card if you wish to upgrade to Poe Pro to remove daily token limits and get unlimited usage (or higher limits) across all models.

### 2. Available Models (as of today):

Poe provides access to a wide range of models, and critically, **all models accessible via the API have a free tier with daily limits.** The specific limits vary by model.

Here is a list of prominent models mentioned in Poe's API documentation and available through the platform. For context window and speed tier, these are general characteristics of the underlying model, as Poe itself does not alter these.

*   **gpt-4o**
    *   Context Window: 128K tokens
    *   Speed Tier: Fast
*   **claude-3-opus-20240229**
    *   Context Window: 200K tokens
    *   Speed Tier: Fast
*   **claude-3-sonnet-20240229**
    *   Context Window: 200K tokens
    *   Speed Tier: Medium-Fast
*   **claude-3-haiku-20240229**
    *   Context Window: 200K tokens
    *   Speed Tier: Very Fast
*   **gpt-4-turbo** (typically `gpt-4-0125-preview` or similar)
    *   Context Window: 128K tokens
    *   Speed Tier: Fast
*   **gpt-4-0613**
    *   Context Window: 8K tokens
    *   Speed Tier: Medium
*   **gpt-3.5-turbo** (latest version, e.g., `gpt-3.5-turbo-0125`)
    *   Context Window: 16K tokens (or 4K for older versions)
    *   Speed Tier: Very Fast
*   **mixtral-8x7b-instruct-v0.1**
    *   Context Window: 32K tokens
    *   Speed Tier: Fast
*   **llama-3-8b-chat**
    *   Context Window: 8K tokens
    *   Speed Tier: Very Fast
*   **llama-3-70b-chat**
    *   Context Window: 8K tokens
    *   Speed Tier: Fast
*   **gemini-pro**
    *   Context Window: 32K tokens
    *   Speed Tier: Fast
*   **command-r-plus**
    *   Context Window: 128K tokens
    *   Speed Tier: Fast
*   **mistral-medium**
    *   Context Window: 32K tokens
    *   Speed Tier: Fast
*   **dalle-3** (Image Generation) - *Note: While available, this is an image generation model, not text-based LLM.*
    *   Context Window: N/A
    *   Speed Tier: Moderate

*(Note: Poe frequently updates its model offerings. This list is based on currently prominent models in their API documentation and platform.)*

### 3. API Documentation:

*   **Base URL:** `https://api.poe.com`
*   **Authentication Method:**
    Authentication is done using an **API Key** passed in the `X-Api-Key` HTTP header.
    Your API Key can be generated and managed on your Poe account page: `https://poe.com/account/api`
*   **Example Curl Command (for Chat Completion):**

    ```bash
    curl 'https://api.poe.com/bot/chat' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -H 'X-Api-Key: YOUR_POE_API_KEY' \
      -d '{
        "model": "gpt-4o",
        "query": "Hello, how are you today?",
        "context": []
      }'
    ```
    *(Note: For `context`, you typically pass a history of messages. `model` can be any of the available models, e.g., "claude-3-opus-20240229", "llama-3-8b-chat", etc. For more complex interactions, refer to the full API documentation on `developer.poe.com`.)*

### 4. Reliability:

*   **Uptime History:**
    Poe maintains a status page at `status.poe.com` which primarily reports on the operational status of `Poe.com` and `Poe Bots`. It generally reports "Operational" for its core services. However, a dedicated status page specifically for the *developer API* or the uptime of individual third-party models accessed through Poe's gateway is not publicly available. As Poe acts as a proxy, individual model availability or performance can sometimes be subject to the upstream provider's status, which Poe's system aims to abstract and manage.
*   **Community Feedback:**
    Community feedback is generally positive regarding the convenience and breadth of access Poe provides, especially for its free tier. Developers appreciate having a unified API to experiment with multiple models without needing separate accounts for each provider. Some feedback points to occasional latency spikes or temporary rate limit issues, particularly with popular models during peak usage times. For applications requiring mission-critical, extremely low-latency performance, robust error handling and potentially a paid tier might be necessary, but for development and many production use cases, it's considered a reliable and cost-effective option.

### 5. Best Use Case for Poe:

Poe's strength lies in its **model agnosticism and unified API**, making it excellent for rapid prototyping, comparative testing, and applications that might switch between models based on task or cost efficiency.

*   **PDF Extraction:**
    *   **Recommended Models:** `claude-3-opus-20240229`, `gpt-4o`, `command-r-plus`
    *   **Reasoning:** These models excel in understanding complex document structures, performing detailed information extraction, summarization, and handling long context windows (up to 200K tokens for Claude Opus/Sonnet, 128K for GPT-4o/Command-R-Plus). Their strong reasoning capabilities are crucial for accurately parsing and extracting data from unstructured PDFs.

*   **Research:**
    *   **Recommended Models:** `claude-3-opus-20240229`, `gpt-4o`, `llama-3-70b-chat`
    *   **Reasoning:** Similar to PDF extraction, research tasks (e.g., summarizing articles, identifying key arguments, synthesizing information) benefit from models with large context windows and advanced reasoning. Claude 3 Opus and GPT-4o are top-tier for complex analysis, while Llama 3 70B offers a powerful open-source alternative for detailed inquiry and text generation.

*   **Coding:**
    *   **Recommended Models:** `gpt-4o`, `claude-3-sonnet-20240229`, `mixtral-8x7b-instruct-v0.1`
    *   **Reasoning:** `GPT-4o` is highly proficient across many programming languages, offering excellent code generation, debugging, and explanation capabilities. `Claude 3 Sonnet` is also strong for coding tasks, particularly for larger codebases or more nuanced problem-solving. `Mixtral-8x7B-Instruct-v0.1` is a strong, faster, and more cost-effective option for many coding assistance tasks, especially for generating snippets, explaining concepts, or refactoring.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
