本模块基于python3.8版本

Neuracle的接口实现位于Neuracle包中，Neuroscan的接口实现位于Neuroscan包中

Neuracle支持串口或并口发送，Neuroscan只支持并口发送

使用者只需要参考Trigger接口说明调用TriggerController.py文件即可

Trigger测试程序位于TriggerTest.py文件中

注意：由于并口每次发送trigger后需要重新将引脚电平置为低电平，所以使用并口发送trigger的间隔请大于20ms

# 前期准备

### 检查是否可正确识别串口/并口

右键我的电脑—管理—设备管理器，检查串口/并口是否可以正确识别，如果未正确识别则应安装相应驱动。串口驱动在安装Neuracle软件时安装，并口驱动请按照并口卡的型号搜索其相应驱动。正确识别串口/并口后请记录其端口号。如：串口为COM3；并口端口号查看：右键并口—属性—资源—I/O范围，将首位16进制数换算为10进制，如：3FF8换算为16376.

### 安装inpoutx64驱动

使用并口发送trigger前需要安装inpoutx64对应的驱动，驱动位于TriggerDependency—1—Win32下，双击InstallDriver.exe即可安装驱动。

### 配置串口/并口

##### USB Trigger配置

a.关闭USB选择性暂停
设置 - 电源和睡眠 - 其他电源设置 - 选择电源计划 - 选择“高性能模式”- 更改计划设置 - 更改高级电源设置 - 找到“USB设置”- USB选择性暂停设置： 设置为“已禁用”(系统默认为"已启用"）
b.USB 端口延迟设置
我的电脑-右键-属性-左侧边栏"设备管理器" - 与TriggerBox 连接的USB接口（安装TriggerBox驱动后，通常位于 端口(COM和LPT)-USB Serial Port(COM X) 位置) - 右键”属性“-端口设置-高级
BM选项中 延迟计时器(毫秒) - 修改设置为'1'(Windows 10 系统安装驱动后默认设置为16ms)

##### 通过PCI-Express 转并口 发送Trigger 配置

关闭PCI-Express并口 链接状态电源管理
设置 - 电源和睡眠 - 其他电源设置 - 选择电源计划 - 选择“高性能模式”- 更改计划设置 - 更改高级电源设置 - 找到“PCI Express”-链接状态电源管理： 设置为“关闭”(系统默认即为"关闭"）

##### 485接口接收Trigger配置

我的电脑-空白处点右键-属性-设备管理器-端口(COM和LPT)-确定485接口转USB连接线所对应的COM口-右键属性-端口设置-高级-修改对应COM端口号为COM12

# Trigger接口说明

### 实例化TriggerController

```python
trigger = TriggerController(eegServerType, triggerHandle, port)
```

```python
:param eegServerType: 输入'neuracle'则使用neuracle的trigger系统,输入'neuroscan'则使用neuroscan的trigger系统
:param triggerHandle: 输入'serial'表示使用串口,输入'parallel'表示使用并口
:param port: 串口/并口所对应的端口,如:neuracle串口输入'COM3'(字符串格式),neuracle/neuroscan并口输入32760;
```

### 打开端口

```python
trigger.open()
```

### 发送Trigger事件

```python
trigger.send(event)
```

```python
:param event: 输入想输入的trigger值,取值范围为1-255之间的整数
```

### 关闭

```python
trigger.close()
```

