from src.entity.config_entity import MongoDBConfig

from .producer_repository import ProducerRepository
from .work_generator_repository import WorkGeneratorRepository


class MongoFactory:
    @staticmethod
    def get_repository(repo_type: str, **kwargs):
        commong_args = {
            "mongo_db_config": MongoDBConfig(),
            **kwargs # additional all keyword arguments required other than config
        }
        if repo_type == "work_generator":
            return WorkGeneratorRepository(**commong_args)
        elif repo_type == "producer":
            return ProducerRepository(**commong_args)
        else:
            raise ValueError("Unknown repository type")
