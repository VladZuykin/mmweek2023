from classes import Config
from database import org_db_funcs

config = Config("config.json")
db = org_db_funcs.OrgDataBase(config.db_path)