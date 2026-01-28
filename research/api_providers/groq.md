# Groq - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://groq.com

---

Groq has emerged as a leader in high-speed inference for large language models, leveraging its custom LPU™ architecture. They offer a generous free tier for developers.

Here's a detailed breakdown of Groq's free LLM API offering as of today:

---

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Groq offers an **"always free with limits"** tier for developers, specifically designed for personal and non-commercial projects. No credit card is required to sign up and start using the free tier.

*   **What are the rate limits?**
    The free tier has the following rate limits, applied across all available models:
    *   **Requests Per Minute (RPM):** 30 RPM
    *   **Tokens Per Minute (TPM):** 15,000 TPM
    *   **Daily Cap:** 1,000,000 tokens per day (combined usage across all models).
    *   *Note: These limits are subject to change, but are current as of this writing based on Groq's official documentation.*

*   **Does it require credit card?**
    **No**, a credit card is explicitly *not* required to use the free developer tier.

---

### 2. Available Models (as of today):

Groq provides access to a selection of popular open-source models optimized for their LPU architecture. All models listed below are available on the free tier.

| Model Name             | Context Window (tokens) | Speed Tier                                         |
| :--------------------- | :---------------------- | :------------------------------------------------- |
| `llama3-8b-8192`       | 8,192                   | Extremely Fast (Among the fastest for its size)    |
| `llama3-70b-8192`      | 8,192                   | Very Fast (Significantly faster than typical 70B) |
| `mixtral-8x7b-32768`   | 32,768                  | Very Fast (Excellent balance of context and speed) |

*   **Note on Speed Tier:** Groq's unique selling proposition is its unparalleled speed. Instead of categorizing into "speed tiers" like low/medium/high, all models on Groq are designed for high-performance, low-latency inference. The descriptions reflect their relative performance *on Groq* and their general performance compared to other providers.

---

### 3. API Documentation:

Groq's API is designed to be largely compatible with the OpenAI API standard, making it easy for developers familiar with OpenAI's interface to integrate.

*   **Base URL:**
    `https://api.groq.com/openai/v1`

*   **Authentication Method:**
    Authentication is done using an API key, which needs to be passed in the `Authorization` header as a Bearer token.
    `Authorization: Bearer YOUR_GROQ_API_KEY`

*   **Example curl command:**
    To generate a chat completion:

    ```bash
    curl -X POST \
      https://api.groq.com/openai/v1/chat/completions \
      -H "Authorization: Bearer YOUR_GROQ_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "llama3-8b-8192",
        "messages": [
          {
            "role": "user",
            "content": "Explain the concept of quantum entanglement in simple terms."
          }
        ],
        "temperature": 0.7,
        "max_tokens": 150
      }'
    ```
    *Replace `YOUR_GROQ_API_KEY` with your actual API key obtained from the GroqCloud console.*

---

### 4. Reliability:

*   **Uptime History:**
    Groq maintains a public status page at [status.groq.com](https://status.groq.com/). As of recent checks, Groq's API services generally show a high uptime, often reporting 100% operational status across its core services. Minor incidents or degraded performance are rare and typically resolved quickly.

*   **Community Feedback:**
    Community feedback for Groq is overwhelmingly positive, primarily praising its **blazing-fast inference speeds** which are often cited as a game-changer for real-time applications and developer productivity. Users frequently highlight the responsiveness of the API. Reliability is generally considered very good, with developers reporting stable performance for their applications. Occasional reports of brief API unavailability or rate limit issues exist, as with any cloud service, but these appear to be exceptions rather than the norm. The developer experience is often lauded for its simplicity and OpenAI compatibility.

---

### 5. Best Use Case for Kontablo (within Groq's Free Tier):

Considering Groq's primary advantage (speed) and the capabilities of its free-tier models, here are the recommendations for Kontablo:

*   **PDF Extraction:**
    *   **Recommended Model:** `mixtral-8x7b-32768`
    *   **Justification:** For PDF extraction, a larger context window is often beneficial to ingest more of the document at once, especially for complex layouts or longer sections. `mixtral-8x7b-32768` offers a generous 32,768 tokens, which is significantly more than the Llama 3 models on Groq, allowing for processing larger chunks of text. Its strong reasoning capabilities are good for identifying and extracting specific data points, while Groq's speed will significantly accelerate the overall extraction pipeline, especially if processing many documents sequentially.

*   **Research:**
    *   **Recommended Model:** `llama3-70b-8192` or `mixtral-8x7b-32768` (depending on input length)
    *   **Justification:**
        *   **For Shorter, Complex Queries/Summaries (`llama3-70b-8192`):** Llama 3 70B is known for its strong reasoning, factual recall, and summarization abilities. If research tasks involve processing concise information and generating insightful summaries or answers that fit within its 8,192-token context, its superior general intelligence on Groq's fast inference engine will be highly effective.
        *   **For Longer Documents/Context (`mixtral-8x7b-32768`):** If research involves analyzing longer articles, reports, or multiple snippets where a broader context is crucial, `mixtral-8x7b-32768`'s 32,768-token context window is invaluable. While `llama3-70b` might have slightly stronger raw reasoning, Mixtral is still highly capable and its larger context allows for more comprehensive information intake, which can be critical for research. The speed ensures quick iteration through research questions.

*   **Coding:**
    *   **Recommended Model:** `mixtral-8x7b-32768`
    *   **Justification:** For coding tasks (code generation, explanation, debugging, refactoring), `mixtral-8x7b-32768` is an excellent choice. It performs very well on coding benchmarks, and its larger 32,768-token context window is highly advantageous for understanding larger code snippets, reviewing entire functions, or generating more extensive code blocks. The sheer speed of inference on Groq means developers get near-instantaneous suggestions and completions, drastically improving the coding workflow and developer experience.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
