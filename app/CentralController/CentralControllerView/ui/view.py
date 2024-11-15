from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QGridLayout, QPushButton
from PyQt5.QtGui import QColor
from CentralController.api.model.ComponentGroupModel import ComponentGroupStatusListModel, ComponentGroupStatusModel
from CentralController.api.model.GroupModel import GroupModel
from CentralControllerView.CentralManagementController import CentralManagementController



class MainWindow(QWidget):
    def __init__(self, central_management_view_controller: CentralManagementController):
        super().__init__()
        self.status_dict = {}
        self.group_layout_dict = {}
        self.group_box_dict = {}
        self.component_layout_dict = {}
        self.group_ui_dict = {}
        self.groups_layout = None
        self.sort_component = None
        self.group_dict = None
        self.group_statuses = None
        self.__app: QApplication = None
        self.status_labels = {}
        self.index_dict = {}
        self.__central_management_view_controller = central_management_view_controller

        # 创建 QTimer 实例
        self.timer = QTimer(self)
        # 连接信号与槽
        self.timer.timeout.connect(self.update)
        # 设置时间间隔（毫秒），这里是 1000 毫秒即 1 秒
        self.timer.start(1000)

    def run(self):
        self.group_statuses = self.__central_management_view_controller.get_components_status_list()
        self.group_dict = self.__group_by_component_group_id(self.group_statuses)
        # 设置主窗口的布局
        self.layout = QVBoxLayout(self)

        # 添加公共的准备和关闭按钮
        # self.prepare_button = QPushButton("Prepare", self)
        # self.close_button = QPushButton("Close", self)
        # self.layout.addWidget(self.prepare_button)
        # self.layout.addWidget(self.close_button)

        # 创建一个QWidget作为所有组的容器
        groups_container = QWidget(self)
        self.groups_layout = QVBoxLayout(groups_container)

        # 连接信号和槽
        # self.prepare_button.clicked.connect(lambda: self.__prepare("all component "))
        # self.close_button.clicked.connect(lambda: self.__shutdown("all component "))

        # 创建并添加组件
        for group_id, info in self.group_dict.items():
            group_ui = self.create_group_ui(group_id, info)
            self.group_ui_dict[group_id] = group_ui
            self.groups_layout.addWidget(group_ui)

            # 将包含所有组的QWidget添加到主布局中
        self.layout.addWidget(groups_container)

        # 设置窗口的初始大小和标题
        self.setWindowTitle('中央控制器管理界面')
        self.resize(800, 600)

    def update(self):
        latest_grouped_info = self.__central_management_view_controller.get_components_status_list()
        latest_grouped = self.__group_by_component_group_id(latest_grouped_info)
        self.status_dict = self.__get_component_status_dict(latest_grouped_info)
        # 更新UI中的状态显示

        # 添加新组和更新现有组（如果它们的位置/顺序有变化）
        for group_id, new_info in latest_grouped.items():
            if group_id in self.group_dict:
                self.sort_component = self.__group_by_component_type(new_info)
                for component_type, info in self.sort_component.items():
                    for item in info:
                        if item.component_id in self.status_labels:
                            pass
                        else:
                            self.__add_component_to_group(group_id, component_type, item)
            else:
                self.__add_group(group_id, new_info)

        self.update_status()
        self.group_dict=latest_grouped

    def __add_component_to_group(self, group_id, component_type, info):
        # 添加组件（这里用QLabel和QLineEdit表示）
        if group_id + info.component_type in self.component_layout_dict:
            label = QLabel(f"Component ({info.component_id}):", self.group_box_dict[group_id])
            self.component_layout_dict[group_id + component_type].addWidget(label, 0,self.index_dict[group_id])
            # 添加组件的状态指示灯
            status_label = QLabel("", self.group_box_dict[group_id])
            self.update_status_label(status_label, info.component_status)
            self.component_layout_dict[group_id + component_type].addWidget(status_label, 1,self.index_dict[group_id])
            self.status_labels[info.component_id] = status_label
            self.index_dict[group_id] = self.index_dict[group_id] + 1
            # 注意：如果算法组件很多，可能会超出屏幕范围
            self.group_layout_dict[group_id].addLayout(self.component_layout_dict[group_id + component_type])
        else:
            component_layout = QGridLayout()
            # 对item进行处理
            # 添加组件（这里用QLabel和QLineEdit表示）
            label = QLabel(f"Component ({info.component_id}):", self.group_box_dict[group_id])
            component_layout.addWidget(label, 0, self.index_dict[group_id])

            # 添加组件的状态指示灯
            status_label = QLabel("", self.group_box_dict[group_id])
            self.update_status_label(status_label, info.component_status)

            component_layout.addWidget(status_label, 1, self.index_dict[group_id])
            self.component_layout_dict[group_id + component_type] = component_layout
            self.status_labels[info.component_id] = status_label
            self.index_dict[group_id] = self.index_dict[group_id] + 1
            # 这里为了简单起见，我们直接将网格布局添加到垂直布局中
            # 注意：如果算法组件很多，可能会超出屏幕范围
            self.group_layout_dict[group_id].addLayout(component_layout)

    def __add_group(self, group_id, info):
        # 创建一个QGroupBox来表示一个新组
        group_box = QGroupBox(f"Group {group_id}", self)
        # 创建组内的布局
        group_layout = QVBoxLayout(group_box)
        self.group_layout_dict[group_id] = group_layout
        # 按照组件类型对info排序
        info.sort(key=lambda x: x.component_type)
        # 按组件类型分组
        sort_component = self.__group_by_component_type(info)
        # 初始化索引字典
        self.index_dict[group_id] = 0
        # 遍历每种类型的组件
        for component_type, items in sort_component.items():
            # 创建并添加组件的网格布局
            component_layout = QGridLayout()
            self.component_layout_dict[group_id + component_type] = component_layout
            for item in items:
                # 添加组件（这里用QLabel和QLineEdit表示）
                label = QLabel(f"Component ({item.component_id}):", group_box)
                component_layout.addWidget(label, 0, self.index_dict[group_id])
                # 添加组件的状态指示灯
                status_label = QLabel("", group_box)
                self.update_status_label(status_label, item.component_status)
                component_layout.addWidget(status_label, 1, self.index_dict[group_id])
                self.status_labels[item.component_id] = status_label
                self.index_dict[group_id] += 1
            # 将网格布局添加到垂直布局中
            group_layout.addLayout(component_layout)
        if group_id == "group_base":
            pass
        else:
            # 添加启动和重置按钮
            start_button = QPushButton(f"Start Group {group_id}", group_box)
            # reset_button = QPushButton(f"Reset Group {group_id}", group_box)
            group_layout.addWidget(start_button)
            # group_layout.addWidget(reset_button)
            # 连接信号和槽
            start_button.clicked.connect(lambda: self.__startup(group_id))
            # reset_button.clicked.connect(lambda: self.__reset(group_id))

        # 保存新创建的QGroupBox
        self.groups_layout.addWidget(group_box)
        self.group_box_dict[group_id] = group_box

    def update_status(self):
        for component_id, current_status in self.status_dict.items():
            self.update_status_label(self.status_labels[component_id], current_status)

    def create_group_ui(self, group_id, info):
        # i为位置信息
        # 创建一个QGroupBox来表示一个组
        group_box = QGroupBox(f"Group {group_id}", self)
        # 创建组内的布局
        group_layout = QVBoxLayout(group_box)
        self.group_layout_dict[group_id] = group_layout
        info.sort(key=lambda x: x.component_type)
        self.sort_component = self.__group_by_component_type(info)
        self.index_dict[group_id] = 0
        for component_type, info in self.sort_component.items():
            # 创建并添加算法组件的网格布局
            component_layout = QGridLayout()
            for item in info:
                # 对item进行处理
                # 添加组件（这里用QLabel和QLineEdit表示）
                label = QLabel(f"Component ({item.component_id}):", group_box)
                component_layout.addWidget(label, 0, self.index_dict[group_id])

                # 添加组件的状态指示灯
                status_label = QLabel("", group_box)
                self.update_status_label(status_label, item.component_status)

                component_layout.addWidget(status_label, 1, self.index_dict[group_id])
                self.component_layout_dict[group_id + component_type] = component_layout
                self.status_labels[item.component_id] = status_label
                self.index_dict[group_id] = self.index_dict[group_id] + 1
                # 这里为了简单起见，我们直接将网格布局添加到垂直布局中
                # 注意：如果算法组件很多，可能会超出屏幕范围
            group_layout.addLayout(component_layout)
        if group_id == "group_base":
            pass
        else:
            # 添加启动和重置按钮
            start_button = QPushButton(f"Start Group {group_id}", group_box)
            # reset_button = QPushButton(f"Reset Group {group_id}", group_box)
            group_layout.addWidget(start_button)
            # group_layout.addWidget(reset_button)
            start_button.clicked.connect(lambda: self.__startup(group_id))
            # reset_button.clicked.connect(lambda: self.__reset(group_id))

        self.group_box_dict[group_id] = group_box
        return group_box

    def update_status_label(self, label, status):
        """根据状态更新QLabel的背景色"""
        if status == 'RUNNING':
            label.setStyleSheet(f"background-color: {QColor(0, 255, 0).name()};")  # 绿色
        elif status == 'ERROR':
            label.setStyleSheet(f"background-color: {QColor(255, 0, 0).name()};")  # 红色
        else:
            # label.setStyleSheet("background-color: none;")  # 清除背景色
            label.setStyleSheet("background-color: #808080;")

    def __prepare(self, message):
        print(message + " prepare sucess")
        self.__central_management_view_controller.prepare_system()

    def __startup(self, message):
        print(message + " startup sucess")
        self.__central_management_view_controller.start_group(GroupModel(group_id=message))

    def __reset(self, message):
        print(message + " reset sucess")
        self.__central_management_view_controller.reset_group(GroupModel(group_id=message))

    def __shutdown(self, message):
        print(message + " shutdown sucess")
        self.__central_management_view_controller.close_system()
        self.exit()

    def exit(self):
        self.__app.quit()

    def __group_by_component_group_id(self, group_statuses: list[ComponentGroupStatusModel]) -> dict:
        result = {}
        for item in group_statuses:
            if item.component_group_id not in result:
                result[item.component_group_id] = []
            result[item.component_group_id].append(item)
        return result

    def __group_by_component_type(self, group_info: list[ComponentGroupStatusModel]) -> dict[
        str, list[ComponentGroupStatusModel]]:
        result = {}
        for item in group_info:
            if item.component_type not in result:
                result[item.component_type] = []
            result[item.component_type].append(item)
        return result

    def __get_component_status_dict(self, group_info: list[ComponentGroupStatusModel]) -> dict:
        result = {}
        for cg in group_info:
            result[cg.component_id] = cg.component_status
        return result


