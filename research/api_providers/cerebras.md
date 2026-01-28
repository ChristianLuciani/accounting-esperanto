# Cerebras - Free Tier Research

**Research Date:** 2026-01-27
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** https://cerebras.ai

---

After thoroughly reviewing the Cerebras website (https://cerebras.ai) as of today, it's important to clarify Cerebras's offering in the context of LLM APIs.

**Cerebras primarily operates as an AI hardware company that provides enterprise-level AI Cloud solutions for training and inference, powered by their Wafer-Scale Engine (WSE) technology.** They do not appear to offer a public, self-service, free-tier LLM API in the same vein as providers like OpenAI, Anthropic, Groq, or Together.ai, where a developer can sign up, get an API key, and start making requests for free or on a pay-as-you-go basis.

Their "Cerebras AI Cloud" is an enterprise offering for large-scale, private model inference and fine-tuning, not a public API endpoint for general developers.

Therefore, many of the requested details for a "free LLM API" are not applicable to Cerebras's current public offerings.

---

Here's a breakdown based on their publicly available information:

### PROVIDER: Cerebras (https://cerebras.ai)

---

### 1. Free Tier Details:

*   **Is it "always free with limits" or "free credits that run out"?**
    Cerebras does **not appear to offer a public, self-service free-tier LLM API.** Their "Cerebras AI Cloud" is an enterprise-focused service for organizations to deploy and run large models on Cerebras hardware. It operates on a contractual or bespoke pricing model, not a public free tier or pay-as-you-go.
*   **What are the rate limits? (RPM, TPM, daily caps)**
    As there is no public free-tier API, there are no publicly advertised rate limits for such a service. Enterprise clients would have these terms defined in their service agreements.
*   **Does it require credit card?**
    For a public API, this is not applicable as there is no public sign-up process for a free or paid API tier. Access to Cerebras AI Cloud is typically arranged through direct sales and enterprise contracts.

---

### 2. Available Models (as of today):

Since there is no public free-tier API, there are no models available through such an interface for individual developers.

However, the **Cerebras AI Cloud** (for enterprise clients) supports running various large models, leveraging the Cerebras WSE-3 hardware for high-performance inference. While they don't list specific context windows or speed tiers for general consumption (as it's a managed enterprise service), they mention supporting:

*   **Llama 3 70B**
*   **Mixtral 8x7B**
*   And other popular large open-source models, which can be deployed privately for enterprise use.

These models are *not* accessible via a free, public API key.

---

### 3. API Documentation:

*   **Base URL:** Not applicable, as there is no public API.
*   **Authentication method:** Not applicable.
*   **Example curl command:** Not applicable.

Enterprise clients utilizing the Cerebras AI Cloud would receive specific, private API access details and documentation as part of their service agreement, which would be tailored to their deployment.

---

### 4. Reliability:

*   **Uptime history (if available):**
    There is no public uptime history or status page for a general-purpose LLM API from Cerebras, as such a service does not exist. Reliability for their enterprise AI Cloud would be governed by Service Level Agreements (SLAs) with individual clients.
*   **Community feedback:**
    Community feedback regarding Cerebras generally pertains to their groundbreaking hardware (WSE), their contributions to AI research, and their enterprise-level AI supercomputing solutions, rather than direct developer experience with an LLM API. There isn't a readily available body of community feedback on a public Cerebras LLM API because it's not a public offering.

---

### 5. Best Use Case for Kontablo:

**Given that Cerebras does not offer a public, free-tier LLM API, it is not a suitable provider for "Kontablo" (assuming Kontablo is an individual developer or small team looking for direct API access).**

Cerebras's solutions are geared towards large enterprises requiring custom deployments of powerful LLMs on dedicated high-performance hardware.

For use cases like:

*   **PDF extraction:**
*   **Research:**
*   **Coding:**

Kontablo would be much better served by providers that offer accessible free tiers or clear pay-as-you-go models with public APIs, such as:
*   **OpenAI** (GPT-3.5 Turbo, GPT-4o)
*   **Anthropic** (Claude 3 Haiku, Sonnet, Opus)
*   **Groq** (Llama 3 8B/70B, Mixtral 8x7B)
*   **Together.ai** (various open-source models like Llama, Mixtral, Qwen)
*   **Anyscale Endpoints** (various open-source models)
*   **Google Gemini API** (Gemini 1.5 Pro)

These providers offer documented APIs, clear pricing (including free tiers or substantial free credits), and are designed for developers to integrate LLMs into their applications directly.

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
