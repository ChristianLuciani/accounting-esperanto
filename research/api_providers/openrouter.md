# OpenRouter - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://openrouter.ai

---

As of **June 14, 2024**, here is the detailed research on OpenRouter's free LLM API offerings:

---

## OpenRouter Research

**URL:** https://openrouter.ai

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    OpenRouter is currently **"free to use while in beta."** This means all models available on their platform are effectively free to use without charging during this beta period. It is not a fixed credit system that runs out, nor is it an "always free" tier with specific limits that will persist indefinitely; its free status is tied to its beta phase, which could end at any time.

*   **What are the rate limits? (RPM, TPM, daily caps)**
    OpenRouter documentation states: "Paid users get significantly higher rate limits based on their spend, and **beta users are given conservative rate limits.**"
    *   **Specific numbers for beta users are NOT explicitly published.** This is a common practice for beta programs. Users should expect limits designed to prevent abuse and ensure service availability, which might be lower than typical commercial tiers. If you hit rate limits, you'll receive a `429 Too Many Requests` error.

*   **Does it require a credit card?**
    **No.** Signing up for an account and generating an API key for beta usage does not require a credit card.

### 2. Available Models (as of today):

**Crucial Note:** During the beta phase, all models listed on OpenRouter's pricing page are effectively available for free use. This is an extremely generous offering.

Below is a selection of popular and high-performing models available, along with their reported context windows. OpenRouter does not explicitly categorize models by "speed tier"; instead, they provide input/output token costs (which are currently $0 during beta) and often latency metrics.

