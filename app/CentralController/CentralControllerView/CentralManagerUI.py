from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from CentralControllerView.CentralManagementInterface import CentralManagementViewControllerInterface
from CentralController.api.model.GroupModel import GroupModel


class CentralManagerUI:

    def __init__(self, central_management_view_controller: CentralManagementViewControllerInterface):
        self.__app: QApplication = None
        self.__central_management_view_controller = central_management_view_controller

    def run(self):
        # 创建应用程序和主窗口
        self.__app = QApplication([])
        window = QWidget()
        window.setWindowTitle('中央控制器管理界面')
        window.setGeometry(100, 100, 300, 200)  # 设置窗口位置和大小
        # window.setWindowFlags(window.windowFlags() & ~Qt.WindowCloseButtonHint)  # 隐藏关闭按钮
        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建四个按钮并添加到布局中
        button_prepare = QPushButton('准备')
        button_startup = QPushButton('启动')
        button_reset = QPushButton('重置')
        button_shutdown = QPushButton('关闭')

        # 将按钮添加到布局中
        layout.addWidget(button_prepare)
        layout.addWidget(button_startup)
        layout.addWidget(button_reset)
        layout.addWidget(button_shutdown)

        # 设置布局
        window.setLayout(layout)

        # 连接信号和槽
        button_prepare.clicked.connect(self.__prepare)
        button_startup.clicked.connect(self.__startup)
        button_reset.clicked.connect(self.__reset)
        button_shutdown.clicked.connect(self.__shutdown)

        # 设置主窗口的布局
        window.setLayout(layout)

        # 显示窗口
        window.show()

        # 运行应用程序的主循环
        self.__app.exec_()

    def __prepare(self):
        self.__central_management_view_controller.prepare_system()

    def __startup(self):
        self.__central_management_view_controller.start_group(GroupModel(group_id='group_1'))

    def __reset(self):
        self.__central_management_view_controller.reset_group(GroupModel(group_id='group_1'))

    def __shutdown(self):
        self.__central_management_view_controller.close_system()
        self.exit()

    def exit(self):
        self.__app.quit()
