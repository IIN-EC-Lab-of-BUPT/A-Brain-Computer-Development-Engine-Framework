import os
from pathlib import Path

import yaml

from Collector.receiver.virtual_receiver.api.message.VirtualReceiverMessageKeyEnum import VirtualReceiverMessageKeyEnum


class VirtualReceiverConfigCreator:

    def run(self):
        virtual_receiver_config_dict = {}
        virtual_receiver_config_dict.update(self.create_message())
        virtual_receiver_config_dict.update(self.create_send_config())
        virtual_receiver_config_dict.update(self.create_device_info())
        # prefix_dir 前缀一定不要加/ 否则表示相对根目录的绝对路径
        virtual_receiver_config_dict.update(
            self.create_data_files('E:/Workspace/bcicompetitionframework/Collector/receiver/virtual_receiver/data',
                                   'Collector/receiver/virtual_receiver/data',
                                   ['dat', 'pkl'])
        )
        with open('VirtualReceiverConfig.yml', 'w', encoding='utf-8') as file:
            yaml.dump(virtual_receiver_config_dict, file, sort_keys=False)

    @staticmethod
    def create_send_config():
        send_config = {
            'send_config':
                {
                    'send_package_points': 40  # 发送数据包点数
                }
        }
        return send_config

    @staticmethod
    def create_device_info():
        device_info = {
            'device_info': {
                'channel_number': 8,
                'sample_rate': 1000,
                'channel_label':
                    {
                        'POz': None,
                        'PO3': None,
                        'PO4': None,
                        'PO5': None,
                        'PO6': None,
                        'Oz': None,
                        'O1': None,
                        'O2': None
                    }
                }
        }
        return device_info

    def create_data_files(self, target_dir: str, prefix_dir: str, extensions: list[str]):
        # 按照 被试者:block方式构建
        relative_paths = self.__collect_files_by_subdirectories(target_dir, prefix_dir, extensions)
        data_files = {
            'data_files': relative_paths
        }
        return data_files

    @staticmethod
    def create_message():
        message_dict = {
            'message':
                {
                    VirtualReceiverMessageKeyEnum.VIRTUAL_RECEIVER_CUSTOM_CONTROL.value: None
                }
        }
        return message_dict

    @staticmethod
    def __collect_files_by_subdirectories(target_dir: str, prefix_dir: str, extensions: list[str]):
        """
        递归地收集指定目录及其子目录下所有具有指定扩展名的文件的相对路径，
        并按子目录分组。在每个路径前添加预定义的前缀。

        参数:
        root_dir (str): 根目录的路径。
        prefix_dir (str): 添加到每个相对路径前的前缀。
        extensions (list): 文件扩展名列表。

        返回:
        dict: 字典，键是子目录的相对路径，值是该目录下所有指定扩展名文件的相对路径列表，每个路径都带有前缀。
        字典内元素形式
        S1:
            -block_1_dir
            -block_2_dir
        S2:
            -block_1_dir
            -block_2_dir
        """
        results = {}
        root_path = Path(target_dir)

        # 遍历根目录下的所有子目录
        for sub_dir in root_path.iterdir():
            if sub_dir.is_dir():
                # 收集子目录下所有指定扩展名的文件
                files = []
                for ext in extensions:
                    files.extend(list(sub_dir.rglob(f'*{ext}')))

                # 获取每个文件相对于根目录的相对路径，添加前缀，并确保路径分隔符兼容
                relative_files = [
                    f"{prefix_dir}/{str(file.relative_to(root_path)).replace(os.path.sep, '/')}"
                    for file in files
                ]

                # 将结果存储在字典中
                # 注意：这里我们也需要在子目录的相对路径前加上前缀，并确保路径分隔符兼容
                results[str(sub_dir.relative_to(root_path))] = relative_files
        return results


if __name__ == '__main__':
    VirtualReceiverConfigCreator().run()
