# ============================================================
# LoRA Fine-Tuning with PEFT — bigscience/bloomz-560m
# ============================================================

# ── Step 1: Install libraries ────────────────────────────────
# Run these in your terminal or notebook cell:
#   pip install peft==0.4.0
#   pip install datasets
#   mkdir -p ../cache/working

# ── Step 2: Load model and tokenizer ────────────────────────
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigscience/bloomz-560m"

tokenizer = AutoTokenizer.from_pretrained(model_name)
foundation_model = AutoModelForCausalLM.from_pretrained(model_name)

# ── Step 3: Load and preprocess dataset ─────────────────────
# Using the "Abirate/english_quotes" dataset (has a "quote" column)
data = load_dataset("Abirate/english_quotes", split="train").shuffle(seed=42)
data = data.select(range(int(len(data) * 0.1)))          # Sample 10%
data = data.map(lambda samples: tokenizer(samples["quote"]), batched=True)

train_sample = data.select(range(5))
print(train_sample)

# ── Step 4: Configure LoRA ───────────────────────────────────
import peft
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=1,                          # Low rank — keeps adapter small
    lora_alpha=1,                 # Scaling factor (usually 1 for r=1)
    target_modules=["query_key_value"],   # BLOOM's combined QKV projection layer
    lora_dropout=0.05,            # Light dropout for regularisation
    bias="none",                  # Don't train bias terms
    task_type="CAUSAL_LM"
)

# ── Step 5: Apply LoRA to the foundation model ───────────────
peft_model = get_peft_model(foundation_model, lora_config)
print(peft_model.print_trainable_parameters())
# Expect ~0.1% trainable params — that's the whole point of LoRA!

# ── Step 6 & 7: Training arguments and Trainer ──────────────
import transformers
from transformers import TrainingArguments, Trainer
import os

output_directory = os.path.join("../cache/working", "peft_lab_outputs")
os.makedirs(output_directory, exist_ok=True)

training_args = TrainingArguments(
    report_to="none",                  # Don't log to W&B / TensorBoard
    output_dir=output_directory,
    auto_find_batch_size=True,         # Auto-reduce batch size if OOM
    learning_rate=3e-2,                # Higher LR than full fine-tuning
    num_train_epochs=1,                # 1 epoch is enough for demonstration
    use_cpu=True                       # Force CPU (remove if GPU is available)
)

trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=train_sample,        # Using the 5-sample demo set
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

# ── Step 8: Save the fine-tuned LoRA model ──────────────────
import time

time_now = int(time.time())
peft_model_path = os.path.join(output_directory, f"peft_model_{time_now}")
trainer.model.save_pretrained(peft_model_path)
print(f"Model saved to: {peft_model_path}")

# ── Step 9: Load saved LoRA model for inference ──────────────
from peft import PeftModel

# Re-load the base model and attach the saved LoRA adapter
loaded_model = PeftModel.from_pretrained(
    AutoModelForCausalLM.from_pretrained(model_name),   # fresh base model
    peft_model_path,                                     # path to saved adapter
    is_trainable=False                                   # inference only
)
print("LoRA model loaded for inference.")

# ── Step 10: Generate text ───────────────────────────────────
inputs = tokenizer("Two things are infinite: ", return_tensors="pt")

outputs = loaded_model.generate(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"],
    max_new_tokens=50,        # How many tokens to generate
    do_sample=True,           # Enable sampling for varied output
    temperature=0.7,          # Lower = more focused, higher = more creative
    top_p=0.9,                # Nucleus sampling threshold
    repetition_penalty=1.1    # Penalise repeated phrases
)

print(tokenizer.batch_decode(outputs, skip_special_tokens=True))