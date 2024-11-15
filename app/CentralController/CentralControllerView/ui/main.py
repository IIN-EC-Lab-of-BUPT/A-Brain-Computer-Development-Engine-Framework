from CentralControllerView.CentralManagementController import CentralManagementController
from CentralControllerView.CentralManagerUI import CentralManagerUI
from CentralControllerView.ui.view import CentralManagementControllerTest
from CentralControllerView.test.view import MainWindow
from CentralControllerView.ui.viewcontrol import ViewControl

# class ViewMain:
#     def run(self):
#         central_management_controller = CentralManagementControllerTest()
#         central_manager_ui = MainWindow(central_management_controller)
#         with central_management_controller:
#             central_manager_ui.run()
#
#
# def main():
#     view_main = ViewMain()
#     view_main.run()


if __name__ == '__main__':
    central_management_controller = CentralManagementController()
    view_control = ViewControl(central_management_controller)
    view_control.run()

