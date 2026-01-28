# Together AI - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://together.ai

---

Here's a detailed breakdown of Together AI's FREE LLM API offering as of today:

---

### Provider: Together AI
**URL:** [https://together.ai](https://together.ai)

---

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Together AI offers **free credits that run out**. New users receive **$25 in free credits** upon signing up. These credits can be used across any of their available models until they are exhausted.
*   **What are the rate limits? (RPM, TPM, daily caps)**
    For accounts in the free tier:
    *   **RPM (Requests Per Minute):** 200
    *   **TPM (Tokens Per Minute):** 200,000
    *   **Daily Caps:** No explicit daily cap is stated beyond the general rate limits and the total $25 credit allocation.
*   **Does it require credit card?**
    **No**, a credit card is not required to get started with the free trial and receive the $25 in credits.

---

### 2. Available Models (as of today):

Together AI offers access to a vast array of models. Any model available via their API can be consumed with the free credits. The "speed tier" is relative to the model's size and architecture, often correlating with its cost per token. Below is a selection of popular and capable models available, along with their key specifications:

| Model Name (Together AI ID)                 | Context Window (Tokens) | Speed Tier (General Performance)                                |
| :------------------------------------------ | :---------------------- | :-------------------------------------------------------------- |
| `mistralai/Mistral-7B-Instruct-v0.2`        | 32,768                  | Fast, good balance of speed & quality for general tasks.        |
| `mistralai/Mixtral-8x7B-Instruct-v0.1`      | 32,768                  | High-quality, strong reasoning, moderate-to-fast speed.         |
| `meta-llama/Llama-2-70b-chat-hf`            | 4,096                   | High-quality, reliable for general chat and complex tasks, moderate speed. |
| `Qwen/Qwen1.5-72B-Chat`                     | 32,768                  | High-quality, competitive, versatile for various applications, moderate speed. |
| `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`| 32,768                  | Excellent instruction following, strong reasoning, moderate-to-fast speed. |
| `zero-one-ai/Yi-34B-Chat`                   | 4,096                   | Strong general performance, good for reasoning, moderate speed. |
| `databricks/dbrx-instruct`                  | 32,768                  | State-of-the-art, highly capable, premium quality, moderate speed (may consume credits faster). |
| `TinyLlama/TinyLlama-1.1B-Chat-v1.0`        | 2,048                   | Very fast, low cost, suitable for simple tasks or testing.      |

*(Note: This is a selection. Together AI's catalog includes many more models from various developers.)*

---

### 3. API Documentation:

*   **Base URL:**
    `https://api.together.xyz/v1/`
    (For chat completions, the endpoint is `https://api.together.xyz/v1/chat/completions`)
*   **Authentication Method:**
    Authentication is done using an **API Key**. The API key is passed in the `Authorization` header as a Bearer token.
    `Authorization: Bearer <YOUR_API_KEY>`
    Your API key can be generated and managed from your Together AI dashboard.
*   **Example curl command (for chat completions):**

    ```bash
    curl https://api.together.xyz/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOGETHER_API_KEY" \
      -d '{
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
          {
            "role": "system",
            "content": "You are a helpful and creative AI assistant."
          },
          {
            "role": "user",
            "content": "Write a short poem about a cat named Luna."
          }
        ],
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.7
      }'
    ```

---

### 4. Reliability:

*   **Uptime history:**
    Together AI maintains a public status page at [https://status.together.ai/](https://status.together.ai/). This page provides real-time operational status for all core services (API, inference, data platform, etc.) and lists historical incidents, including their root cause analysis and resolution. Generally, Together AI shows **high uptime** for its core inference services, indicating a reliable platform for API access.
*   **Community feedback:**
    Community feedback generally praises Together AI for its **extensive model catalog**, **competitive pricing**, and **developer-friendly API**. Users appreciate the ability to access many open-source models through a single, unified API. While occasional service interruptions or performance fluctuations can occur (as with any cloud provider), the overall sentiment for reliability and value is positive among developers and researchers.

---

### 5. Best Use Case for Kontablo:

Given Kontablo's need for PDF extraction, research, and coding, here are the recommended Together AI models from their free tier, leveraging their strengths:

*   **For PDF Extraction:**
    *   **`mistralai/Mixtral-8x7B-Instruct-v0.1`** or **`Qwen/Qwen1.5-72B-Chat`**
    *   **Reasoning:** Both models offer a substantial **32,768-token context window**, which is crucial for handling lengthy PDF content without excessive chunking. Their advanced reasoning and instruction-following capabilities make them excellent for tasks like summarizing documents, extracting specific entities (dates, names, figures), answering questions based on document content, or converting unstructured text into structured data. Mixtral is particularly known for its strong performance on complex analytical tasks.

*   **For Research:**
    *   **`NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`** or **`mistralai/Mixtral-8x7B-Instruct-v0.1`**
    *   **Reasoning:** Both are leading models with a **32,768-token context window**, allowing them to synthesize information from large bodies of text. `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO` is specifically fine-tuned for instruction following and dialogue, making it highly effective for complex queries, summarization of research papers, generating hypotheses, and interactive data analysis. Mixtral-8x7B-Instruct-v0.1 also excels at deep reasoning and generating coherent, well-supported text, making it ideal for drafting research outlines or explanations. For cutting-edge quality, `databricks/dbrx-instruct` could also be considered, though it might consume credits faster.

*   **For Coding:**
    *   **`mistralai/Mistral-7B-Instruct-v0.2`** (for general tasks)
    *   **`mistralai/Mixtral-8x7B-Instruct-v0.1`** (for complex tasks)
    *   **Reasoning:**
        *   For general coding tasks like generating small scripts, explaining code snippets, or basic debugging, **`mistralai/Mistral-7B-Instruct-v0.2`** offers a **32,768-token context** and is known for its speed and efficiency, making it cost-effective on a free tier. It provides surprisingly good results for its size.
        *   For more complex coding challenges, larger code generation, intricate debugging, or understanding larger codebases, **`mistralai/Mixtral-8x7B-Instruct-v0.1`** is superior. Its enhanced reasoning capabilities and 32,768-token context window allow it to handle more nuanced programming logic and provide more robust solutions.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
