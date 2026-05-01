import numpy as np
import pandas as pd
import random
import string

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from transformers import BertTokenizer, BertForSequenceClassification
from transformers import BertConfig
from transformers.models.bert.modeling_bert import BertEncoder
from sklearn.metrics import roc_auc_score

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# ── Paths ──────────────────────────────────────────────────────────────────────
TRAIN_PATH  = "llm-detect-ai-generated-text/train_essays.csv"
TEST_PATH   = "llm-detect-ai-generated-text/test_essays.csv"
PROMPT_PATH = "llm-detect-ai-generated-text/train_prompts.csv"

src_train  = pd.read_csv(TRAIN_PATH)
src_prompt = pd.read_csv(PROMPT_PATH)
src_sub    = pd.read_csv("llm-detect-ai-generated-text/sample_submission.csv")

# ── Pretrained model ───────────────────────────────────────────────────────────
tokenizer_save_path = "bert-base-uncased"   # use HF hub name directly
model_save_path     = "bert-base-uncased"

tokenizer       = BertTokenizer.from_pretrained(tokenizer_save_path)
pretrained_model = BertForSequenceClassification.from_pretrained(
    model_save_path, num_labels=2
)
# Embedding layer only (no classifier head needed for feature extraction)
embedding_model = pretrained_model.bert.embeddings
embedding_model.eval()
for p in embedding_model.parameters():
    p.requires_grad = False

# ── Hyperparameters ────────────────────────────────────────────────────────────
train_batch_size  = 16
test_batch_size   = 32
lr                = 2e-4
beta1             = 0.5
nz                = 100   # latent vector dimensions
num_epochs        = 5
num_hidden_layers = 6
train_ratio       = 0.8

# ── Data preparation ───────────────────────────────────────────────────────────
class GANDAIGDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels):
        self.texts  = texts
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]


all_num   = len(src_train)
train_num = int(all_num * train_ratio)
test_num  = all_num - train_num

# Shuffle for reproducibility
src_train = src_train.sample(frac=1, random_state=42).reset_index(drop=True)

train_set = src_train.iloc[:train_num]
test_set  = pd.concat([
    src_train.iloc[train_num:],
]).reset_index(drop=True)

train_dataset = GANDAIGDataset(
    texts=train_set["text"].tolist(),
    labels=train_set["generated"].tolist(),
)
test_dataset = GANDAIGDataset(
    texts=test_set["text"].tolist(),
    labels=test_set["generated"].tolist(),
)

train_loader = DataLoader(train_dataset, batch_size=train_batch_size, shuffle=True)
test_loader  = DataLoader(test_dataset,  batch_size=test_batch_size,  shuffle=False)

# ── Generator ──────────────────────────────────────────────────────────────────
config = BertConfig(num_hidden_layers=num_hidden_layers)

