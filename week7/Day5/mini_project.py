# =============================================================================
# Cats vs Dogs — Full Pipeline (single file)
# =============================================================================
# Setup: unzip dataset, rename folder to cats_dogs, place under data/
#   data/cats_dogs/train/train/<images>
#   data/cats_dogs/test/test/<images>
# Run:  python cats_dogs_pipeline.py
# =============================================================================

import os, re, json, math, random
from glob import glob
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

np.random.seed(42)
tf.random.set_seed(42)

# =============================================================================
# CONFIG
# =============================================================================
DATA_ROOT   = Path("data/cats_dogs")
OUTPUT_DIR  = Path("outputs");  OUTPUT_DIR.mkdir(exist_ok=True)
IMG_H, IMG_W = 180, 180
BATCH        = 32
SEED         = 1337
EPOCHS_MAX   = 30          # hard cap; early stopping usually fires earlier
THRESHOLD    = 0.5         # dog-probability cutoff

# =============================================================================
# 1. DATA LOADING
# =============================================================================
print("\n=== 1. Data Loading ===")

train_dir = (DATA_ROOT/"train"/"train") if (DATA_ROOT/"train"/"train").exists() else (DATA_ROOT/"train")
test_dir  = (DATA_ROOT/"test" /"test")  if (DATA_ROOT/"test" /"test").exists()  else (DATA_ROOT/"test")

def build_df(folder: Path, labeled=True):
    exts = ("*.jpg","*.jpeg","*.png","*.bmp")
    files = []
    for ex in exts:
        files.extend(glob(str(folder/"**"/ex), recursive=True))
    if not files:
        raise FileNotFoundError(f"No images found under {folder}")
    rows = []
    for f in files:
        if labeled:
            name   = Path(f).name.lower()
            parent = Path(f).parent.name.lower()
            if parent in {"cat","cats"}:           label = "cat"
            elif parent in {"dog","dogs"}:         label = "dog"
            elif re.search(r'(^|[^a-z])cat([^a-z]|$)', name): label = "cat"
            elif re.search(r'(^|[^a-z])dog([^a-z]|$)', name): label = "dog"
            else: continue
            rows.append({"filepath": f, "label": label})
        else:
            rows.append({"filepath": f})
    return pd.DataFrame(rows)

df_all  = build_df(train_dir, labeled=True)
df_test = build_df(test_dir,  labeled=False)

df_tr, df_val = train_test_split(
    df_all, test_size=0.2, stratify=df_all["label"], random_state=SEED
)

# Generators — augmentation on train only
train_gen = ImageDataGenerator(
    rescale=1./255, rotation_range=45,
    width_shift_range=0.15, height_shift_range=0.15,
    zoom_range=0.5, horizontal_flip=True,
)
val_gen  = ImageDataGenerator(rescale=1./255)
test_gen = ImageDataGenerator(rescale=1./255)

def make_flow(gen, df, labeled=True, shuffle=False):
    kwargs = dict(dataframe=df, x_col="filepath",
                  target_size=(IMG_H, IMG_W), batch_size=BATCH,
                  shuffle=shuffle, validate_filenames=False)
    if labeled:
        return gen.flow_from_dataframe(**kwargs, y_col="label", class_mode="binary")
    return gen.flow_from_dataframe(**kwargs, y_col=None, class_mode=None)

train_flow = make_flow(train_gen, df_tr,  labeled=True,  shuffle=True)
val_flow   = make_flow(val_gen,   df_val, labeled=True,  shuffle=False)
test_flow  = make_flow(test_gen,  df_test,labeled=False, shuffle=False)

print(f"Train: {train_flow.samples}  Val: {val_flow.samples}  Test: {test_flow.samples}")
print(f"Class indices: {train_flow.class_indices}")   # {'cat':0, 'dog':1}

# =============================================================================
# 2. DATA INSPECTION
# =============================================================================
print("\n=== 2. Data Inspection ===")

labels_arr = train_flow.labels
cats = int((labels_arr == 0).sum())
dogs = int((labels_arr == 1).sum())
print(f"Training — cats: {cats}, dogs: {dogs}")
print("Classes are", "balanced." if abs(cats-dogs)/max(cats,dogs) < 0.1 else "imbalanced!")

# Sample grid
imgs, lbls = next(train_flow)
fig, axes = plt.subplots(3, 4, figsize=(10, 7))
idx_map = {v: k for k, v in train_flow.class_indices.items()}
for ax, img, lbl in zip(axes.flat, imgs, lbls):
    ax.imshow(img)
    ax.set_title(idx_map[round(lbl)], fontsize=10)
    ax.axis("off")
plt.suptitle("Sample training images (augmented)", y=1.01)
plt.tight_layout()
plt.savefig(OUTPUT_DIR/"sample_grid.png", bbox_inches="tight")
plt.close()
print("Saved outputs/sample_grid.png")

# =============================================================================
# 3–4. MODEL + OPTIMIZER
# =============================================================================
# Architecture: 3 conv blocks (32→64→128 filters), MaxPool after each,
# Dropout(0.5) before Dense head, single sigmoid output for binary target.

