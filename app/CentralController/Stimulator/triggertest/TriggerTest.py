import os
import sys

currentPath = os.path.dirname(__file__)
sys.path.append(currentPath)
sys.path.append(os.path.join(currentPath, r'Neuracle'))
sys.path.append(os.path.join(currentPath, r'Neuroscan'))

from TriggerController import TriggerController
import time


if __name__ == '__main__':

    # # Neuracle串口测试
    neuracleSerial = TriggerController('neuracle', 'serial', 'COM3')
    neuracleSerial.open()
    for i in range(1, 11):
        neuracleSerial.send(i)
        # trigger的发送间隔应大于20ms
        time.sleep(0.1)
    neuracleSerial.close()

    # # Neuracle并口测试
    # neuracleParallel = TriggerController('neuracle', 'parallel', 16376)
    # neuracleParallel.open()
    # for i in range(1, 11):
    #     neuracleParallel.send(i)
    #     # trigger的发送间隔应大于20ms
    #     time.sleep(0.1)
    # neuracleParallel.close()

    # Neuroscan并口测试
    # neuroscanParallel = TriggerController('neuroscan', 'parallel', 16376)
    # neuroscanParallel.open()
    # for i in range(1, 256):
    #     neuroscanParallel.send(i)
    #     # trigger的发送间隔应大于20ms
    #     time.sleep(0.1)
    # neuroscanParallel.close()





