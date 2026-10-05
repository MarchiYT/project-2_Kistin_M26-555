import shlex

from primitive_db.constants import COLUMN_TYPES, ID_COLUMN, NAME_CHARACTERS


def validate_name(name):
    """Проверяет имя таблицы или столбца."""
    if not name or any(char not in NAME_CHARACTERS for char in name):
        raise ValueError(f"Некорректное имя: {name}.")
    return name


def parse_command(text):
    """Разбирает команды для управления таблицами."""
    tokens = shlex.split(text)
    if not tokens:
        return None
    command = tokens[0]
    if command in ("help", "exit", "list_tables") and len(tokens) == 1:
        return {"command": command}
    if command == "drop_table" and len(tokens) == 2:
        return {"command": command, "table_name": validate_name(tokens[1])}
    if command == "create_table" and len(tokens) >= 3:
        columns = {}
        for token in tokens[2:]:
            parts = token.split(":")
            if len(parts) != 2:
                raise ValueError(f"Некорректное значение: {token}. Попробуйте снова.")
            name, column_type = parts
            validate_name(name)
            if name == ID_COLUMN or name in columns or column_type not in COLUMN_TYPES:
                raise ValueError(f"Некорректное значение: {token}. Попробуйте снова.")
            columns[name] = column_type
        return {
            "command": command,
            "table_name": validate_name(tokens[1]),
            "columns": columns,
        }
    raise ValueError(f"Функции {command} нет. Попробуйте снова.")