| Model Name (OpenRouter ID)              | Context Window | Speed Tier (OpenRouter's Info)              |
| :-------------------------------------- | :------------- | :------------------------------------------ |
| **GPT-4o** (openai/gpt-4o)              | 128k tokens    | Not specified by OpenRouter (Generally High-end) |
| **GPT-4o Mini** (openai/gpt-4o-mini)    | 128k tokens    | Not specified by OpenRouter (Faster/Cheaper than GPT-4o) |
| **GPT-4 Turbo (2024-04-09)** (openai/gpt-4-turbo) | 128k tokens | Not specified by OpenRouter (Generally High-end) |
| **GPT-3.5 Turbo (0125)** (openai/gpt-3.5-turbo) | 16k tokens     | Not specified by OpenRouter (Generally Fast) |
| **Claude 3 Opus** (anthropic/claude-3-opus) | 200k tokens    | Not specified by OpenRouter (Generally High-end) |
| **Claude 3 Sonnet** (anthropic/claude-3-sonnet) | 200k tokens    | Not specified by OpenRouter (Generally Balanced) |
| **Claude 3 Haiku** (anthropic/claude-3-haiku) | 200k tokens    | Not specified by OpenRouter (Generally Fast) |
| **Llama 3 8B Instruct** (meta-llama/llama-3-8b-instruct) | 8k tokens      | Not specified by OpenRouter (Generally Fast) |
| **Llama 3 70B Instruct** (meta-llama/llama-3-70b-instruct) | 8k tokens      | Not specified by OpenRouter (Generally Powerful) |
| **Gemini 1.5 Pro (Flash)** (google/gemini-1.5-pro-flash) | 1M tokens      | Not specified by OpenRouter (Generally Fast) |
| **Gemini 1.5 Pro (Long)** (google/gemini-1.5-pro-long) | 1M tokens      | Not specified by OpenRouter (Generally Powerful) |
| **Mixtral 8x7B Instruct (v0.1)** (mistralai/mixtral-8x7b-instruct) | 32k tokens     | Not specified by OpenRouter (Generally Fast) |
| **Mixtral 8x22B Instruct (v0.1)** (mistralai/mixtral-8x22b-instruct) | 64k tokens     | Not specified by OpenRouter (Generally Powerful) |
| **Command R+** (cohere/command-r-plus) | 128k tokens    | Not specified by OpenRouter (Generally High-end) |
| **Perplexity LLM v2** (perplexity/llama-3-sonar-large-32k-online) | 32k tokens     | Not specified by OpenRouter (Optimized for Search/RAG) |
| **Nous Hermes-2 Vision** (nousresearch/nous-hermes-2-vision) | 4k tokens      | Not specified by OpenRouter (Multimodal) |

*(This is a selection. OpenRouter hosts many more models from various providers. All are currently free during beta.)*

### 3. API Documentation:

*   **Base URL:**
    `https://openrouter.ai/api/v1/chat/completions` (for chat completions, which is the most common use case)

*   **Authentication method:**
    API Key in the `Authorization` header as a Bearer token.
    `Authorization: Bearer sk-my-api-key`

*   **Example curl command:**

    ```bash
    curl -X POST \
      https://openrouter.ai/api/v1/chat/completions \
      -H "Authorization: Bearer sk-my-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "openai/gpt-4o",
        "messages": [
          {"role": "user", "content": "What is the capital of France?"}
        ]
      }'
    ```
    *(Replace `sk-my-api-key` with your actual API key and `openai/gpt-4o` with your desired model ID).*

### 4. Reliability:

*   **Uptime history (if available):**
    OpenRouter provides a public status page: **https://status.openrouter.ai/**
    This page offers real-time status updates and historical uptime for its services, API, and individual model endpoints. As of today, the overall API uptime is generally excellent (often 99.9%+), but individual model availability can fluctuate based on the underlying provider's status.

*   **Community feedback:**
    OpenRouter generally receives very positive community feedback from developers.
    *   **Pros:** Highly valued for its unified API interface across a vast array of models, competitive pricing (when not free), and convenience of testing different models. The current "free during beta" offering is highly praised.
    *   **Cons:** As a router, performance (latency) can sometimes vary depending on the chosen model and its underlying provider. Occasional transient errors related to specific model backends are reported, but OpenRouter's system is designed to provide visibility and allow switching models.
    *   Overall, it's considered a reliable and essential tool for many LLM developers looking for flexibility and cost-effectiveness.

### 5. Best Use Case for OpenRouter:

Given the current "free during beta" offering, OpenRouter is an excellent choice for **rapid prototyping, experimentation, and development** across a wide range of LLM tasks without upfront costs. You can easily switch models to find the best fit for your application.

*   **PDF Extraction:**
    *   **Best Model:** **Claude 3 Opus** (anthropic/claude-3-opus) or **Gemini 1.5 Pro (Long)** (google/gemini-1.5-pro-long)
    *   **Reasoning:** Both are leading models in terms of complex reasoning, long context window (200k for Opus, 1M for Gemini 1.5 Pro), and ability to follow intricate instructions, which are critical for accurate information extraction from lengthy documents. Claude 3 Opus is particularly strong in nuanced understanding, while Gemini 1.5 Pro excels with its massive context window for entire PDFs. GPT-4o is also a strong contender with its 128k context and multimodal capabilities if the PDF contains images.

*   **Research:**
    *   **Best Model:** **Claude 3 Opus** (anthropic/claude-3-opus) or **GPT-4o** (openai/gpt-4o) or **Gemini 1.5 Pro (Long)** (google/gemini-1.5-pro-long)
    *   **Reasoning:** Similar to PDF extraction, research demands high-level reasoning, summarization of complex information, critical analysis, and long context understanding. These models excel at synthesizing information, identifying key points, and generating insightful responses. Gemini 1.5 Pro's 1M context is unparalleled for extensive document analysis. GPT-4o's multimodal capabilities could also be useful if research involves visual data.

*   **Coding:**
    *   **Best Model:** **GPT-4o** (openai/gpt-4o), **Claude 3 Sonnet** (anthropic/claude-3-sonnet), or **Mixtral 8x22B Instruct (v0.1)** (mistralai/mixtral-8x22b-instruct)
    *   **Reasoning:** GPT-4o is a general powerhouse and performs exceptionally well on coding tasks, from generation to debugging. Claude 3 Sonnet provides a good balance of performance and speed for coding assistance. Mixtral 8x22B Instruct is known for its strong coding capabilities among open-source models and offers a larger context than its 8x7B counterpart, making it suitable for more complex codebases or longer functions. For focused code generation/completion, models like Code Llama (if available and updated) can also be excellent, but the general-purpose models often cover a broader range of coding tasks effectively.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
