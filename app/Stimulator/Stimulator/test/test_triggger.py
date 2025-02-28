import ctypes
import time

# 定义并口地址
PARALLEL_PORT_ADDRESS = 20472  # 并口地址，根据实际情况修改

# 加载 inpoutx64.dll 驱动程序
try:
    inpout32 = ctypes.WinDLL(r'F:\bci-framework\eegSystem\app\Stimulator\Stimulator\facade\TriggerSend\inpoutx64.dll')
    print('inpoutx64.dll 驱动程序加载成功')
except Exception as e:
    print(f"加载 inpoutx64.dll 驱动程序失败: {e}")
    exit()

# 检查驱动程序是否已加载
if not inpout32.IsInpOutDriverOpen():
    print("inpoutx64 驱动程序未加载，请检查安装状态")
    exit()


def send_data_to_parallel_port(port, data):
    """
    向并口发送数据
    :param port: 并口地址
    :param data: 要发送的数据，应为一个字节（0-255）
    """
    try:
        # 发送数据
        inpout32.DlPortWritePortUchar(port, data)
        print(f"发送数据: {data}")

        # 等待一段时间，以便数据稳定
        time.sleep(0.1)

        # 读取并口状态

        received_data = inpout32.Inp32(port)
        print(f"读取数据: {received_data}")

        # 比较发送的数据和读取的数据
        # if received_data == data:
        #     print("数据发送成功，读取的数据与发送的数据一致")
        # else:
        #     print("数据发送失败，读取的数据与发送的数据不一致")

    except Exception as e:
        print(f"发送数据时发生错误: {e}")


# 示例：发送数据 0x55
send_data_to_parallel_port(PARALLEL_PORT_ADDRESS, 12)