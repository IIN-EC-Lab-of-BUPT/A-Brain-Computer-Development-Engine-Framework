import argparse
import asyncio
import os
from ApplicationFramework.launcher.Launcher import Launcher


async def startup():

    # 创建解析器
    parser = argparse.ArgumentParser(description="Script to connect a daemon at a specified IP and port.")
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help="IP address to bind the daemon. Default is localhost (127.0.0.1).")
    parser.add_argument('--port', type=int, default=8864, help="Port number for the daemon. Default is 8864.")

    # 解析命令行参数
    args = parser.parse_args()
    print(f"输入参数: {args}")
    launcher = Launcher()
    launcher.configure(args.ip, args.port)
    async with launcher:
        print('component 运行结束')

if __name__ == '__main__':
    os.environ['PYTHONASYNCIODEBUG'] = str(int(1))  # 启用debug模式
    asyncio.run(startup())
