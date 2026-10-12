import json
import os

from primitive_db.constants import DATA_DIRECTORY


def load_metadata(filepath):
    try:
        with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise ValueError("Не удалось прочитать JSON метаданных.") from None
    if not isinstance(metadata, dict):
        raise ValueError("Некорректный формат файла метаданных.")
    return metadata


def save_metadata(filepath, metadata):
    temporary_path = str(filepath) + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)
        file.write("\n")
    os.replace(temporary_path, filepath)


def load_table_data(table_name):
    filepath = os.path.join(DATA_DIRECTORY, table_name + ".json")
    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise ValueError("Не удалось прочитать JSON таблицы.") from None
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError("Некорректный формат файла таблицы.")
    return data


def save_table_data(table_name, data):
    os.makedirs(DATA_DIRECTORY, exist_ok=True)
    filepath = os.path.join(DATA_DIRECTORY, table_name + ".json")
    save_metadata(filepath, data)


def delete_table_data(table_name):
    filepath = os.path.join(DATA_DIRECTORY, table_name + ".json")
    if os.path.exists(filepath):
        os.remove(filepath)
