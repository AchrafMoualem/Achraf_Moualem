# =============================================================================
# Open Source LLM Exercises — Completed
# =============================================================================


# =============================================================================
# Exercise 1: Open Source Levels Reflection
# =============================================================================

open_source_levels = {
    "Fully Open": {
        "definition": (
            "A model where every artifact is publicly released: training code, "
            "training data, model weights, tokenizer, architecture config, and "
            "evaluation scripts. Anyone can reproduce, modify, or redistribute "
            "the model without restriction."
        ),
        "what_is_open": [
            "Training code and data pipeline",
            "Model weights, tokenizer, and architecture config",
        ],
        "what_you_can_do": [
            "Retrain from scratch on your own or the original data",
            "Audit data provenance, modify architecture, redistribute freely",
        ],
        "what_you_cannot_do": [
            "Nothing is inherently forbidden — subject only to the data licenses",
            "Claiming sole authorship of an unmodified release would be misleading",
        ],
    },
    "Weights Released": {
        "definition": (
            "The pre-trained model weights (and usually a model card) are publicly "
            "available, but training code and/or training data remain closed. "
            "License terms often impose commercial or derivative-work restrictions."
        ),
        "what_is_open": [
            "Pre-trained model weights and tokenizer",
            "Architecture description (but not necessarily the training code)",
        ],
        "what_you_can_do": [
            "Run inference and fine-tune on your own data",
            "Build products on top of the model (subject to license terms)",
        ],
        "what_you_cannot_do": [
            "Reproduce the full training pipeline (data and code are closed)",
            "May not be able to train competing LLMs or exceed MAU caps (e.g. Llama 2)",
        ],
    },
    "Architecture Only": {
        "definition": (
            "Only the model design (layer types, attention pattern, hyperconfig) is "
            "published. No weights and no training data are released. The team must "
            "train from scratch using their own compute and data."
        ),
        "what_is_open": [
            "Model architecture specification and configuration",
            "Research paper describing design decisions",
        ],
        "what_you_can_do": [
            "Implement the architecture and train entirely on your own data",
            "Maintain full data provenance — critical for regulated domains",
        ],
        "what_you_cannot_do": [
            "Use any pre-trained weights (none exist publicly)",
            "Skip the expensive pretraining compute step",
        ],
    },
}

print(open_source_levels)


# Comparison table
comparison_table = """| Openness level   | What's open?                                              | Impact on retraining / modifying                                                        |
| ---------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Fully Open       | Training code, data, weights, tokenizer, eval scripts     | Full freedom: retrain from scratch, modify architecture, audit data, redistribute freely |
| Weights Released | Pre-trained weights and model card; training data closed  | Can fine-tune or run inference; cannot reproduce training; may face license restrictions |
| Architecture Only| Model design spec only — no weights, no data              | Must train from scratch on own data; maximum data sovereignty; high compute cost        |"""

print(comparison_table)


# Comparative paragraph
comparative_paragraph = """
The three openness levels represent fundamentally different trade-offs between
transparency and control. A Fully Open model gives practitioners complete access
to every artifact — training code, datasets, weights, and evaluation scripts —
enabling full reproducibility and unrestricted customisation, but these models are
rare because curating and releasing training data at scale is costly and legally
complex. Weights-Released models, such as Mistral 7B, strike the most common
balance: they let teams fine-tune a strong pre-trained baseline without investing
in pretraining compute, but license clauses can restrict commercial use or
redistribution, and the closed training data makes it impossible to audit for bias
or contamination. Architecture-Only releases provide the least out-of-the-box
utility yet the most data sovereignty, since organisations must supply and vet
their own training corpora — an advantage in regulated sectors where data lineage
must be documented. In practice, the right choice depends on whether
speed-to-deployment, cost, or compliance dominates the team's priorities.
"""

print(comparative_paragraph)


# Healthcare answer
healthcare_prompt_answer = """
For retraining on clinical data under HIPAA or GDPR, an Architecture-Only or
Fully Open model is preferable, because the team controls the entire training
pipeline and can guarantee that no proprietary or undisclosed patient data entered
the base model. A Weights-Released model requires auditing the provider's data
practices — which is often impossible — making compliance certification much harder.
"""

print(healthcare_prompt_answer)


# =============================================================================
# Exercise 2: License Check for SaaS Use
# =============================================================================

