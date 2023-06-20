import ast
import os
import sqlite3
import pickle

from src.smolex.config import config


def setup_database():
    conn = sqlite3.connect(config.ast_sqlite_db)
    conn.execute("DROP TABLE IF EXISTS Entities")
    conn.execute(
        """
        CREATE TABLE Entities
        (ID INTEGER PRIMARY KEY AUTOINCREMENT, FileName TEXT, Type TEXT, Name TEXT, AST BLOB)
    """
    )
    conn.commit()
    return conn


def insert_into_database(
    db_connection, filename: str, entity_type: str, name: str, ast_pickle: bytes
):
    db_connection.execute(
        "INSERT INTO Entities (FileName, Type, Name, AST) VALUES (?, ?, ?, ?)",
        (filename, entity_type, name, ast_pickle),
    )


def create_ast_sqlite_index():
    db_connection = setup_database()

    for directory in config.roots:
        print(f"AST Parsing code in {directory}")

        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(extension) for extension in config.extensions):
                    filename = os.path.join(root, file)

                    with open(filename, "r") as fd:
                        try:
                            root_node = ast.parse(fd.read())
                        except Exception as e:
                            print(e)
                            continue

                    for node in [
                        n
                        for n in ast.walk(root_node)
                        if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                    ]:
                        insert_into_database(
                            db_connection=db_connection,
                            filename=filename,
                            name=node.name,
                            entity_type=type(node).__name__,
                            ast_pickle=pickle.dumps(node),
                        )
                        db_connection.commit()

    db_connection.close()


def generate_class_interface(ast_node: ast.AST) -> str:
    """
    Generate the interface for the class:

    Example result:

    class Foo:
        def bar(self, x: int) -> str:
            ...
    """

    if not isinstance(ast_node, ast.ClassDef):
        return ""

    output = []

    class_name = ast_node.name
    output.append(f"class {class_name}:")

    for node in ast_node.body:
        if isinstance(node, ast.FunctionDef):
            func_name = node.name

            # Gather arguments
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                arg_type = "Any"  # Default to Any if there's no annotation
                if arg.annotation:
                    arg_type = ast.unparse(arg.annotation)
                args.append(f"{arg_name}: {arg_type}")

            # Gather return type
            ret_type = "None"  # Default to None if there's no annotation
            if node.returns:
                ret_type = ast.unparse(node.returns)

            # Add the function definition to the output
            output.append(
                f'    def {func_name}(self, {", ".join(args)}) -> {ret_type}:'
            )
            output.append("        <...>")

    return "\n".join(output)


if __name__ == "__main__":
    create_ast_sqlite_index()
