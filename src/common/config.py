
import logging
from starlette.config import Config

logging.getLogger("watchfiles").setLevel(logging.WARNING)
log = logging.getLogger(__name__)
config = Config(".env")


# region secret provider
SECRET_PROVIDER = config("SECRET_PROVIDER", default=None)
if SECRET_PROVIDER == "metatron-secret":
    pass

elif SECRET_PROVIDER == "kms-secret":
    pass

else:
    from starlette.datastructures import Secret
# endregion


LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)
ENV = config("ENV", default="local")

# this will support special chars for credentials
# DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret)

# region mongodb
MONGODB_DATABASE_HOSTNAME = config("MONGODB_DATABASE_HOSTNAME",default="mongodb://localhost")
MONGODB_DATABASE_NAME = config("MONGODB_DATABASE_NAME", default="stock_data")
MONGODB_DATABASE_PORT = config("MONGODB_DATABASE_PORT", default="27017")
# endregion

# region milvus
MILVUS_DATABASE_HOST = config("MILVUS_DATABASE_HOST", default="localhost")
MILVUS_DATABASE_NAME = config("MILVUS_DATABASE_NAME", default="stock_data")
MILVUS_DATABASE_PORT = config("MILVUS_DATABASE_PORT", default="19530")
# endregion

# region openai
OPENAI_API_KEY = config("OPENAI_API_KEY", cast=Secret)
# endregion