class Generator(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.fc = nn.Linear(input_dim, 256 * 128)

        self.conv_net = nn.Sequential(
            nn.ConvTranspose1d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(True),
            nn.ConvTranspose1d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(True),
            nn.ConvTranspose1d(64, config.hidden_size, kernel_size=4, stride=2, padding=1),
            nn.Tanh(),
        )
        self.bert_encoder = BertEncoder(config)

    def forward(self, x):
        x = self.fc(x)                         # (B, 256*128)
        x = x.view(x.size(0), 256, 128)        # (B, 256, 128)
        x = self.conv_net(x)                   # (B, hidden_size, seq_len)
        x = x.permute(0, 2, 1)                 # (B, seq_len, hidden_size)
        x = self.bert_encoder(x)               # BaseModelOutput
        return x

# ── Discriminator ──────────────────────────────────────────────────────────────
class SumBertPooler(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        sum_hidden = hidden_states.sum(dim=1)
        sum_mask   = sum_hidden.sum(1).unsqueeze(1)
        sum_mask   = torch.clamp(sum_mask, min=1e-9)
        mean_embeddings = sum_hidden / sum_mask
        return mean_embeddings


class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert_encoder = BertEncoder(config)
        self.bert_encoder.layer = nn.ModuleList([
            layer for layer in pretrained_model.bert.encoder.layer[:6]
        ])
        self.pooler = SumBertPooler()
        self.classifier = torch.nn.Sequential(
            nn.Linear(config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 1),
        )

    def forward(self, input):
        out = self.bert_encoder(input)
        out = self.pooler(out.last_hidden_state)
        out = self.classifier(out)
        return torch.sigmoid(out).view(-1)

# ── Training utilities ─────────────────────────────────────────────────────────
def preparation_embedding(texts):
    encodings      = tokenizer(texts, padding=True, truncation=True,
                               max_length=512, return_tensors="pt")
    input_ids      = encodings["input_ids"]
    token_type_ids = encodings["token_type_ids"]
    with torch.no_grad():
        embeded = embedding_model(input_ids=input_ids,
                                  token_type_ids=token_type_ids)
    return embeded


def eval_auc(model):
    model.eval()
    predictions, actuals = [], []
    with torch.no_grad():
        for batch in test_loader:
            texts = batch[0]
            label = batch[1].float().to(device)

            encodings      = tokenizer(texts, padding=True, truncation=True,
                                       max_length=512, return_tensors="pt")
            input_ids      = encodings["input_ids"]
            token_type_ids = encodings["token_type_ids"]
            embeded        = embedding_model(input_ids=input_ids,
                                             token_type_ids=token_type_ids)
            embeded        = embeded.to(device)

            outputs = model(embeded)
            predictions.extend(outputs.cpu().numpy())
            actuals.extend(label.cpu().numpy())

    auc = roc_auc_score(actuals, predictions)
    print("AUC:", auc)
    return auc


def get_model_info_dict(model, epoch, auc_score):
    current_device = next(model.parameters()).device
    model.to("cpu")
    model_info = {
        "epoch":            epoch,
        "model_state_dict": model.state_dict(),
        "auc_score":        auc_score,
    }
    model.to(current_device)
    return model_info


def GAN_step(optimizerG, optimizerD, netG, netD, real_data, label, epoch, i):
    # ── Train Discriminator ────────────────────────────────────────────────────
    netD.zero_grad()
    batch_size = real_data.size(0)

    label.fill_(0)                              # real = 0 (human-written)
    output     = netD(real_data)
    errD_real  = criterion(output, label)
    errD_real.backward()
    D_x = output.mean().item()

    noise      = torch.randn(batch_size, nz, device=device)
    fake_data  = netG(noise).last_hidden_state
    label.fill_(1)                              # fake = 1 (AI-generated)
    output     = netD(fake_data.detach())
    errD_fake  = criterion(output, label)
    errD_fake.backward()
    D_G_z1 = output.mean().item()
    errD   = errD_real + errD_fake
    optimizerD.step()

    # ── Train Generator ────────────────────────────────────────────────────────
    netG.zero_grad()
    label.fill_(0)                              # fool discriminator → predict human
    output  = netD(fake_data)
    errG    = criterion(output, label)
    errG.backward()
    D_G_z2  = output.mean().item()
    optimizerG.step()

    if i % 50 == 0:
        print("[%d/%d][%d/%d] Loss_D: %.4f Loss_G: %.4f D(x): %.4f D(G(z)): %.4f / %.4f"
              % (epoch, num_epochs, i, len(train_loader),
                 errD.item(), errG.item(), D_x, D_G_z1, D_G_z2))

    return optimizerG, optimizerD, netG, netD

# ── Instantiate models ─────────────────────────────────────────────────────────
netG = Generator(input_dim=nz).to(device)
netD = Discriminator().to(device)

criterion  = nn.BCELoss()
optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(beta1, 0.999))
optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(beta1, 0.999))

# ── Training loop ──────────────────────────────────────────────────────────────
model_infos = []
for epoch in range(num_epochs):
    netG.train()
    netD.train()
    for i, data in enumerate(train_loader, 0):
        with torch.no_grad():
            embeded = preparation_embedding(data[0])

        optimizerG, optimizerD, netG, netD = GAN_step(
            optimizerG=optimizerG,
            optimizerD=optimizerD,
            netG=netG,
            netD=netD,
            real_data=embeded.to(device),
            label=data[1].float().to(device),
            epoch=epoch,
            i=i,
        )

    auc_score = eval_auc(netD)
    model_infos.append(get_model_info_dict(netD, epoch, auc_score))

print("Train complete!")

# ── Inference ──────────────────────────────────────────────────────────────────
max_auc_model_info = max(model_infos, key=lambda x: x["auc_score"])

model = Discriminator()
model.load_state_dict(max_auc_model_info["model_state_dict"])
model.to(device)
model.eval()


class InferenceDataset(torch.utils.data.Dataset):
    def __init__(self, texts):
        self.texts = texts

    def __getitem__(self, idx):
        return self.texts[idx]

    def __len__(self):
        return len(self.texts)


src_test    = pd.read_csv(TEST_PATH)
sub_dataset = InferenceDataset(texts=src_test["text"].tolist())

inference_loader = DataLoader(sub_dataset, batch_size=test_batch_size, shuffle=False)

sub_predictions = []
with torch.no_grad():
    for batch in inference_loader:
        encodings      = tokenizer(list(batch), padding=True, truncation=True,
                                   max_length=512, return_tensors="pt")
        input_ids      = encodings["input_ids"]
        token_type_ids = encodings["token_type_ids"]
        embeded        = embedding_model(input_ids=input_ids,
                                         token_type_ids=token_type_ids)
        embeded        = embeded.to(device)

        outputs = model(embeded)
        sub_predictions.extend(outputs.cpu().numpy())

sub_ans_df = pd.DataFrame({
    "id":        src_test["id"].tolist(),
    "generated": sub_predictions,
})
print(sub_ans_df)
sub_ans_df.to_csv("submission.csv", index=False)
print("Saved submission.csv")