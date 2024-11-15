from google.protobuf.message import Message
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel
from Stimulator.api.protobuf.out.RandomNumberSeeds_pb2 import RandomNumberSeedsMessage as RandomNumberSeedsMessage_pb2


def ensure_initialization(cls):
    if not hasattr(cls, '_has_been_initialized'):
        cls.initial()
        setattr(cls, '_has_been_initialized', True)
    return cls


@ensure_initialization
class RandomNumberSeedsMessageConverter:
    __model_class_for_convert_func_dict: dict
    __package_name_for_convert_func_dict: dict

    @classmethod
    def initial(cls):
        cls.__package_name_for_convert_func_dict = {
            RandomNumberSeedsMessage_pb2: cls.__random_number_seeds_pb2,
        }
        cls.__model_class_for_convert_func_dict = {
            RandomNumberSeedsModel: cls.__random_number_seeds_model_to_package_pb,
        }

    @classmethod
    def protobuf_to_model(cls, pb_message: Message) -> RandomNumberSeedsModel:
        convert_func = cls.__package_name_for_convert_func_dict[type(pb_message)]
        return convert_func(pb_message)

    @classmethod
    def model_to_protobuf(cls, model: RandomNumberSeedsModel) -> RandomNumberSeedsMessage_pb2:
        convert_func = cls.__model_class_for_convert_func_dict[type(model)]
        return convert_func(model)

    @classmethod
    def __random_number_seeds_pb2(
            cls,
            random_number_seeds_message: RandomNumberSeedsMessage_pb2) -> RandomNumberSeedsModel:
        return RandomNumberSeedsModel(seeds=random_number_seeds_message.seeds)

    @classmethod
    def __random_number_seeds_model_to_package_pb(
            cls,
            random_number_seeds_model: RandomNumberSeedsModel) -> RandomNumberSeedsMessage_pb2:
        return RandomNumberSeedsMessage_pb2(seeds=random_number_seeds_model.seeds)
