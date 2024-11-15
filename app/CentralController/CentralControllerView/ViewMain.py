import os
from typing import Union

import yaml

from CentralControllerView.CentralManagementController import CentralManagementController
from CentralControllerView.CentralManagerUI import CentralManagerUI
from CentralControllerView.ui.viewcontrol import ViewControl


class ViewMain:

    def __init__(self, config_dict: dict[str, Union[str, dict]]):
        self.__config_dict = config_dict

    def run(self):
        central_management_controller = CentralManagementController()
        central_manager_ui = ViewControl(central_management_controller)

        central_management_controller.initial(self.__config_dict)
        with central_management_controller:
            central_manager_ui.run()


def main():
    current_file_path = os.path.abspath(__file__)
    directory_path = os.path.join(os.path.dirname(current_file_path), 'config')
    application_config_file_name = 'config.yml'
    application_config_path = os.path.join(directory_path, application_config_file_name)
    with open(application_config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    view_main = ViewMain(config_dict)
    view_main.run()


if __name__ == '__main__':
    main()
