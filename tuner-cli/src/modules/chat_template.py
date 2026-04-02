import os
import torch
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

def start_inference(model_path):
    print(f"📦 Подготовка стабильного инференса для {model_path}...")

    # 1. Определяем базовую модель
    base_model_path = "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit"
    base_info_file = os.path.join(model_path, "base_model.txt")
    if os.path.exists(base_info_file):
        with open(base_info_file, "r") as f:
            base_model_path = f.read().strip()

    # 2. Настройка квантования
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    # 3. Загружаем токенизатор и базовую модель
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Исправляем отсутствие pad_token если нужно
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    # 4. Накладываем LoRA адаптер
    if model_path != base_model_path:
        print(f"🧠 Накладываю обученные веса...")
        model = PeftModel.from_pretrained(model, model_path)

    model.eval()

    print("\n" + "="*40)
    print("🚀 TUNER-2: КАНАЛ С МОДЕЛЬЮ ОТКРЫТ (ULTRA STABLE)")
    print("Напишите 'exit' для выхода.")
    print("="*40)

    while True:
        try:
            user_text = input("\n👤 ВЫ: ")
            if user_text.lower() in ["exit", "quit", "выход"]:
                break
            if not user_text.strip(): continue

            # Применяем шаблон чата
            messages = [{"role": "user", "content": user_text}]
            encoding = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True
            ).to("cuda")

            # Генерация
            with torch.no_grad():
                output_ids = model.generate(
                    **encoding,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.pad_token_id
                )

            # Декодируем (обрезаем входную часть)
            input_length = encoding.input_ids.shape[1]
            response = tokenizer.decode(output_ids[0][input_length:], skip_special_tokens=True)
            print(f"\n🤖 ИИ: {response.strip()}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            import traceback
            print(f"\n❌ Ошибка генерации: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    MODEL_PATH = "tuner-model"
    if len(sys.argv) > 1:
        MODEL_PATH = sys.argv[1]
    start_inference(MODEL_PATH)
