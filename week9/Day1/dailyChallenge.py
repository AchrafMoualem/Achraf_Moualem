# ============================================================
# Multilingual NLI with BERT & XLM-RoBERTa
# Dataset: Contradictory, My Dear Watson (Kaggle)
# Labels: 0=Entailment, 1=Neutral, 2=Contradiction
# ============================================================

# ── Step 1: Install dependencies (run once) ──────────────────
# pip install transformers datasets scikit-learn torch pandas

# ════════════════════════════════════════════════════════════
# PART 1 — Understanding BERT and XLM-RoBERTa
# ════════════════════════════════════════════════════════════
"""
BERT (Bidirectional Encoder Representations from Transformers)
--------------------------------------------------------------
- Reads text in BOTH directions simultaneously using a Transformer encoder.
- Pre-trained on English Wikipedia + BookCorpus via:
    * Masked Language Modelling (MLM): predict masked tokens
    * Next Sentence Prediction (NSP): predict if two sentences follow each other
- Key versions:
    * bert-base-uncased  — 12 layers, 110M params, English only, lowercased
    * bert-base-cased    — same but preserves capitalisation
    * bert-large-uncased — 24 layers, 340M params, higher accuracy, slower

XLM-RoBERTa (Cross-lingual Language Model - Robustly Optimised BERT Pretraining)
----------------------------------------------------------------------------------
- Extension of RoBERTa trained on 100 languages using CC-100 corpus.
- No NSP objective — longer training, larger batches than original BERT.
- Uses SentencePiece tokenizer with a shared 250k vocabulary across languages.
- Key versions:
    * xlm-roberta-base  — 12 layers, 125M params, good speed/accuracy balance
    * xlm-roberta-large — 24 layers, 355M params, state-of-the-art multilingual

WHY XLM-RoBERTa for this task?
  Our dataset has 15 languages. XLM-RoBERTa handles all of them in one model
  using cross-lingual transfer — knowledge from English helps all other languages.
"""

from transformers import BertTokenizer, XLMRobertaTokenizer

# Load tokenizers
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
xlm_tokenizer  = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")

print("BERT vocab size     :", bert_tokenizer.vocab_size)   # 30,522
print("XLM-RoBERTa vocab  :", xlm_tokenizer.vocab_size)    # 250,002
print()
print("BERT special tokens :", bert_tokenizer.special_tokens_map)
print("XLM special tokens  :", xlm_tokenizer.special_tokens_map)


# ════════════════════════════════════════════════════════════
# PART 2 — Tokenizing Text
# ════════════════════════════════════════════════════════════

sample_premise    = "The cat sat on the mat."
sample_hypothesis = "There is a cat on a mat."

# ── Single-sentence tokenisation (BERT) ─────────────────────
bert_single = bert_tokenizer.encode_plus(
    sample_premise,
    add_special_tokens=True,   # adds [CLS] and [SEP]
    max_length=64,
    padding="max_length",
    truncation=True,
    return_attention_mask=True,
    return_tensors="pt",
)
print("=== BERT Single Sentence ===")
print("input_ids     :", bert_single["input_ids"])
print("attention_mask:", bert_single["attention_mask"])
print("Decoded       :", bert_tokenizer.decode(bert_single["input_ids"][0]))

# ── Two-sentence tokenisation (BERT) — NLI format ───────────
# BERT formats NLI as: [CLS] premise [SEP] hypothesis [SEP]
bert_pair = bert_tokenizer.encode_plus(
    sample_premise,
    sample_hypothesis,
    add_special_tokens=True,
    max_length=128,
    padding="max_length",
    truncation=True,
    return_attention_mask=True,
    return_token_type_ids=True,   # 0 = premise tokens, 1 = hypothesis tokens
    return_tensors="pt",
)
print("\n=== BERT Two-Sentence (NLI) ===")
print("token_type_ids:", bert_pair["token_type_ids"])   # shows segment boundary
print("Decoded       :", bert_tokenizer.decode(bert_pair["input_ids"][0]))

# ── Two-sentence tokenisation (XLM-RoBERTa) ─────────────────
# XLM-R format: <s> premise </s> </s> hypothesis </s>
xlm_pair = xlm_tokenizer.encode_plus(
    sample_premise,
    sample_hypothesis,
    add_special_tokens=True,
    max_length=128,
    padding="max_length",
    truncation=True,
    return_attention_mask=True,
    return_tensors="pt",
)
print("\n=== XLM-RoBERTa Two-Sentence (NLI) ===")
print("Decoded:", xlm_tokenizer.decode(xlm_pair["input_ids"][0]))
print()

