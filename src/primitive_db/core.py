from primitive_db import utils
from primitive_db.constants import COLUMN_TYPES, ID_COLUMN
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
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


@handle_db_errors
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


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    get_schema(metadata, table_name)
    del metadata[table_name]
    return metadata



def validate_values(schema, values):
    """Проверяет столбцы и типы значений."""
    for column, value in values.items():
        if column not in schema:
            raise ValueError(f'Ошибка: Столбец "{column}" не существует.')
        if type(value) is not COLUMN_TYPES[schema[column]]:
            raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет запись с новым ID."""
    schema = get_schema(metadata, table_name)
    columns = [name for name in schema if name != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(f"Ожидалось значений: {len(columns)}, получено: {len(values)}.")
    row = dict(zip(columns, values))
    validate_values(schema, row)
    data = utils.load_table_data(table_name)
    next_id = max((item[ID_COLUMN] for item in data), default=0) + 1
    row = {ID_COLUMN: next_id, **row}
    data.append(row)
    return data


def matches(row, where_clause):
    """Проверяет совпадение записи с условием."""
    return where_clause is None or all(
        row[column] == value and type(row[column]) is type(value)
        for column, value in where_clause.items()
    )


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает подходящие записи."""
    return [row.copy() for row in table_data if matches(row, where_clause)]



@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Меняет поля записей, подходящих под условие."""
    if ID_COLUMN in set_clause:
        raise ValueError("Изменять ID нельзя.")
    result = []
    for row in table_data:
        updated_row = row.copy()
        if matches(row, where_clause):
            updated_row.update(set_clause)
        result.append(updated_row)
    return result


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Возвращает записи, оставшиеся после удаления."""
    return [row.copy() for row in table_data if not matches(row, where_clause)]
