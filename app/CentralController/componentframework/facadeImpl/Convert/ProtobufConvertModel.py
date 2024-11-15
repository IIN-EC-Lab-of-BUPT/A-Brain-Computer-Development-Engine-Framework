from componentframework.api.model.MessageOperateModel import AddListenerOnRegisterComponentModel


class ProtobufConvertModel:
    def __init__(self):
        pass

    def convert_to_model(self, protobuf):
        match protobuf:
            case DataPackageModel():
                return self._deal_data_msg(protobuf)

            case DevicePackageModel():
                return self._deal_device_msg(protobuf)

            case EventPackageModel():
                return self._deal_event_msg(protobuf)

            case ImpedancePackageModel():
                return self._deal_impedance_msg(protobuf)

            case InformationPackageModel():
                return self._deal_information_msg(protobuf)

            case ControlpackageModel():
                return self._deal_control_msg(protobuf)

    @staticmethod
    def _deal_data_msg(msg) -> AddListenerOnRegisterComponentModel:
        add_listener_on_register_component_model = AddListenerOnRegisterComponentModel()
        add_listener_on_register_component_model.component_id = msg.componentID
        add_listener_on_register_component_model.component_type = msg.componentType
        add_listener_on_register_component_model.component_info = msg.componentInfo
        return add_listener_on_register_component_model
