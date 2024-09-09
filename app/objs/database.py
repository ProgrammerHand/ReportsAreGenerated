from pathlib import Path
import subprocess
import re


class Database:
    def __init__(self):
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.database = None
        self.db_type = None

    # ============================== PUBLIC METHODS ============================== #

    def add_new_config(self, username, password, host, port, database, db_type):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.db_type = db_type

        save_path = Path(f'existing/{self.database}')

        if not save_path.exists():
            save_path.mkdir()

        self._save_dotenv(save_path)
        self._get_sql_metadata(save_path)
        self._filter_metadata(save_path)

    
    def get_added_databases(self):
        databases = [db.name for db in Path('existing').iterdir() if db.is_dir()]
        return databases



    # ============================== PRIVATE METHODS ============================== #
        
    def _save_dotenv(self, save_path):
        """Save the database configuration to a .env file"""
        with open(save_path / '.env', 'w') as f:
            f.write(f'PGUSERNAME={self.username}\n')
            f.write(f'PGPASSWORD={self.password}\n')
            f.write(f'HOST={self.host}\n')
            f.write(f'PORT={self.port}\n')
            f.write(f'NAME={self.database}\n')
            f.write(f'DB_TYPE={self.db_type}\n')

    
    def _get_sql_metadata(self, dotenv_path):
        """Getting the SQL schema"""
        script_path = f'../scripts/{self.db_type}.ps1'
        pipeline = ['powershell.exe', 
                    '-ExecutionPolicy', 'Unrestricted', 
                    '-File', script_path,
                    '-savePath', dotenv_path / 'metadata.sql', 
                    '-username', self.username,
                    '-password', self.password,
                    '-name', self.database]
        result = subprocess.run(pipeline)
        if result.returncode != 0:
            raise Exception(f'Error: {result.stderr}')

    def _filter_metadata(self, metadata_path):
        """Filter the SQL metadata"""
        with open(metadata_path / 'metadata.sql', "r") as f:
            metadata = f.read()
            pattern = re.compile(r'CREATE TABLE[\s\S]*?;', re.MULTILINE)
            matches = pattern.findall(metadata)

        with open(metadata_path / 'metadata.sql', 'w') as f:
            for match in matches:
                f.write(match)
                f.write('\n\n')






        

        