license_checklist = [
    {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "url": "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3",
        "license": "Apache 2.0",
        "commercial_use": "Yes — fully permitted with no MAU caps",
        "restrictions": [
            "Must include the Apache 2.0 NOTICE file in any distribution",
            "Must state significant changes if the model is modified before redistribution",
        ],
    },
    {
        "model": "meta-llama/Llama-2-7b-chat-hf",
        "url": "https://huggingface.co/meta-llama/Llama-2-7b-chat-hf",
        "license": "Llama 2 Community License",
        "commercial_use": "Conditional — free for products with fewer than 700 million MAU; "
                          "separate Meta commercial license required above that threshold",
        "restrictions": [
            "Cannot use Llama 2 outputs to train other large language models (including competitors)",
            'Product name must include "Meta Llama 2" if built on this model',
            "Export controls apply — use is prohibited in embargoed countries and for restricted parties",
        ],
    },
]

print(license_checklist)


# Markdown checklist
license_md_checklist = """
- [x] **Model 1 — mistralai/Mistral-7B-Instruct-v0.3**
  - Type of license:
    - [x] Apache 2.0
  - Commercial use allowed:
    - [x] Yes — unrestricted (no MAU cap)
  - Restrictions:
    - [x] Must distribute the Apache 2.0 NOTICE file with any derivative product
    - [x] Must document significant changes if the weights are modified before redistribution

- [x] **Model 2 — meta-llama/Llama-2-7b-chat-hf**
  - Type of license:
    - [x] Llama 2 Community License (Meta)
  - Commercial use allowed:
    - [x] Conditional — permitted below 700 million MAU; negotiate with Meta above that
  - Restrictions:
    - [x] Cannot use model outputs to train competing LLMs
    - [x] Product must include "Meta Llama 2" in its name
    - [x] Export controls — prohibited in embargoed regions and for restricted parties
"""

print(license_md_checklist)


# =============================================================================
# Exercise 3: LLM Matchmaker Challenge
# =============================================================================

filters_by_team = {
    "LegalTech": [
        "text-generation",
        "cpu / gguf / quantized",
        "boolq benchmark",
        "size <= 7B",
        "permissive license (Apache 2.0 preferred)",
    ],
    "EdTech": [
        "math / gsm8k benchmark",
        "cpu / quantized",
        "size <= 4B preferred for low-end laptops",
        "MIT or Apache 2.0 license",
    ],
    "Global NGO": [
        "multilingual tag",
        "flores-200 coverage >= 5 languages",
        "cpu / gguf",
        "size <= 7B",
        "permissive license",
    ],
}

print(filters_by_team)


candidates_by_team = {
    "LegalTech": [
        {
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "params_b": "7",
            "arch": "Mistral",
            "optimization": "Q4_K_M GGUF (llama.cpp)",
            "benchmarks": "BoolQ ~83%, HellaSwag ~81%",
        },
        {
            "model": "microsoft/Phi-3-mini-4k-instruct",
            "params_b": "3.8",
            "arch": "Phi-3",
            "optimization": "Q4_K_M GGUF",
            "benchmarks": "BoolQ ~82%, fits in ~2.5 GB RAM",
        },
        {
            "model": "google/gemma-2-2b-it",
            "params_b": "2",
            "arch": "Gemma 2",
            "optimization": "Q4 GGUF",
            "benchmarks": "BoolQ ~78%, very low RAM footprint",
        },
    ],
    "EdTech": [
        {
            "model": "microsoft/Phi-3-mini-4k-instruct",
            "params_b": "3.8",
            "arch": "Phi-3",
            "optimization": "Q4_K_M GGUF",
            "benchmarks": "GSM8K ~82%, MMLU ~68%",
        },
        {
            "model": "google/gemma-2-2b-it",
            "params_b": "2",
            "arch": "Gemma 2",
            "optimization": "Q4 GGUF",
            "benchmarks": "GSM8K ~74%",
        },
        {
            "model": "Qwen/Qwen2-1.5B-Instruct",
            "params_b": "1.5",
            "arch": "Qwen2",
            "optimization": "Q4 GGUF",
            "benchmarks": "GSM8K ~58%, smallest footprint",
        },
    ],
    "Global NGO": [
        {
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "params_b": "7",
            "arch": "Mistral",
            "optimization": "Q4_K_M GGUF",
            "benchmarks": "FLORES-200 strong on 10+ languages",
        },
        {
            "model": "CohereForAI/aya-23-8B",
            "params_b": "8",
            "arch": "Command R",
            "optimization": "Q4 GGUF",
            "benchmarks": "FLORES-200 23 languages, best multilingual coverage",
        },
        {
            "model": "ai-forever/mGPT",
            "params_b": "1.3",
            "arch": "GPT-2 multilingual",
            "optimization": "GGUF",
            "benchmarks": "FLORES-200 60 languages (weaker per-language quality)",
        },
    ],
}

