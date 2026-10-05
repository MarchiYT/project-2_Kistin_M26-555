import prompt

from primitive_db import core, utils
from primitive_db.constants import COMMAND_PROMPT, HELP_LINES, METADATA_FILE
from primitive_db.parser import parse_command


def print_help():
    """Выводит список команд."""
    print("Доступные команды:")
    for line in HELP_LINES:
        print(line)


def execute_command(text):
    command = parse_command(text)
    if command is None:
        return
    action = command["command"]
    if action == "exit":
        return "exit"
    if action == "help":
        print_help()
        return
    metadata = utils.load_metadata(METADATA_FILE)
    if action == "list_tables":
        if not metadata:
            print("Таблиц пока нет.")
        for name in metadata:
            print(f"- {name}")
    elif action == "create_table":
        name = command["table_name"]
        core.create_table(metadata, name, command["columns"])
        utils.save_table_data(name, [])
        utils.save_metadata(METADATA_FILE, metadata)
        columns = ", ".join(f"{key}:{value}" for key, value in metadata[name].items())
        print(f'Таблица "{name}" успешно создана со столбцами: {columns}')
    elif action == "drop_table":
        name = command["table_name"]
        core.drop_table(metadata, name)
        utils.delete_table_data(name)
        utils.save_metadata(METADATA_FILE, metadata)
        print(f'Таблица "{name}" успешно удалена.')


def run():
    """Запускает цикл ввода команд."""
    print_help()
    while True:
        try:
            text = prompt.string(COMMAND_PROMPT, empty=True)
            if execute_command(text) == "exit":
                break
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break
        except (ValueError, OSError) as error:
            print(error)