def build_model():
    model = keras.Sequential([
        layers.Input(shape=(IMG_H, IMG_W, 3)),

        layers.Conv2D(32,  3, padding="same", activation="relu"),
        layers.MaxPooling2D(),

        layers.Conv2D(64,  3, padding="same", activation="relu"),
        layers.MaxPooling2D(),

        layers.Conv2D(128, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),

        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(128, activation="relu"),
        layers.Dense(1,   activation="sigmoid"),   # binary → sigmoid + BCE
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model

model = build_model()
model.summary()

# =============================================================================
# 5. TRAINING (with early stopping)
# =============================================================================
print("\n=== 5. Training ===")

callbacks = [
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=5,
                                   restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                       patience=3, verbose=1),
    keras.callbacks.ModelCheckpoint(str(OUTPUT_DIR/"best_model.keras"),
                                    save_best_only=True, monitor="val_loss"),
]

history = model.fit(
    train_flow,
    epochs=EPOCHS_MAX,
    validation_data=val_flow,
    callbacks=callbacks,
)

# Curves
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(history.history["loss"],     label="train")
ax1.plot(history.history["val_loss"], label="val")
ax1.set_title("Loss"); ax1.legend()
ax2.plot(history.history["accuracy"],     label="train")
ax2.plot(history.history["val_accuracy"], label="val")
ax2.set_title("Accuracy"); ax2.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR/"training_curves.png")
plt.close()
print("Saved outputs/training_curves.png")

# =============================================================================
# 6. VALIDATION EVALUATION
# =============================================================================
print("\n=== 6. Validation Metrics ===")

val_loss, val_acc = model.evaluate(val_flow, verbose=0)
print(f"Val loss: {val_loss:.4f}  Val accuracy: {val_acc:.4f}")

# Predictions on validation set (rebuild flow without shuffle)
val_flow2 = make_flow(val_gen, df_val, labeled=True, shuffle=False)
probs_val  = model.predict(val_flow2, verbose=0).ravel()
preds_val  = (probs_val >= THRESHOLD).astype(int)
true_val   = val_flow2.labels.astype(int)

print("\nClassification Report:")
print(classification_report(true_val, preds_val, target_names=["cat","dog"]))

cm = confusion_matrix(true_val, preds_val)
disp = ConfusionMatrixDisplay(cm, display_labels=["cat","dog"])
disp.plot(colorbar=False)
plt.title("Confusion Matrix — Validation")
plt.savefig(OUTPUT_DIR/"confusion_matrix.png")
plt.close()
print("Saved outputs/confusion_matrix.png")

# =============================================================================
# 7. TEST INFERENCE
# =============================================================================
print("\n=== 7. Test Inference ===")

probs_test = model.predict(test_flow, verbose=1).ravel()
pred_labels = ["dog" if p >= THRESHOLD else "cat" for p in probs_test]

df_preds = pd.DataFrame({
    "filepath":  df_test["filepath"].values,
    "prob_dog":  probs_test,
    "pred_label": pred_labels,
})
df_preds.to_csv(OUTPUT_DIR/"test_predictions.csv", index=False)
print(f"Saved outputs/test_predictions.csv  ({len(df_preds)} rows)")
print(df_preds.head())

# =============================================================================
# 8. BASELINE (no augmentation) COMPARISON
# =============================================================================
print("\n=== 8. Baseline vs Augmented ===")

plain_gen   = ImageDataGenerator(rescale=1./255)
train_plain = make_flow(plain_gen, df_tr, labeled=True, shuffle=True)

base_model = build_model()
base_cb = [keras.callbacks.EarlyStopping(monitor="val_loss", patience=5,
                                          restore_best_weights=True)]
base_history = base_model.fit(
    train_plain, epochs=EPOCHS_MAX,
    validation_data=val_flow, callbacks=base_cb, verbose=0,
)

base_loss, base_acc = base_model.evaluate(val_flow, verbose=0)
print(f"Baseline  — val loss: {base_loss:.4f}  val acc: {base_acc:.4f}")
print(f"Augmented — val loss: {val_loss:.4f}  val acc: {val_acc:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, key, title in zip(axes, ["val_loss","val_accuracy"], ["Val Loss","Val Accuracy"]):
    ax.plot(base_history.history[key],    label="baseline")
    ax.plot(history.history[key],         label="augmented")
    ax.set_title(title); ax.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR/"baseline_vs_augmented.png")
plt.close()
print("Saved outputs/baseline_vs_augmented.png")

# =============================================================================
# 9. CLASS IMBALANCE (compute weights if needed)
# =============================================================================
total = cats + dogs
class_weight = {0: total / (2 * cats), 1: total / (2 * dogs)}
print(f"\n=== 9. Class Weights ===\n{class_weight}")
# To retrain with weights: model.fit(..., class_weight=class_weight)
# Increases recall on the minority class at the cost of some precision.

# =============================================================================
# 10. SAVE ARTIFACTS
# =============================================================================
print("\n=== 10. Saving Artifacts ===")

model.save(str(OUTPUT_DIR/"best_model.keras"))   # already saved by checkpoint too

config = {
    "img_size": [IMG_H, IMG_W],
    "batch_size": BATCH,
    "optimizer": "Adam",
    "lr": 1e-3,
    "loss": "binary_crossentropy",
    "threshold": THRESHOLD,
    "augmentation": True,
    "val_accuracy": float(round(val_acc, 4)),
    "val_loss": float(round(val_loss, 4)),
}
with open(OUTPUT_DIR/"run_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("Saved outputs/best_model.keras")
print("Saved outputs/run_config.json")
print("\nDone! All outputs are in the outputs/ folder.")

# =============================================================================
# 11. EXTENSION NOTE
# =============================================================================
# Recommended next step: Transfer learning with MobileNetV2
#
# base = keras.applications.MobileNetV2(include_top=False,
#            input_shape=(IMG_H, IMG_W, 3), weights="imagenet")
# base.trainable = False   # freeze backbone
# x = layers.GlobalAveragePooling2D()(base.output)
# x = layers.Dropout(0.3)(x)
# out = layers.Dense(1, activation="sigmoid")(x)
# tl_model = keras.Model(base.input, out)
# tl_model.compile(optimizer=Adam(1e-4), loss="binary_crossentropy",
#                  metrics=["accuracy"])
# Expected benefit: ImageNet priors for low-level features → faster convergence
# and higher accuracy with fewer training samples.