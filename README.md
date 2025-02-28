# 介绍
&emsp;&emsp;本项目以https://github.com/IIN-EC-Lab-of-BUPT/A-Brain-Computer-Development-Engine-Framework开源的脑机接口平台系统为基础进行拓展开发，新开发了支持neuroscan采集设备的采集模块，可以将neuroscan设备采集的脑电数据传输到本团队开发的脑机接口平台进行数据处理，提高了采集设备的多样性，为科研人员和开发者在脑电数据采集方面提供了更多选择。

# 使用指南
## 1.安装配置脑机接口平台系统
### 1.1平台系统安装：
&emsp;&emsp;首先确保您已按照https://github.com/IIN-EC-Lab-of-BUPT/A-Brain-Computer-Development-Engine-Framework中的使用指南在您的计算机上配置好脑机接口平台系统，且可以成功运行。
### 1.2替换采集文件夹：
&emsp;&emsp;将https://github.com/IIN-EC-Lab-of-BUPT/A-Brain-Computer-Development-Engine-Framework中app文件夹中的Collector文件夹替换为本链接的Collector文件夹。您可以通过下载本项目代码，然后手动进行文件夹的替换工作。
## 2.在脑机接口平台系统的采集模块配置自己的neuroscan设备
### 2.1配置信息说明：
&emsp;&emsp;在app/Collector/Collector/receiver/neuroscan/NeuroScan.yml文件中，配置neuroscan服务端与客户端连接的地址信息、发送配置与设备信息。
### 2.2连接地址配置：
&emsp;&emsp;连接地址可在Curry软件中配置，并将Curry软件中NetStreaming Server的地址和端口填写至NeuroScan.yml文件。connect_address为“地址：端口号”格式。
### 2.3导联数配置：
&emsp;&emsp;n_chan代表导联数，导联数要填入实验数据传输的导联数量（不包括trigger导），配置文件导联数与实际导联数不一致时系统会报错。
## 3. 在脑机接口平台系统的刺激模块配置neuroscan的trigger发送模式
&emsp;&emsp;本链接在原脑机接口平台系统上提供一种直接通过计算机并口向neuroscan发送trigger的方式，若使用此方式发送trigger，先将原脑机接口平台的app文件夹下的Simulator文件夹替换为本链接的Simulator文件夹，并在app/Stimulator/Stimulator/application/ApplicationImplement.yml中，将trigger_sender改为neuroscan的trigger发送模式，并配置”port”参数为本机并口端口号。若使用外部trigger或其他trigger发送方式，也要确保此yml文件中trigger_sender参数配置为正确的trigger发送方式。