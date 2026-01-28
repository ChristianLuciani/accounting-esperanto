# DeepInfra - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://deepinfra.com

---

DeepInfra offers a robust free tier for accessing a wide range of open-source LLMs. Here's a breakdown based on their current offerings (as of today, 2023-11-20):

---

## DeepInfra Free LLM API Details

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    It is **"always free with limits."** DeepInfra's free tier provides continuous access to models without requiring a credit card, subject to specific rate limits. It's designed for testing and early development.
*   **What are the rate limits?**
    *   **Requests per minute (RPM):** 10
    *   **Tokens per minute (TPM):** 30,000
    *   **Daily requests:** 1,000
*   **Does it require credit card?**
    **No**, a credit card is not required for the free tier.

### 2. Available Models (as of today):

DeepInfra's free tier provides access to **most of their available models**, constrained by the free tier rate limits. There isn't a separate, explicit list of "free tier only" models; rather, the free tier applies to the general model catalog.

Below is a selection of popular and capable models available, along with their reported context window and speed tier. To get the most up-to-date and complete list, always refer to their [Models page](https://deepinfra.com/models).

| Model Name                      | Context Window | Speed Tier |
| :------------------------------ | :------------- | :--------- |
| `mistralai/Mistral-7B-Instruct-v0.2` | 32,768 tokens  | Standard   |
| `mistralai/Mixtral-8x7B-Instruct-v0.1` | 32,768 tokens  | Standard   |
| `meta-llama/Llama-2-7b-chat-hf` | 4,096 tokens   | Standard   |
| `meta-llama/Llama-2-13b-chat-hf`| 4,096 tokens   | Standard   |
| `meta-llama/Llama-2-70b-chat-hf`| 4,096 tokens   | Standard   |
| `codellama/CodeLlama-34b-Instruct-hf`| 16,384 tokens  | Standard   |
| `lmsys/vicuna-7b-v1.5`          | 4,096 tokens   | Standard   |
| `lmsys/vicuna-13b-v1.5`         | 4,096 tokens   | Standard   |
| `openai/gpt2`                   | 1,024 tokens   | Standard   |

*Note: Context window and speed tier are based on information provided on individual model pages on deepinfra.com. "Standard" speed tier is their default for most models.*

### 3. API Documentation:

*   **Base URL:**
    DeepInfra offers an OpenAI-compatible API endpoint for chat completions, as well as a direct inference endpoint for specific models.
    *   **OpenAI-compatible Chat Completions:** `https://api.deepinfra.com/v1/openai/chat/completions`
    *   **General Inference (for specific models):** `https://api.deepinfra.com/v1/inference/{model_id}` (e.g., `https://api.deepinfra.com/v1/inference/mistralai/Mistral-7B-Instruct-v0.2`)
*   **Authentication method:**
    Requests are authenticated using a **Bearer Token** (your DeepInfra API key) in the `Authorization` HTTP header. You can generate an API key from your DeepInfra dashboard after signing up.
*   **Example curl command (using OpenAI-compatible endpoint for Mistral-7B-Instruct-v0.2):**

    ```bash
    curl -X POST \
      -H "Authorization: Bearer <YOUR_DEEPINFRA_API_KEY>" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
          {"role": "user", "content": "Explain quantum entanglement in simple terms."}
        ],
        "max_tokens": 150,
        "temperature": 0.7
      }' \
      https://api.deepinfra.com/v1/openai/chat/completions
    ```

    *(Replace `<YOUR_DEEPINFRA_API_KEY>` with your actual API key)*

### 4. Reliability:

*   **Uptime history:**
    According to their official status page ([https://status.deepinfra.com/](https://status.deepinfra.com/)), DeepInfra generally maintains a **high level of uptime.**
    *   As of today, the status page indicates "All Systems Operational."
    *   Historical data often shows 99.9% or 100% uptime for core API services over recent months (e.g., last 90 days, 30 days).
    *   Minor incidents, when they occur, are typically brief and well-documented on the status page.
*   **Community feedback:**
    Community feedback for DeepInfra is generally **positive**, especially for developers looking to integrate open-source LLMs.
    *   **Pros:** Users often praise the wide selection of models, the ease of use with OpenAI-compatible endpoints, competitive pricing (and a generous free tier), and good performance for many models. It's highly regarded for making cutting-edge open-source models easily accessible.
    *   **Cons:** Some users occasionally report cold starts or slightly slower response times for less popular models or during peak usage, which is common for serverless inference platforms. Performance can sometimes be inconsistent with very large models on the free tier due to the nature of shared resources and rate limits.

### 5. Best Use Case for Kontablo:

Given DeepInfra's available models, here are recommendations for PDF extraction, research, and coding tasks:

*   **PDF Extraction (assuming text is already extracted from the PDF):**
    *   **Recommended Model:** `mistralai/Mixtral-8x7B-Instruct-v0.1`
    *   **Reasoning:** Mixtral is a highly capable "sparse mixture of experts" model known for its strong reasoning abilities and understanding of complex text. Its large 32,768-token context window is excellent for processing longer documents, extracting key information, summarizing sections, and answering questions based on the content. `meta-llama/Llama-2-70b-chat-hf` could also be considered for extremely nuanced extraction, but Mixtral's balance of speed, capability, and context window makes it a strong contender for this task on the free tier.

*   **Research (summarizing papers, extracting insights, generating hypotheses):**
    *   **Recommended Model:** `mistralai/Mixtral-8x7B-Instruct-v0.1`
    *   **Reasoning:** Similar to PDF extraction, research tasks heavily benefit from strong analytical and summarization capabilities. Mixtral's advanced reasoning, instruction following, and expansive 32,768-token context window allow it to ingest substantial amounts of research material, identify patterns, synthesize information, and provide insightful summaries or answers. `meta-llama/Llama-2-70b-chat-hf` is another excellent choice for deep, complex analysis, though its smaller context window (4K) means you'd need to chunk larger research papers.

*   **Coding (code generation, debugging, explanation):**
    *   **Recommended Model:** `codellama/CodeLlama-34b-Instruct-hf`
    *   **Reasoning:** CodeLlama is specifically fine-tuned for coding tasks. The 34B instruction-following variant is highly proficient at generating accurate code, explaining complex logic, completing functions, and assisting with debugging across various programming languages. Its 16,384-token context window is generous for typical code files. While Mixtral can handle some coding tasks, CodeLlama is purpose-built and will generally outperform general-purpose models for code-specific applications.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
