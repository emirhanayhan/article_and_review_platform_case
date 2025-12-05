import optparse
import uvicorn

from configs.local import local_config
from configs.prod import prod_config
from configs.stage import stage_config
from src import create_fastapi_app


CONFIG_LOOKUP = {
    "local": local_config,
    "prod": prod_config,
    "stage": stage_config
}


def config_settings(config_name, ):
    config = CONFIG_LOOKUP[config_name]
    return config


parser = optparse.OptionParser()
parser.add_option("--config", default="local", help="which config to load")
options, args = parser.parse_args()

settings = config_settings(options.config)

app = create_fastapi_app(settings)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings["host"], port=settings["port"], workers=settings["worker_count"])