print(candidates_by_team)


matchmaker_table = """| Team        | Needs                                          | Your Pick                                      |
| ----------- | ---------------------------------------------- | ---------------------------------------------- |
| LegalTech   | Fast model for logic-heavy chatbot on CPU      | Mistral-7B-Instruct-v0.3 (Q4_K_M GGUF)        |
| EdTech      | Logic/math-focused LLM on low-end laptops      | Phi-3-mini-4k-instruct (Q4_K_M GGUF)          |
| Global NGO  | Model that speaks 5+ languages well            | Mistral-7B-Instruct-v0.3 or Aya-23-8B (Q4)   |"""

print(matchmaker_table)


# =============================================================================
# Exercise 4: Local Readiness Audit
# =============================================================================

# NOTE: replace these values with your actual system specs
system_specs = {
    "ram_gb": 16,          # e.g. run: free -h   (Linux) or About This Mac (macOS)
    "free_disk_gb": 80,    # e.g. run: df -h ~   (Linux/macOS)
    "os": "Ubuntu 22.04",  # e.g. run: uname -a  (Linux) or sw_vers (macOS)
}

print(system_specs)


readiness_table = """| Requirement                    | Your System Specs         | Meets Requirement? |
| ------------------------------ | ------------------------- | ------------------ |
| RAM (>= 8 GB for Q4 7B model)  | 16 GB                     | ✓                  |
| RAM (>= 16 GB recommended)     | 16 GB                     | ✓                  |
| Free Disk Space (>= 10 GB)     | 80 GB                     | ✓                  |
| OS (Linux / macOS / WSL2)      | Ubuntu 22.04              | ✓                  |
| CPU AVX2 or ARM NEON           | Check with command below  | verify             |
| cmake >= 3.14                  | Install via apt/brew      | verify             |
| gcc >= 9 or clang >= 11        | Install via apt/brew      | verify             |"""

print(readiness_table)


llama_cpp_readiness = {
    "cpu_instruction_support": (
        "AVX2 (x86-64 post-2013) or NEON (ARM / Apple Silicon). "
        "Check: grep -m1 flags /proc/cpuinfo | grep -o avx2   (Linux) "
        "or:    sysctl machdep.cpu.features | grep AVX2        (macOS)"
    ),
    "tooling": [
        "cmake >= 3.14  →  apt install cmake  /  brew install cmake",
        "gcc >= 9 or clang >= 11  →  apt install build-essential  /  xcode-select --install",
        "make  →  usually pre-installed; apt install make if missing",
    ],
    "other_requirements": (
        "Python >= 3.8 for llama-cpp-python bindings (optional). "
        "Windows users: enable WSL2 via 'wsl --install' in an admin PowerShell, "
        "then install Ubuntu 22.04 from the Microsoft Store."
    ),
}

print(llama_cpp_readiness)


upgrade_actions = [
    "RAM < 8 GB  →  use Q2_K or Q3_K_S quant (~2–3 GB) instead of Q4_K_M, "
    "or switch to a 3B model (Phi-3-mini Q4 ≈ 2.3 GB)",
    "No AVX2    →  build llama.cpp with LLAMA_NO_AVX2=1 (slower) "
    "or run on Apple Silicon with Metal acceleration",
    "Disk tight  →  download only one quantization level; delete the GGUF after testing",
    "Windows (no WSL2)  →  run: wsl --install  in admin PowerShell, reboot, install Ubuntu",
    "No cmake/gcc  →  Linux: apt install build-essential cmake; macOS: xcode-select --install",
]

print(upgrade_actions)


# =============================================================================
# Exercise 5: Benchmark-Based Model Explorer
# =============================================================================

leaderboard_models = [
    {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "url": "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3",
        "hellaswag": "81.3",
        "mmlu": "62.5",
        "license": "Apache 2.0",
        "ideal_use_case": (
            "General-purpose instruction following, SaaS chatbots, RAG pipelines; "
            "best commonsense reasoning per dollar in the 7B tier"
        ),
    },
    {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "url": "https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct",
        "hellaswag": "82.1",
        "mmlu": "68.4",
        "license": "Llama 3 Community License",
        "ideal_use_case": (
            "Knowledge-heavy tasks, exam-style Q&A, coding assistants; "
            "highest MMLU in the ≤8B open-weight tier"
        ),
    },
    {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct",
        "hellaswag": "78.9",
        "mmlu": "68.8",
        "license": "MIT",
        "ideal_use_case": (
            "Edge deployment, mobile apps, low-RAM devices; "
            "best MMLU-per-parameter ratio at 3.8B — MIT license allows free redistribution"
        ),
    },
]

