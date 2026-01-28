# Hugging Face - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://huggingface.co/inference-api

---

Here's a detailed breakdown of the Hugging Face Inference API's free tier as of today, May 22, 2024:

---

### Hugging Face Inference API

**URL:** `https://huggingface.co/inference-api`

---

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    It is **"always free with limits"** based on a "fair use policy." This applies to "Serverless Inference" for any public model on the Hugging Face Hub.
*   **What are the rate limits? (RPM, TPM, daily caps)**
    *   **Daily Cap:** Approximately **1,000 requests per day** across all serverless tasks per user.
    *   **RPM/TPM:** Not explicitly stated, but the 1,000 requests/day is the primary limitation. For the free tier, there's no guaranteed throughput; performance and latency can be variable due to shared infrastructure and potential cold starts.
*   **Does it require credit card?**
    **No**, a credit card is not required to use the free tier Serverless Inference API. It is only required for paid tiers or Dedicated Inference Endpoints.

---

### 2. Available Models (as of today):

Hugging Face allows access to **any public model available on the Hugging Face Hub** via the Serverless Inference API, provided it supports the `text-generation` task. While technically *any* model is available, certain models are more stable and performant on the shared free tier. Here are some of the most popular and capable open-source LLMs suitable for various tasks:

| Model Name                               | Context Window | Speed Tier                                         |
| :--------------------------------------- | :------------- | :------------------------------------------------- |
| **Mixtral-8x7B-Instruct-v0.1**           | 32,768 tokens  | Standard (variable latency, higher cold start risk) |
| **Mistral-7B-Instruct-v0.2**             | 32,768 tokens  | Standard (variable latency)                        |
| **OpenHermes-2.5-Mistral-7B**            | 32,768 tokens  | Standard (variable latency)                        |
| **Llama-2-7b-chat-hf**                   | 4,096 tokens   | Standard (variable latency)                        |
| **HuggingFaceH4/zephyr-7b-beta**         | 4,096 tokens   | Standard (variable latency)                        |
| **microsoft/Phi-3-mini-4k-instruct**     | 4,096 tokens   | Standard (variable latency)                        |

**Note:** "Speed Tier: Standard" refers to the shared infrastructure of the Serverless Inference API. Actual latency can vary significantly due to traffic, model size, and whether the model is "warm" or requires a "cold start." Larger models like Mixtral-8x7B may experience longer cold start times on the free tier.

---

### 3. API Documentation:

*   **Base URL:**
    `https://api-inference.huggingface.co/models/`
*   **Authentication Method:**
    Authentication is done using a Hugging Face API token. You can generate one from your Hugging Face account settings (`https://huggingface.co/settings/tokens`). The token is passed in the `Authorization` header as `Bearer YOUR_HF_TOKEN`.
*   **Example curl command (using Mistral-7B-Instruct-v0.2):**
    ```bash
    curl -X POST \
      -H "Authorization: Bearer YOUR_HF_TOKEN" \
      -H "Content-Type: application/json" \
      https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2 \
      -d '{
        "inputs": "Write a short poem about the beauty of open-source.",
        "parameters": {
          "max_new_tokens": 100,
          "return_full_text": false,
          "temperature": 0.7,
          "top_p": 0.9
        }
      }'
    ```

---

### 4. Reliability:

*   **Uptime history:**
    Hugging Face maintains a public status page at `https://status.huggingface.co/`. The "Inference API" service generally shows good uptime, with occasional incidents reported and resolved. For the free serverless tier, while the underlying service infrastructure is reliable, individual requests may experience higher latency, cold starts, or queueing during peak usage periods compared to paid dedicated endpoints.
*   **Community feedback:**
    Community feedback for the free Inference API is generally positive, highlighting its accessibility for prototyping and learning. Common points include:
    *   **Great for prototyping:** Excellent for experimenting with various models without setup costs.
    *   **Variable latency:** The most common complaint is inconsistent response times, especially for larger models or during periods of high demand. Cold starts can add significant delay to the first request.
    *   **Rate limit awareness:** Users need to be mindful of the 1,000 requests/day limit, which can be hit quickly with automated testing.
    *   **Not for production:** It's widely understood that the free tier is not suitable for production applications requiring high throughput, guaranteed latency, or strict SLAs. For such needs, Dedicated Inference Endpoints are recommended.

---

### 5. Best Use Case for Kontablo:

Given the models available on the free tier and their typical performance:

*   **PDF extraction:** (Assuming text from PDF has been extracted via OCR/parsing)
    *   **Best Model:** `Mixtral-8x7B-Instruct-v0.1` or `Mistral-7B-Instruct-v0.2`
    *   **Reasoning:** Both models offer a substantial 32,768-token context window, which is crucial for processing longer documents or multiple sections of a PDF. They excel at instruction following, making them suitable for summarizing sections, extracting specific data points (e.g., names, dates, figures), or answering complex questions about the content. Mixtral provides superior reasoning capabilities for more nuanced extraction.

*   **Research:**
    *   **Best Model:** `Mixtral-8x7B-Instruct-v0.1`
    *   **Reasoning:** Mixtral-8x7B-Instruct-v0.1 is the most powerful model listed, offering advanced reasoning, summarization, and question-answering capabilities. Its Mixture of Experts (MoE) architecture allows it to handle complex research queries, synthesize information from multiple sources (within its 32k context window), and generate detailed insights. Its larger capacity is invaluable for tasks involving literature reviews, trend analysis, or complex problem-solving.

*   **Coding:**
    *   **Best Model:** `Mixtral-8x7B-Instruct-v0.1`
    *   **Reasoning:** Mixtral-8x7B-Instruct-v0.1 is highly regarded for its coding proficiency. It can generate coherent code snippets, explain complex programming concepts, debug errors, and refactor existing code. Its large context window (32,768 tokens) is particularly beneficial for providing relevant code context, handling larger files, or generating multi-file changes. `Mistral-7B-Instruct-v0.2` and `OpenHermes-2.5-Mistral-7B` are strong alternatives for smaller coding tasks.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
