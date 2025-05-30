from app import db, create_app
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    print("Tables in database:")
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  Column: {column['name']} {column['type']}")
        # Print foreign keys
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            print(f"  Foreign Key: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
