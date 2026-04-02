import os
import torch
import sys

# Фикс багов PyTorch
if not hasattr(torch, 'int1'): torch.int1 = torch.int8
if not hasattr(torch, 'uint1'): torch.uint1 = torch.uint8
if not hasattr(torch, '_inductor'):
    class Dummy: pass
    torch._inductor = Dummy()
if not hasattr(torch._inductor, 'config'):
    class DummyConfig: pass
    torch._inductor.config = DummyConfig()

from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

def run_train(model_name="unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit", dataset_path="data/abai_train.jsonl"):
    print(f"🚀 ЗАГРУЗКА БАЗОВОЙ МОДЕЛИ: {model_name}")

    # 1. Загрузка ЧИСТОЙ модели (она останется нетронутой)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = 1024,
        load_in_4bit = True,
        dtype = None,
    )

    # 2. Создание "Адаптера" (Дополнительные слои)
    # Это и есть наш "второй способ" - мы не меняем веса модели, а создаем новые сверху
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Rank: чем выше, тем больше "памяти", но больше риск "тупости"
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth",
    )

    # Шаблон для ответов
    prompt_style = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response:
{}"""

    EOS_TOKEN = tokenizer.eos_token
    def formatting_prompts_func(examples):
        # Поддержка разных форматов датасета
        instructions = examples.get("instruction") or examples.get("prompt") or [""] * len(next(iter(examples.values())))
        # Добавил поддержку вашего поля 'response'
        outputs = examples.get("response") or examples.get("output") or examples.get("completion") or examples.get("answer")

        # Если outputs всё еще None, попробуем взять что-нибудь из словаря
        if outputs is None:
             outputs = [""] * len(instructions)

        texts = []
        for instr, out in zip(instructions, outputs):
            text = prompt_style.format(instr if instr else "", out if out else "") + EOS_TOKEN
            texts.append(text)
        return { "text" : texts, }

    # 3. Загрузка данных
    print(f"📊 ЗАГРУЗКА ДАТАСЕТА: {dataset_path}")
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    dataset = dataset.map(formatting_prompts_func, batched = True,)

    # 4. Настройка тренера
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = 1024,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60, # Оптимально для маленьких датасетов
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
        ),
    )

    # 5. Обучение ТОЛЬКО новых слоев (адаптеров)
    print("🔥 ОБУЧЕНИЕ НОВЫХ СЛОЕВ (ADAPTERS)...")
    trainer.train()

    # 6. СОХРАНЕНИЕ АДАПТЕРА (НЕ ВСЕЙ МОДЕЛИ!)
    # Это сохранит только маленькие файлы (~50-100MB) в папку tuner-model
    print("💾 СОХРАНЕНИЕ АДАПТЕРА В 'tuner-model'...")
    model.save_pretrained("tuner-model")
    tokenizer.save_pretrained("tuner-model")

    # Также сохраним конфиг базовой модели, чтобы знать на что "клеить"
    with open("tuner-model/base_model.txt", "w") as f:
        f.write(model_name)

    print("✅ ГОТОВО! Теперь ваша модель имеет 'внешние мозги' в папке tuner-model.")

if __name__ == "__main__":
    # Эти значения будут подставлены TrainingMaster-ом при генерации
    MODEL_NAME = "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit"
    DATASET_PATH = "newdataset/train.jsonl"

    try:
        run_train(MODEL_NAME, DATASET_PATH)
    except KeyboardInterrupt:
        print("\n🛑 Прервано.")
