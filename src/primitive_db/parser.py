import shlex

from primitive_db.constants import COLUMN_TYPES, ID_COLUMN, NAME_CHARACTERS


def validate_name(name):
    if not name or any(char not in NAME_CHARACTERS for char in name):
        raise ValueError(f"Некорректное имя: {name}.")
    return name


def tokenize(text):
    tokens = []
    value = ""
    quote = None
    escaped = False
    for char in text:
        if quote is not None:
            value += char
            if escaped:
                escaped = False
            elif char == "\\" and quote == '"':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char.isspace() or char in "(),=":
            if value:
                tokens.append(value)
                value = ""
            if not char.isspace():
                tokens.append(char)
        elif char in ('"', "'"):
            if value:
                raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
            value = char
            quote = char
        else:
            if value.startswith(('"', "'")):
                raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
            value += char
    if quote is not None:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
    if value:
        tokens.append(value)
    return tokens


def parse_value(value):
    if value.startswith(('"', "'")):
        parts = shlex.split(value)
        if len(parts) == 1:
            return parts[0]
    elif value.lower() in ("true", "false"):
        return value.lower() == "true"
    else:
        digits = value[1:] if value.startswith(("+", "-")) else value
        if digits and digits.isascii() and digits.isdigit():
            return int(value)
    raise ValueError(f"Некорректное значение: {value}. Попробуйте снова.")


def parse_values(text):
    tokens = tokenize(text) if isinstance(text, str) else text
    if len(tokens) < 3 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("Некорректный список значений.")
    values = tokens[1:-1]
    if not values or len(values) % 2 == 0:
        raise ValueError("Некорректный список значений.")
    result = []
    for index, value in enumerate(values):
        if index % 2:
            if value != ",":
                raise ValueError("Значения нужно разделять запятыми.")
        else:
            result.append(parse_value(value))
    return result


def parse_assignments(tokens):
    if not tokens or (len(tokens) + 1) % 4:
        raise ValueError("Некорректное условие.")
    result = {}
    for index in range(0, len(tokens), 4):
        name, sign, value = tokens[index : index + 3]
        validate_name(name)
        if sign != "=" or name in result:
            raise ValueError("Некорректное условие.")
        if index and tokens[index - 1] != ",":
            raise ValueError("Некорректное условие.")
        result[name] = parse_value(value)
    return result


def parse_where(text):
    tokens = tokenize(text) if isinstance(text, str) else text
    if len(tokens) != 3:
        raise ValueError("В where нужно указать одно условие.")
    return parse_assignments(tokens)


def parse_set(text):
    tokens = tokenize(text) if isinstance(text, str) else text
    return parse_assignments(tokens)


def parse_command(text):
    tokens = tokenize(text)
    if not tokens:
        return None
    action = tokens[0]
    if action in ("help", "exit", "list_tables") and len(tokens) == 1:
        return {"command": action}
    if action in ("drop_table", "info") and len(tokens) == 2:
        return {"command": action, "table_name": validate_name(tokens[1])}
    if action == "create_table" and len(tokens) >= 3:
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
            "command": action,
            "table_name": validate_name(tokens[1]),
            "columns": columns,
        }
    if action == "insert" and len(tokens) >= 7:
        if tokens[1] == "into" and tokens[3] == "values":
            return {
                "command": action,
                "table_name": validate_name(tokens[2]),
                "values": parse_values(tokens[4:]),
            }
    if action == "select" and len(tokens) in (3, 7) and tokens[1] == "from":
        if len(tokens) == 3 or tokens[3] == "where":
            return {
                "command": action,
                "table_name": validate_name(tokens[2]),
                "where_clause": parse_where(tokens[4:]) if len(tokens) == 7 else None,
            }
    if action == "update" and len(tokens) >= 10:
        if tokens[2] == "set" and tokens[-4] == "where":
            return {
                "command": action,
                "table_name": validate_name(tokens[1]),
                "set_clause": parse_set(tokens[3:-4]),
                "where_clause": parse_where(tokens[-3:]),
            }
    if action == "delete" and len(tokens) == 7:
        if tokens[1] == "from" and tokens[3] == "where":
            return {
                "command": action,
                "table_name": validate_name(tokens[2]),
                "where_clause": parse_where(tokens[4:]),
            }
    known_commands = (
        "create_table",
        "drop_table",
        "list_tables",
        "insert",
        "select",
        "update",
        "delete",
        "info",
        "help",
        "exit",
    )
    if action in known_commands:
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
    raise ValueError(f"Функции {action} нет. Попробуйте снова.")
