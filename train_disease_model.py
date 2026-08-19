import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(
    BASE_DIR,
    "disease_dataset",
    "PlantVillage"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "disease_model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "plant_disease_model.keras"
)

CLASS_NAMES_PATH = os.path.join(
    MODEL_DIR,
    "class_names.json"
)

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 32

EPOCHS = 10

VALIDATION_SPLIT = 0.20

SEED = 123


# ============================================================
# CHECK DATASET
# ============================================================

print("=" * 60)
print("PLANT DISEASE DETECTION MODEL")
print("=" * 60)

print("Dataset:")
print(DATASET_DIR)

if not os.path.exists(DATASET_DIR):

    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_DIR}"
    )


# ============================================================
# REMOVE NESTED PLANTVILLAGE FROM CLASS DISCOVERY
# ============================================================

all_directories = []

for name in os.listdir(DATASET_DIR):

    full_path = os.path.join(
        DATASET_DIR,
        name
    )

    if os.path.isdir(full_path):

        # Ignore nested PlantVillage directory
        if name.lower() == "plantvillage":
            continue

        all_directories.append(name)


all_directories = sorted(all_directories)


print()
print("Disease classes found:")
print("-" * 60)

for index, class_name in enumerate(all_directories):

    print(
        f"{index:2d} : {class_name}"
    )

print("-" * 60)

print(
    "Number of classes:",
    len(all_directories)
)


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("Loading images...")
print("This may take some time.")


train_dataset = tf.keras.utils.image_dataset_from_directory(

    DATASET_DIR,

    validation_split=VALIDATION_SPLIT,

    subset="training",

    seed=SEED,

    image_size=IMAGE_SIZE,

    batch_size=BATCH_SIZE,

    label_mode="int",

    shuffle=True,

    class_names=all_directories
)


validation_dataset = tf.keras.utils.image_dataset_from_directory(

    DATASET_DIR,

    validation_split=VALIDATION_SPLIT,

    subset="validation",

    seed=SEED,

    image_size=IMAGE_SIZE,

    batch_size=BATCH_SIZE,

    label_mode="int",

    shuffle=False,

    class_names=all_directories
)


class_names = train_dataset.class_names


print()
print("Classes used by model:")
print(class_names)

print(
    "Number of classes:",
    len(class_names)
)


# ============================================================
# SAVE CLASS NAMES
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

with open(
    CLASS_NAMES_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        class_names,
        file,
        indent=4
    )


print()
print(
    "Class names saved:",
    CLASS_NAMES_PATH
)


# ============================================================
# PERFORMANCE OPTIMIZATION
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(
    buffer_size=AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    buffer_size=AUTOTUNE
)


# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential(

    [

        layers.RandomFlip(
            "horizontal"
        ),

        layers.RandomRotation(
            0.10
        ),

        layers.RandomZoom(
            0.10
        ),

        layers.RandomContrast(
            0.10
        )

    ],

    name="data_augmentation"
)


# ============================================================
# BASE MODEL
# ============================================================

base_model = MobileNetV2(

    input_shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    ),

    include_top=False,

    weights="imagenet"
)


# Freeze the pretrained layers initially

base_model.trainable = False


# ============================================================
# BUILD MODEL
# ============================================================

inputs = layers.Input(

    shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    )
)


x = data_augmentation(
    inputs
)


x = tf.keras.applications.mobilenet_v2.preprocess_input(
    x
)


x = base_model(
    x,
    training=False
)


x = layers.GlobalAveragePooling2D()(x)


x = layers.Dropout(
    0.30
)(x)


outputs = layers.Dense(

    len(class_names),

    activation="softmax"

)(x)


model = models.Model(

    inputs,
    outputs
)


# ============================================================
# COMPILE
# ============================================================

model.compile(

    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.0001
    ),

    loss="sparse_categorical_crossentropy",

    metrics=[
        "accuracy"
    ]
)


# ============================================================
# MODEL SUMMARY
# ============================================================

print()
print("=" * 60)
print("MODEL SUMMARY")
print("=" * 60)

model.summary()


# ============================================================
# CALLBACKS
# ============================================================

callbacks = [

    tf.keras.callbacks.ModelCheckpoint(

        MODEL_PATH,

        monitor="val_accuracy",

        save_best_only=True,

        verbose=1
    ),

    tf.keras.callbacks.EarlyStopping(

        monitor="val_accuracy",

        patience=3,

        restore_best_weights=True,

        verbose=1
    )
]


# ============================================================
# TRAIN
# ============================================================

print()
print("=" * 60)
print("STARTING TRAINING")
print("=" * 60)

history = model.fit(

    train_dataset,

    validation_data=validation_dataset,

    epochs=EPOCHS,

    callbacks=callbacks
)


# ============================================================
# FINAL EVALUATION
# ============================================================

print()
print("=" * 60)
print("FINAL MODEL EVALUATION")
print("=" * 60)

loss, accuracy = model.evaluate(
    validation_dataset
)

print(
    f"Validation Loss: {loss:.4f}"
)

print(
    f"Validation Accuracy: {accuracy * 100:.2f}%"
)


# ============================================================
# SAVE FINAL MODEL
# ============================================================

model.save(
    MODEL_PATH
)


print()
print("=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print(
    "Model saved to:"
)

print(
    MODEL_PATH
)

print()
print(
    "Class names saved to:"
)

print(
    CLASS_NAMES_PATH
)

print()
print("Disease Detector model is ready.")