from primitive_db.constants import COLUMN_TYPES, ID_COLUMN
from primitive_db.parser import validate_name


def get_schema(metadata, table_name):
    """Возвращает столбцы существующей таблицы."""
    validate_name(table_name)
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')
    schema = metadata[table_name]
    if not isinstance(schema, dict) or schema.get(ID_COLUMN) != "int":
        raise ValueError("Некорректный формат файла метаданных.")
    for column, column_type in schema.items():
        validate_name(column)
        if column_type not in COLUMN_TYPES:
            raise ValueError("Некорректный формат файла метаданных.")
    return schema


def create_table(metadata, table_name, columns):
    """Добавляет новую таблицу в метаданные."""
    validate_name(table_name)
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError("Нужно указать хотя бы один столбец.")
    schema = {ID_COLUMN: "int"}
    for column, column_type in columns.items():
        validate_name(column)
        if column == ID_COLUMN or column_type not in COLUMN_TYPES:
            raise ValueError(f"Некорректный столбец: {column}:{column_type}.")
        schema[column] = column_type
    metadata[table_name] = schema
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    get_schema(metadata, table_name)
    del metadata[table_name]
    return metadata
