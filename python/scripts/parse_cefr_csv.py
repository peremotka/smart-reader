import csv
import json

csv_file_path = 'oxford-5k.csv'
json_output_path = '../app/data/cefr_dict.json'

cefr_dict = {}

with open(csv_file_path, mode='r', encoding='utf-8') as f:
    # DictReader автоматически подхватит названия колонок из первой строчки
    reader = csv.DictReader(f)

    for row in reader:
        word = row.get('word')
        level = row.get('level')

        if word and level:
            # На всякий случай нормализуем: слово в нижний регистр, уровень в верхний
            cefr_dict[word.strip().lower()] = level.strip().upper()

# Сохраняем в компактный JSON
with open(json_output_path, mode='w', encoding='utf-8') as f:
    json.dump(cefr_dict, f, ensure_ascii=False, indent=4)

print(f"Готово! База очищена. Сохранено слов: {len(cefr_dict)}")