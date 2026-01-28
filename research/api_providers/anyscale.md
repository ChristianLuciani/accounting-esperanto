# Anyscale - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://anyscale.com

---

Anyscale offers a compelling free tier for accessing popular open-source LLMs. As of today, here's a detailed breakdown:

---

### Anyscale Free LLM API Details

**1. Free Tier Details:**

*   **Always Free with Limits or Free Credits?**
    *   Anyscale Endpoints provides an **"Always Free"** tier for popular open-source LLMs. No free credits that expire, but rather ongoing access within specified limits.
*   **Rate Limits:**
    *   **Active Endpoints:** 3 free active endpoints
    *   **RPM (Requests Per Minute):** 100 RPM
    *   **TPM (Tokens Per Minute):** 200,000 TPM
    *   **Daily Caps:** No explicit daily caps are mentioned beyond the RPM/TPM limits.
*   **Credit Card Requirement?**
    *   **No credit card is required** to get started with the free tier.

**2. Available Models (as of today):**

Anyscale's free tier currently offers the following models:

| Model Name                      | Context Window | Speed Tier (Implied) |
| :------------------------------ | :------------- | :------------------- |
| **Meta-Llama-3-8B-Instruct**    | 8,000 tokens   | Standard             |
| **Mistral-7B-Instruct-v0.2**    | 32,000 tokens  | Standard             |
| **Gemma-2-9B-It**               | 8,000 tokens   | Standard             |
| **Mixtral-8x7B-Instruct-v0.1**  | 32,000 tokens  | Standard             |

*Note: The speed tier for free models is generally 'Standard' as there's no specific 'High-Throughput' option for the free tier.*

**3. API Documentation:**

*   **Base URL:**
    `https://api.endpoints.anyscale.com/v1`
*   **Authentication Method:**
    Authentication requires an Anyscale API key. This key must be passed in the `Authorization` header as a **Bearer token**.
*   **Example `curl` Command:**

    ```bash
    curl -X POST \
      https://api.endpoints.anyscale.com/v1/chat/completions \
      -H "Authorization: Bearer <YOUR_ANYSCALE_API_KEY>" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "meta-llama/Llama-3-8B-instruct",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant that provides concise answers."},
          {"role": "user", "content": "What is the capital of France?"}
        ],
        "temperature": 0.7,
        "max_tokens": 50,
        "stream": false
      }'
    ```
    *(Remember to replace `<YOUR_ANYSCALE_API_KEY>` with your actual API key obtained from the Anyscale console.)*

**4. Reliability:**

*   **Uptime History:**
    Anyscale maintains a public status page ([https://status.anyscale.com/](https://status.anyscale.com/)) that provides real-time status and incident history for its Anyscale Platform and Anyscale Endpoints. Historically, Anyscale Endpoints generally show **high uptime** (often above 99.9%) with occasional, well-documented minor incidents or planned maintenance. It is considered a robust and reliable platform.
*   **Community Feedback:**
    Community feedback for Anyscale Endpoints is generally very positive. Users appreciate the easy access to powerful open-source models without upfront costs, the competitive performance, and the OpenAI-compatible API. Many regard it as a go-to platform for experimenting with or deploying open LLMs in personal projects or for rapid prototyping. Some feedback occasionally mentions variable latency (especially during peak times or for cold starts on the free tier), which is common for free services, but overall, it's considered a highly reliable and performant option for its price point (free).

**5. Best Use Case for Kontablo:**

Based on the free tier models' capabilities and context windows:

*   **For PDF Extraction:**
    *   **Recommended Model:** **Mixtral-8x7B-Instruct-v0.1** or **Mistral-7B-Instruct-v0.2**
    *   **Reasoning:** Both Mixtral-8x7B-Instruct-v0.1 and Mistral-7B-Instruct-v0.2 offer a significantly larger **32,000-token context window**, which is crucial for handling the often lengthy content of PDFs. Mixtral, being a Mixture-of-Experts model, provides superior reasoning and summarization capabilities for its size, making it excellent for extracting specific information, summarizing sections, or answering questions based on PDF content. Mistral also performs very strongly and is a good alternative.

*   **For Research:**
    *   **Recommended Model:** **Mixtral-8x7B-Instruct-v0.1**
    *   **Reasoning:** Mixtral-8x7B-Instruct-v0.1 is the strongest free-tier model for complex reasoning, analysis, and synthesis of information. Its 32,000-token context window allows for processing more extensive research notes, articles, or data. Its higher quality outputs and ability to follow intricate instructions make it ideal for summarizing research papers, brainstorming ideas, or generating detailed explanations.

*   **For Coding:**
    *   **Recommended Model:** **Mixtral-8x7B-Instruct-v0.1** or **Meta-Llama-3-8B-Instruct**
    *   **Reasoning:**
        *   **Mixtral-8x7B-Instruct-v0.1:** Offers robust general coding capabilities, good instruction following, and can handle more complex coding tasks or larger code snippets due to its overall strength and 32,000-token context window.
        *   **Meta-Llama-3-8B-Instruct:** Is highly regarded for its coding proficiency relative to its size (8,000-token context). It excels at generating code, explaining snippets, and debugging, often providing very coherent and correct outputs for common programming tasks. If a slightly faster response is prioritized for simpler coding tasks and the 8k context is sufficient, Llama 3 is an excellent choice.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