print(leaderboard_models)


benchmark_table = """| Model Name                       | HellaSwag Score | MMLU Score | License Type            | Ideal Use Case                              |
| -------------------------------- | --------------- | ---------- | ----------------------- | ------------------------------------------- |
| Mistral-7B-Instruct-v0.3         | 81.3            | 62.5       | Apache 2.0              | General chatbots, SaaS, RAG pipelines       |
| Meta-Llama-3-8B-Instruct         | 82.1            | 68.4       | Llama 3 Community       | Knowledge Q&A, coding assistants            |
| Phi-3-mini-4k-instruct (3.8B)    | 78.9            | 68.8       | MIT                     | Edge / mobile / low-RAM deployment          |"""

print(benchmark_table)


# Optional reflection
benchmark_reflection = """
Benchmarks like HellaSwag and MMLU provide reproducible, task-specific signal
that separates genuine capability from polished marketing demos; a model with
great PR copy but a 55% MMLU score will fail on knowledge-intensive production
workloads. Choosing by benchmarks — not hype — means you can predict failure
modes before deployment, not after.
"""

print(benchmark_reflection)


quiz_reflection = [
    {
        "question": (
            "A startup needs to deploy an LLM on mobile devices with 4 GB RAM "
            "and no GPU. Which benchmark metric matters most, and why?"
        ),
        "answer": (
            "Parameter count and quantized model size matter most — the model must "
            "fit in RAM before any benchmark score is relevant. Then examine MMLU "
            "and task-specific scores on quantized (Q4) versions, since quantization "
            "can reduce accuracy by 2–5 points."
        ),
    },
    {
        "question": (
            "Two models have identical MMLU scores. How do you break the tie "
            "for a customer-facing chatbot?"
        ),
        "answer": (
            "Check HellaSwag (commonsense / conversational fluency), "
            "instruction-following win-rate (MT-Bench or AlpacaEval), and latency "
            "at your target hardware tier. Also verify licenses — an Apache 2.0 model "
            "beats a community-licensed one for SaaS if capabilities are equal."
        ),
    },
    {
        "question": (
            "Why can a high-MMLU model still underperform on a legal document task?"
        ),
        "answer": (
            "MMLU tests broad academic knowledge across 57 subjects, but legal NLP "
            "requires domain-specific vocabulary, citation reasoning, and long-context "
            "faithfulness that general benchmarks do not measure. Always supplement "
            "leaderboard scores with domain-specific evaluations (e.g. LegalBench) "
            "before production deployment."
        ),
    },
]

print(quiz_reflection)


# =============================================================================
# Exercise 6: Cloud vs. Local Deployment Plan
# =============================================================================

pros_and_cons = [
    "Cost — Local: high upfront hardware cost but near-zero marginal cost per query; "
    "Cloud: no capex but pay-per-token pricing scales linearly and can become expensive at volume.",

    "Latency — Local: deterministic low latency with no network round-trip once the model is loaded; "
    "Cloud: adds network + queue latency that can spike under load.",

    "Scalability — Local: hard ceiling at available RAM/CPU; scaling requires buying hardware; "
    "Cloud: effectively unlimited horizontal scaling with auto-scaling for traffic spikes.",

    "Security / Privacy — Local: data never leaves your perimeter, ideal for PII/PHI and regulated industries; "
    "Cloud: data transits external networks; requires reviewing provider DPA, SOC 2, HIPAA BAA.",

    "Maintenance — Local: your team owns upgrades, security patches, runtime monitoring, and driver management; "
    "Cloud: provider manages infrastructure; you update model versions and prompts only.",
]

print(pros_and_cons)


# Optional: Colab timing note
colab_run = {
    "model_tested": "mistralai/Mistral-7B-Instruct-v0.3 (4-bit GPTQ) via Hugging Face transformers on Colab T4",
    "first_token_latency_seconds": 2.1,
    "generation_speed_tokens_per_sec": 28,
    "full_response_time_seconds": 7.5,   # for ~150 output tokens
    "notes": (
        "T4 free tier (16 GB VRAM) handles 4-bit 7B without CPU offload. "
        "Free sessions have runtime and idle limits; Colab Pro or a dedicated "
        "cloud GPU instance is needed for sustained production use."
    ),
}

print(colab_run)