"""
Key token types explained:
  input_ids      — integer IDs for each token in the vocabulary
  attention_mask — 1 for real tokens, 0 for [PAD] tokens (model ignores padding)
  token_type_ids — BERT only: 0=sentence A, 1=sentence B (XLM-R doesn't use this)
"""


# ════════════════════════════════════════════════════════════
# PART 3 — Preparing Input Data for the Model
# ════════════════════════════════════════════════════════════

MAX_LEN = 128  # standard for NLI; increase to 256 if truncating too much

def prepare_input_bert(premise: str, hypothesis: str, tokenizer, max_length: int = MAX_LEN):
    """
    Tokenise a premise-hypothesis pair for BERT.
    Returns input_ids, attention_mask, token_type_ids as tensors.
    """
    encoding = tokenizer.encode_plus(
        premise,
        hypothesis,
        add_special_tokens=True,      # [CLS] ... [SEP] ... [SEP]
        max_length=max_length,
        padding="max_length",         # pad shorter sequences to max_length
        truncation=True,              # truncate longer sequences
        return_attention_mask=True,   # 1 for tokens, 0 for padding
        return_token_type_ids=True,   # segment IDs for BERT
        return_tensors="pt",          # return PyTorch tensors
    )
    return encoding


def prepare_input_xlm(premise: str, hypothesis: str, tokenizer, max_length: int = MAX_LEN):
    """
    Tokenise a premise-hypothesis pair for XLM-RoBERTa.
    Same as BERT but no token_type_ids (RoBERTa-family models don't use them).
    """
    encoding = tokenizer.encode_plus(
        premise,
        hypothesis,
        add_special_tokens=True,      # <s> ... </s> </s> ... </s>
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors="pt",
    )
    return encoding


# Demonstrate special tokens and vocab info
print("=== Tokenizer Properties ===")
print("BERT special tokens map :", bert_tokenizer.special_tokens_map)
print("BERT vocab size         :", bert_tokenizer.vocab_size)
print()
print("XLM-R special tokens map:", xlm_tokenizer.special_tokens_map)
print("XLM-R vocab size        :", xlm_tokenizer.vocab_size)
print()

enc = prepare_input_xlm(sample_premise, sample_hypothesis, xlm_tokenizer)
print("Prepared XLM-R encoding keys:", list(enc.keys()))
print("input_ids shape             :", enc["input_ids"].shape)
print("attention_mask shape        :", enc["attention_mask"].shape)
print("Padding tokens (0s in mask) :", (enc["attention_mask"] == 0).sum().item())


# ════════════════════════════════════════════════════════════
# PART 4 — Loading and Exploring the Dataset
# ════════════════════════════════════════════════════════════

import pandas as pd

# Load CSVs
train_df = pd.read_csv("data/train.csv")
test_df  = pd.read_csv("data/test.csv")

# ── Basic exploration ────────────────────────────────────────
print("=== Dataset Overview ===")
print("\nTrain shape:", train_df.shape)
print("Test shape :", test_df.shape)

print("\nTrain columns:", train_df.columns.tolist())
print("Test columns :", test_df.columns.tolist())

print("\nFirst 5 rows of training data:")
print(train_df.head())

print("\nData types:")
print(train_df.dtypes)

print("\nNull values in train:")
print(train_df.isnull().sum())

# ── Label distribution ───────────────────────────────────────
label_map = {0: "Entailment", 1: "Neutral", 2: "Contradiction"}
print("\nLabel distribution:")
print(train_df["label"].map(label_map).value_counts())

# ── Language distribution ────────────────────────────────────
print("\nLanguages in training set:")
print(train_df["language"].value_counts())

# ── Text length statistics ───────────────────────────────────
train_df["premise_len"]    = train_df["premise"].str.split().str.len()
train_df["hypothesis_len"] = train_df["hypothesis"].str.split().str.len()
print("\nPremise word length stats:")
print(train_df["premise_len"].describe())
print("\nHypothesis word length stats:")
print(train_df["hypothesis_len"].describe())


# ════════════════════════════════════════════════════════════
# PART 5 — Creating Cross-Validation Folds
# ════════════════════════════════════════════════════════════

from sklearn.model_selection import StratifiedKFold
import numpy as np

N_SPLITS   = 5
RANDOM_SEED = 42

