METADATA_FILE = "db_meta.json"
DATA_DIRECTORY = "data"
ID_COLUMN = "ID"
COLUMN_TYPES = {"int": int, "str": str, "bool": bool}
NAME_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
COMMAND_PROMPT = "Введите команду: "
HELP_LINES = (
    "create_table <table_name> <column:type> ...",
    "list_tables",
    "drop_table <table_name>",
    "insert into <table_name> values (<value>, ...)",
    "select from <table_name> [where <column> = <value>]",
    "update <table_name> set <column> = <value> where <column> = <value>",
    "delete from <table_name> where <column> = <value>",
    "info <table_name>",
    "help",
    "exit",
)
