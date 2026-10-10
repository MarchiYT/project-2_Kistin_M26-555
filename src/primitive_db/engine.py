import json

import prompt
from prettytable import PrettyTable

from primitive_db import core, utils
from primitive_db.constants import COMMAND_PROMPT, HELP_LINES, ID_COLUMN, METADATA_FILE
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import parse_command


def print_help():
    """Выводит список команд."""
    print("Доступные команды:")
    for line in HELP_LINES:
        print(line)


def print_table(schema, data):
    """Выводит записи в табличном виде."""
    table = PrettyTable()
    table.field_names = list(schema)
    for row in data:
        table.add_row([row[column] for column in schema])
    print(table)


@handle_db_errors
def execute_command(text, cache_result):
    """Выполняет одну команду."""
    command = parse_command(text)
    if command is None:
        return False
    action = command["command"]
    if action == "exit":
        return "exit"
    if action == "help":
        print_help()
        return False
    metadata = utils.load_metadata(METADATA_FILE)
    if action == "list_tables":
        if not metadata:
            print("Таблиц пока нет.")
        for name in metadata:
            print(f"- {name}")
        return False
    name = command["table_name"]
    if action == "create_table":
        result = core.create_table(metadata, name, command["columns"])
        if result is None:
            return False
        utils.save_table_data(name, [])
        utils.save_metadata(METADATA_FILE, result)
        columns = ", ".join(f"{key}:{value}" for key, value in result[name].items())
        print(f'Таблица "{name}" успешно создана со столбцами: {columns}')
        return True
    schema = core.get_schema(metadata, name)
    if action == "drop_table":
        result = core.drop_table(metadata, name)
        if result is None:
            return False
        utils.delete_table_data(name)
        utils.save_metadata(METADATA_FILE, result)
        print(f'Таблица "{name}" успешно удалена.')
        return True
    if action == "insert":
        data = core.insert(metadata, name, command["values"])
        if data is None:
            return False
        utils.save_table_data(name, data)
        print(f'Запись с ID={data[-1][ID_COLUMN]} успешно добавлена в таблицу "{name}".')
        return True
    data = utils.load_table_data(name)
    if action == "info":
        columns = ", ".join(f"{key}:{value}" for key, value in schema.items())
        print(f"Таблица: {name}")
        print(f"Столбцы: {columns}")
        print(f"Количество записей: {len(data)}")
        return False
    where = command["where_clause"]
    if where is not None:
        core.validate_values(schema, where)
    if action == "select":
        key = (name, json.dumps(where, sort_keys=True))
        result = cache_result(key, lambda: core.select(data, where))
        if result is not None:
            print_table(schema, result)
        return False
    set_clause = command.get("set_clause")
    if set_clause is not None:
        if ID_COLUMN in set_clause:
            raise ValueError("Изменять ID нельзя.")
        core.validate_values(schema, set_clause)
    changed_ids = [row[ID_COLUMN] for row in data if core.matches(row, where)]
    if not changed_ids:
        print("Записи по этому условию не найдены.")
        return False
    if action == "update":
        result = core.update(data, set_clause, where)
    else:
        result = core.delete(data, where)
    if result is None:
        return False
    utils.save_table_data(name, result)
    for row_id in changed_ids:
        if action == "update":
            print(f'Запись с ID={row_id} в таблице "{name}" успешно обновлена.')
        else:
            print(f'Запись с ID={row_id} успешно удалена из таблицы "{name}".')
    return True


def run():
    """Запускает цикл ввода команд."""
    print_help()
    cache_result = create_cacher()
    while True:
        try:
            text = prompt.string(COMMAND_PROMPT, empty=True)
            result = execute_command(text, cache_result)
            if result == "exit":
                break
            if result is True:
                cache_result = create_cacher()
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break
