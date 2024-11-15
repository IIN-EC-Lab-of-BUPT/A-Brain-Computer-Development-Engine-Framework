from PyQt5.QtWidgets import QApplication

from CentralControllerView.CentralManagementController import CentralManagementController
from CentralControllerView.ui.view import MainWindow
import sys


class ViewControl:
    def __init__(self, central_management_view_controller: CentralManagementController):
        self.__central_management_view_controller = central_management_view_controller

    def run(self):
        # 创建应用程序和主窗口
        app = QApplication([])
        ex = MainWindow(self.__central_management_view_controller)
        ex.run()
        ex.show()
        app.exec_()
