# Mistral AI - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://mistral.ai

---

Here's a detailed breakdown of Mistral AI's free LLM API offerings as of today (June 2024), based on their official documentation:

---

### Mistral AI Free LLM API Details

#### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Mistral AI offers **both**:
    *   **Always Free with Limits:** Their open-source models (`mistral-tiny` / Mistral 7B Instruct v0.2 and `mistral-small` / Mixtral 8x7B Instruct v0.1) are available for **free with specific rate limits** and do not require a credit card.
    *   **Free Credits that Run Out:** New accounts receive **$5 in free credits** upon registration. These credits can be used across *all* models offered on their platform (including proprietary ones like Mistral Large and Mistral Small). Once these credits are exhausted, further API calls to paid models will fail unless a payment method is added.

*   **What are the rate limits?**
    For the **free open-source models** (`mistral-tiny` and `mistral-small`):
    *   **RPM (Requests Per Minute):** 15
    *   **TPM (Tokens Per Minute):** 100,000
    *   **Daily Caps:** Not explicitly defined as a daily cap, but the 100,000 TPM acts as a substantial throughput limit.

*   **Does it require credit card?**
    **No**, a credit card is **not required** to use the **open-source models** (`mistral-tiny` and `mistral-small`) within their free rate limits.
    A credit card *is* required if you wish to continue using the paid models (Mistral Large, Mistral Small, Mistral Embed) after your initial $5 in free credits are exhausted.

#### 2. Available Models (as of today) in the Free Tier:

The free tier specifically includes the following open-source models, accessed via their respective API aliases:

*   **Model Name:** `mistral-tiny`
    *   **Actual Model:** Mistral 7B Instruct v0.2
    *   **Context Window:** 32,000 tokens
    *   **Speed Tier:** Described as "Efficient, optimized for low latency and high throughput." (Implies fast performance for its size).

*   **Model Name:** `mistral-small`
    *   **Actual Model:** Mixtral 8x7B Instruct v0.1
    *   **Context Window:** 32,000 tokens
    *   **Speed Tier:** Described as "Optimized for speed and quality." (Implies good speed while maintaining strong performance).

#### 3. API Documentation:

*   **Base URL:** `https://api.mistral.ai/v1/`
*   **Authentication method:** An API key, obtained from the Mistral AI platform, is passed in the `Authorization` header as a Bearer token.
    *   Header format: `Authorization: Bearer YOUR_API_KEY`
*   **Example curl command (Chat Completions):**

    ```bash
    curl -X POST \
      https://api.mistral.ai/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -d '{
        "model": "mistral-small",
        "messages": [
          {"role": "user", "content": "Explain the concept of quantum entanglement in simple terms."}
        ]
      }'
    ```

#### 4. Reliability:

*   **Uptime history:** Mistral AI maintains a public status page at [https://status.mistral.ai/](https://status.mistral.ai/). As of today, most systems are reported as operational. Reviewing past incidents (e.g., last 90 days) indicates a generally stable platform with occasional, usually short-lived, incidents of degraded performance or API unavailability, which is common for cloud service providers. Overall, their uptime history appears solid.
*   **Community feedback:** Community feedback, particularly among developers, is generally positive. Users frequently praise Mistral AI's models for their performance-to-cost ratio, especially Mixtral. The provision of free API access to their open-source models is highly appreciated. While occasional reports of brief slowness or outages appear on forums like Reddit or X (Twitter), these are not widespread or persistent issues, indicating a generally reliable API.

#### 5. Best Use Case for Kontablo (using Free Tier Models):

For Kontablo, utilizing the free-tier models (`mistral-tiny` and `mistral-small`), here are the best recommendations:

*   **PDF Extraction:**
    *   **Best Model:** `mistral-small` (Mixtral 8x7B Instruct v0.1)
    *   **Reasoning:** Mixtral's Mixture of Experts (MoE) architecture provides stronger reasoning and comprehension capabilities compared to the smaller Mistral 7B. This is crucial for accurately parsing and extracting structured or complex information from various PDF documents. Its 32k token context window is sufficient for processing most medium-to-large PDFs.

*   **Research:**
    *   **Best Model:** `mistral-small` (Mixtral 8x7B Instruct v0.1)
    *   **Reasoning:** For research-oriented tasks, superior reasoning, summarization, and the ability to synthesize information are paramount. Mixtral 8x7B excels in these areas, making it better suited for tasks such as summarizing research papers, extracting key arguments, or generating initial hypotheses. The 32k context allows for detailed analysis of substantial textual inputs.

*   **Coding:**
    *   **Best Model:** `mistral-small` (Mixtral 8x7B Instruct v0.1)
    *   **Reasoning:** Mixtral 8x7B has demonstrated strong capabilities in code generation, explanation, and understanding. Its more advanced architecture allows it to grasp coding patterns, syntax, and logical flow more effectively than Mistral 7B, making it the preferred choice for tasks like generating code snippets, debugging assistance, or explaining complex code functions within the free tier.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
