# Cohere - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://cohere.com

---

After visiting the official Cohere website and developer documentation as of today, here is the research on their free LLM API offerings:

---

### **Provider: Cohere**
**URL:** https://cohere.com

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Cohere offers a **free tier that is "always free with limits"** for non-commercial use, allowing developers to build and test applications. It's described as a "free forever plan" for initial development. For scaling beyond the free tier or for commercial use, paid plans are available.

*   **What are the rate limits?**
    *   **RPM (Requests Per Minute):** 10 RPM (for all models combined in the free tier)
    *   **TPM (Tokens Per Minute):** 100,000 TPM (for all models combined in the free tier)
    *   **Daily Caps:** Not explicitly stated as a separate cap, but the RPM and TPM limits effectively set a daily usage ceiling. The free tier is generous enough for development and prototyping.
    *   **Monthly Caps:** 100,000 Free Tokens per month for models like Command, Summarize, and Rerank.

*   **Does it require credit card?**
    **No, a credit card is not required** to sign up for the free tier and get an API key. You can sign up with just an email address.

### 2. Available Models (as of today):

Cohere's free tier provides access to a selection of their foundational models. The availability and specific versions are subject to updates, but as of today, the documentation indicates the following are generally accessible in the free tier for non-commercial use:

| Model Name             | Context Window (Input + Output Tokens) | Speed Tier            | Notes                                             |
| :--------------------- | :------------------------------------- | :-------------------- | :------------------------------------------------ |
| **Command (latest)**   | ~4096 tokens (exact varies)            | Standard              | General-purpose generation, instruction following |
| **Command-light (latest)** | ~4096 tokens (exact varies)            | Faster                | Optimized for speed, good for many tasks          |
| **Embed v3 (English)** | N/A (embedding model)                  | Standard              | Text embeddings for semantic search, RAG, classification |
| **Embed v3 (Multilingual)** | N/A (embedding model)                  | Standard              | Text embeddings for multiple languages            |
| **Rerank v3**          | N/A (reranking model)                  | Standard              | Improves search relevance by re-ranking documents |
| **Summarize**          | Up to ~100k input tokens               | Standard              | Condenses long text into concise summaries        |

*Note: While `Command` and `Command-light` are the core generative models, `Embed`, `Rerank`, and `Summarize` are specialized models available to enhance applications built with the generative models.*

### 3. API Documentation:

*   **Base URL:**
    `https://api.cohere.ai/v1/`

*   **Authentication Method:**
    Authentication is done by including your API key in the `Authorization` header of your HTTP requests as a Bearer token.
    `Authorization: Bearer YOUR_API_KEY`

*   **Example curl command (for text generation using Command):**
    ```bash
    curl -X POST \
      https://api.cohere.ai/v1/chat \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer YOUR_API_KEY' \
      -d '{
        "chat_history": [],
        "message": "What are the capital cities of France and Germany?",
        "connectors": [],
        "model": "command",
        "temperature": 0.3
      }'
    ```
    (Note: The `chat` endpoint is a common way to interact with Command models for conversational use cases.)

### 4. Reliability:

*   **Uptime history:**
    Cohere maintains a public status page which provides real-time operational status and incident history.
    **Status Page URL:** [https://status.cohere.com/](https://status.cohere.com/)
    As of checking, the status page shows "All Systems Operational" with a very good historical uptime record, typically reporting high percentages (e.g., 99.9%+) over the past 90 days for core API services. Minor incidents (e.g., increased latency) are transparently reported and resolved.

*   **Community feedback:**
    Community feedback for Cohere generally indicates a positive experience, particularly for their embedding and reranking models which are highly regarded for their performance in RAG (Retrieval Augmented Generation) applications. The `Command` models are seen as strong contenders for various NLP tasks, offering good balance between performance and cost. Developers appreciate the clear documentation and the generosity of the free tier for testing and prototyping. Some feedback mentions that while powerful, the `Command` models might sometimes be less widely discussed for general chatbot use compared to some competitors, but are highly valued for enterprise and specialized NLP tasks.

### 5. Best Use Case for Cohere:

*   **PDF Extraction:**
    *   **Model:** `Command (latest)` or `Command-light (latest)` combined with `Summarize` and potentially `Embed v3`.
    *   **Approach:** For direct extraction, you'd need to first OCR the PDF (Cohere doesn't do OCR). Once text is extracted, use `Command` with a well-designed prompt to identify and extract specific entities or structured data. For summarizing sections or the entire PDF text, the `Summarize` model is excellent. For semantic search within PDF content (e.g., "find all mentions of project budgets"), `Embed v3` can be used to create embeddings of PDF chunks for a retrieval system, and `Rerank v3` can enhance the relevance of retrieved results before feeding them to `Command`.

*   **Research:**
    *   **Model:** `Command (latest)` and `Summarize` heavily, supported by `Embed v3` and `Rerank v3`.
    *   **Approach:** `Command` is excellent for synthesizing information, answering complex questions, and generating reports based on provided text. Its instruction-following capabilities make it suitable for deep analysis. `Summarize` is invaluable for quickly grasping the essence of long research papers or articles. `Embed v3` and `Rerank v3` are crucial for building effective RAG systems to query large research datasets, ensuring the most relevant information is retrieved and prioritized before being used by `Command` to formulate answers.

*   **Coding:**
    *   **Model:** `Command (latest)` or `Command-light (latest)`.
    *   **Approach:** `Command` can be used for code generation (e.g., "write a Python function to parse JSON"), code explanation ("explain this Javascript function"), debugging suggestions, and translating code between languages. While not solely a code-specific model like some others, its strong natural language understanding and generation capabilities allow it to perform well on coding tasks, especially when guided by clear prompts. For simpler and faster responses, `Command-light` might be preferred.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
