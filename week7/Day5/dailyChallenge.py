# =============================================================================
# IMDB Sentiment Classification — Full Pipeline (single file)
# =============================================================================
# Run:  python imdb_sentiment.py
# Outputs saved to: outputs/
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tensorflow as tf
from tensorflow import keras

np.random.seed(42)
tf.random.set_seed(42)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# =============================================================================
# 1. LOAD & PREPROCESS
# =============================================================================
print("\n=== 1. Load & Preprocess ===")

NUM_WORDS = 10_000

(train_data, train_labels), (test_data, test_labels) = \
    keras.datasets.imdb.load_data(num_words=NUM_WORDS)

print(f"Training samples : {len(train_data)}")
print(f"Test samples     : {len(test_data)}")
print(f"Sample review (ints): {train_data[0][:10]} ...")
print(f"Label: {train_labels[0]}  (1=positive, 0=negative)")

# One-hot encode: each review → 10 000-dim binary vector
def vectorize_sequences(sequences, dimension=10_000):
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.0
    return results

x_train_full = vectorize_sequences(train_data)
x_test        = vectorize_sequences(test_data)
y_train_full  = train_labels.astype("float32")
y_test        = test_labels.astype("float32")

print(f"\nAfter vectorisation — x_train shape: {x_train_full.shape}")

# Validation split: first 10 000 samples → val, rest → train
x_val   = x_train_full[:10_000]
y_val   = y_train_full[:10_000]
x_train = x_train_full[10_000:]
y_train = y_train_full[10_000:]

print(f"Train: {x_train.shape[0]}  Val: {x_val.shape[0]}  Test: {x_test.shape[0]}")

# =============================================================================
# 2. BUILD THE MODEL
# =============================================================================
print("\n=== 2. Build Model ===")

def build_model():
    model = keras.Sequential([
        keras.layers.Dense(16, activation="relu", input_shape=(NUM_WORDS,)),
        keras.layers.Dense(16, activation="relu"),
        keras.layers.Dense(1,  activation="sigmoid"),   # binary → sigmoid + BCE
    ])
    model.compile(
        optimizer="rmsprop",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model

model = build_model()
model.summary()

# =============================================================================
# 3. TRAIN FOR 20 EPOCHS (to see overfitting)
# =============================================================================
print("\n=== 3. Train for 20 epochs ===")

history_20 = model.fit(
    x_train, y_train,
    epochs=20,
    batch_size=512,
    validation_data=(x_val, y_val),
    verbose=1,
)

# =============================================================================
# 4a. PLOT LOSS & ACCURACY (20 epochs)
# =============================================================================
print("\n=== 4a. Plot training curves ===")

h = history_20.history
epochs_range = range(1, 21)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))

# Loss
ax1.plot(epochs_range, h["loss"],     "bo-", label="Training loss")
ax1.plot(epochs_range, h["val_loss"], "rs-", label="Validation loss")
ax1.set_title("Training vs Validation Loss (20 epochs)")
ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss")
ax1.legend()

# Accuracy
ax2.plot(epochs_range, h["accuracy"],     "bo-", label="Training accuracy")
ax2.plot(epochs_range, h["val_accuracy"], "rs-", label="Validation accuracy")
ax2.set_title("Training vs Validation Accuracy (20 epochs)")
ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy")
ax2.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "curves_20_epochs.png")
plt.close()
print("Saved outputs/curves_20_epochs.png")

# Find optimal epoch = lowest validation loss
best_epoch = int(np.argmin(h["val_loss"])) + 1
print(f"\nBest epoch (lowest val loss): {best_epoch}")

# =============================================================================
# 4b. RETRAIN WITH OPTIMAL EPOCHS (fresh model, full train set)
# =============================================================================
print(f"\n=== 4b. Retrain for {best_epoch} epochs ===")

final_model = build_model()
history_opt = final_model.fit(
    x_train, y_train,
    epochs=best_epoch,
    batch_size=512,
    validation_data=(x_val, y_val),
    verbose=1,
)

# Plot optimal training curves
h2 = history_opt.history
opt_range = range(1, best_epoch + 1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
ax1.plot(opt_range, h2["loss"],     "bo-", label="Training loss")
ax1.plot(opt_range, h2["val_loss"], "rs-", label="Validation loss")
ax1.set_title(f"Loss — Optimal ({best_epoch} epochs)")
ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss"); ax1.legend()

ax2.plot(opt_range, h2["accuracy"],     "bo-", label="Training accuracy")
ax2.plot(opt_range, h2["val_accuracy"], "rs-", label="Validation accuracy")
ax2.set_title(f"Accuracy — Optimal ({best_epoch} epochs)")
ax2.set_xlabel("Epoch"); ax2.set_ylabel("Accuracy"); ax2.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / f"curves_optimal_{best_epoch}_epochs.png")
plt.close()
print(f"Saved outputs/curves_optimal_{best_epoch}_epochs.png")

# =============================================================================
# 5. EVALUATE ON TEST SET
# =============================================================================
print("\n=== 5. Test Set Evaluation ===")

test_loss, test_acc = final_model.evaluate(x_test, y_test, verbose=0)
val_loss_final  = h2["val_loss"][-1]
val_acc_final   = h2["val_accuracy"][-1]

print(f"\n{'Metric':<25} {'Value':>10}")
print("-" * 37)
print(f"{'Val  loss  (opt epoch)':<25} {val_loss_final:>10.4f}")
print(f"{'Val  accuracy':<25} {val_acc_final:>10.4f}")
print(f"{'Test loss':<25} {test_loss:>10.4f}")
print(f"{'Test accuracy':<25} {test_acc:>10.4f}")

# Final summary bar chart
metrics  = ["Val Accuracy", "Test Accuracy"]
values   = [val_acc_final, test_acc]
colors   = ["steelblue", "tomato"]
fig, ax = plt.subplots(figsize=(5, 4))
bars = ax.bar(metrics, values, color=colors, width=0.4)
ax.set_ylim(0.8, 1.0)
ax.set_ylabel("Accuracy")
ax.set_title("Final Accuracy Comparison")
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.002,
            f"{v:.4f}", ha="center", fontsize=11)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "final_accuracy.png")
plt.close()
print("Saved outputs/final_accuracy.png")

# Save the trained model
final_model.save(str(OUTPUT_DIR / "imdb_model.keras"))
print("Saved outputs/imdb_model.keras")

print("\n=== Done! All outputs are in the outputs/ folder ===")

# =============================================================================
# CONCLUSION (printed summary)
# =============================================================================
print(f"""
Conclusion
----------
• One-hot encoding turned variable-length integer sequences into fixed-size
  10 000-dim binary vectors, making them compatible with Dense layers.

• A two-hidden-layer network (16 units, ReLU) with a sigmoid output and
  binary cross-entropy loss is the right choice for this binary problem.

• Training for 20 epochs revealed overfitting: val loss rose after epoch
  ~{best_epoch}, while train loss kept falling.

• Retraining for exactly {best_epoch} epoch(s) yielded:
    Validation accuracy : {val_acc_final:.4f}
    Test accuracy       : {test_acc:.4f}

• The small gap between validation and test accuracy confirms the model
  generalises well to unseen data.
""")