# StratifiedKFold preserves the label ratio (0/1/2) in every fold
kf = StratifiedKFold(
    n_splits=N_SPLITS,
    shuffle=True,           # randomise before splitting
    random_state=RANDOM_SEED
)

X = train_df.index.values          # we split on row indices
y = train_df["label"].values        # stratify by label

train_folds = []   # list of training index arrays
val_folds   = []   # list of validation index arrays

for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    train_folds.append(train_idx)
    val_folds.append(val_idx)

    # Show fold size and label distribution
    fold_train_labels = y[train_idx]
    fold_val_labels   = y[val_idx]
    print(f"\nFold {fold + 1}/{N_SPLITS}")
    print(f"  Train: {len(train_idx):,} samples | Val: {len(val_idx):,} samples")
    unique, counts = np.unique(fold_train_labels, return_counts=True)
    print(f"  Train label dist: { {label_map[k]: v for k, v in zip(unique, counts)} }")
    unique, counts = np.unique(fold_val_labels, return_counts=True)
    print(f"  Val   label dist: { {label_map[k]: v for k, v in zip(unique, counts)} }")

print(f"\n✓ {N_SPLITS} folds created.")
print(f"  train_folds[0] shape : {train_folds[0].shape}")
print(f"  val_folds[0]   shape : {val_folds[0].shape}")

# ── Example: retrieve fold 1 DataFrames ─────────────────────
fold1_train_df = train_df.iloc[train_folds[0]].reset_index(drop=True)
fold1_val_df   = train_df.iloc[val_folds[0]].reset_index(drop=True)
print(f"\nFold 1 train DataFrame shape: {fold1_train_df.shape}")
print(f"Fold 1 val   DataFrame shape: {fold1_val_df.shape}")


# ════════════════════════════════════════════════════════════
# BONUS — PyTorch Dataset class (ties everything together)
# ════════════════════════════════════════════════════════════

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class NLIDataset(Dataset):
    """
    PyTorch Dataset for Natural Language Inference.
    Works with both BERT-style and XLM-RoBERTa-style tokenizers.
    """
    def __init__(self, dataframe: pd.DataFrame, tokenizer, max_len: int = MAX_LEN,
                 has_labels: bool = True):
        self.data       = dataframe.reset_index(drop=True)
        self.tokenizer  = tokenizer
        self.max_len    = max_len
        self.has_labels = has_labels

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        encoding = self.tokenizer.encode_plus(
            str(row["premise"]),
            str(row["hypothesis"]),
            add_special_tokens=True,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        item = {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
        }

        # token_type_ids only for BERT-family models
        if "token_type_ids" in encoding:
            item["token_type_ids"] = encoding["token_type_ids"].squeeze(0)

        if self.has_labels:
            item["labels"] = torch.tensor(row["label"], dtype=torch.long)

        return item


# ── Quick sanity check ───────────────────────────────────────
xlm_tok = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")

sample_dataset = NLIDataset(fold1_train_df.head(10), xlm_tok, has_labels=True)
sample_loader  = DataLoader(sample_dataset, batch_size=4, shuffle=False)

batch = next(iter(sample_loader))
print("\n=== Sample Batch (XLM-RoBERTa) ===")
print("input_ids shape     :", batch["input_ids"].shape)       # (4, 128)
print("attention_mask shape:", batch["attention_mask"].shape)  # (4, 128)
print("labels              :", batch["labels"])                # tensor([0, 2, 0, 0])


# ════════════════════════════════════════════════════════════
# NEXT STEPS (full training pipeline outline)
# ════════════════════════════════════════════════════════════
"""
1. Load XLM-RoBERTa for classification:
      model = AutoModelForSequenceClassification.from_pretrained(
          "xlm-roberta-base", num_labels=3
      )

2. For each fold:
      train_ds = NLIDataset(train_df.iloc[train_folds[fold]], xlm_tok)
      val_ds   = NLIDataset(train_df.iloc[val_folds[fold]],   xlm_tok)
      train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
      val_loader   = DataLoader(val_ds,   batch_size=32, shuffle=False)

3. Optimiser + scheduler:
      optimizer = AdamW(model.parameters(), lr=2e-5)
      scheduler = get_linear_schedule_with_warmup(optimizer, ...)

4. Training loop:
      for epoch in range(NUM_EPOCHS):
          model.train()
          for batch in train_loader:
              outputs = model(**batch)
              loss = outputs.loss
              loss.backward()
              optimizer.step(); scheduler.step(); optimizer.zero_grad()

5. Inference on test_df → generate submission.csv with columns [id, prediction]
"""