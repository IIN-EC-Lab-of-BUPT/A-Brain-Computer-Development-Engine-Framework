# 一、开始使用



## 1、介绍

&emsp;&emsp;为了加速脑机接口应用落地、改善脑机接口科研流程。我们团队开发了脑机接口平台系统。可以使得理论研究和算法分析时间大幅缩短，可重复复用已有技术模块，便捷开展理论研究。使用平台提供的功能模块快速搭建数据采集及分析平台，完成参数迭代优化，可以大幅提升科研实验效率。通过快速搭建在线系统，可将已验证过的算法直接部署于在线平台上极大缩短在线系统开发时间。还可通过平台便捷实现与已有算法的横向测评，使用标准指标对算法结果进行客观评估。平台中的各个组件由守护进程、组件接口、组件应用三个部分组成。目前已有基本的刺激组件、采集组件、中控组件、处理组件。用户也可通过组件接口自定义组件应用。  

&emsp;&emsp;平台可服务于初入脑机领域的算法新进学习者，新进学习者可以通过此套系统快速学习脑机相关领域的知识并迅速开始进行算法研究。使得学习者无需关心系统底层实现，全心全意投入算法研究、低代码模式编写处理算法，只考虑核心计算逻辑。直接部署已有算法及配套数据，极大简化算法验证流程。
   
&emsp;&emsp;进行快速在线验证的算法工程师。本系统可以对算法进行快速在线验证，避免开发人员在验证环节造成时间上的浪费。通过采用本系统，可以快速地在工程上进行集成操作，并可以直接进行验证，极大的缩短了耗费的时间，从而使得产品可以快速可以落地。


## 2、快速开始

&emsp;&emsp;我们提供了一个完整的SSVEP刺激范式的示例，首先需要通过链接下载各组件的守护进程：https://pan.baidu.com/s/1KLm859mtxRWjxw9uOnKkUg?pwd=o1sq ，将下载到的proceed文件夹放在与app文件夹同级目录下，项目需要使用到jdk8与python3.10，请下载并配置环境变量，python需要自行下载相关依赖包，通过requirements.txt文件可以看到所有需要下载的依赖包。环境准备好之后，启动neoracle采集软件，eegSystem文件夹下有1至4的执行脚本，需要依次点击，其中脚本1会启动中控模块的守护进程。脚本2会启动中控模块。并弹出中控的ui界面。脚本3会启动其它模块的守护进程，包括处理模块、采集模块、刺激模块。脚本4则会启动其它模块。全部启动之后，在刺激模块弹出选择被试id与起始block的ui界面后选择确定，接着在中控的ui界面中点击start即可开始实验。

**注意事项**：

&emsp;&emsp;在启动脚本1后，守护进程会创建zookeeper和kafka服务，可能无法一次成功，需要等待其自动重试直到成功后再执行后续脚本。建议每个脚本执行后都等待其命令行稳定后再执行下一个脚本。

&emsp;&emsp;若遇到中控ui界面消失，可以执行central_ui.bat脚本重新打开ui界面。

&emsp;&emsp;Neuracle需要配置triggerBoxHandle和port参数，在app/Stimulator/Stimulator/ApplicationImplement.yml文件中进行配置修改，串口请输入'serial',并口请输入'parallel',输入为字符串格式，串口/并口所对应的端口,如:串口输入'COM3'(字符串格式),并口输入32760

## 3、调试方式

&emsp;&emsp;当使用者需要对某个组件进行修改调试以实现自己的脑机实验时，先执行脚本1、2，开启中控以及它的守护进程后。可以通过app文件夹下分别执行不同组件的脚本来分别启动不同组件及其守护进程。带有proceed后缀的为守护进程的启动脚本。例如，需要手动调试算法，可以执行脚本1和2后，再分别执行processhub__proceed.bat，processhub.bat,collector_proceed.bat,collector.bat,stimulator_proceed.bat,stimulator.bat，之后可以自行启动Algorithm算法程序。脚本执行程序使用的是文件夹中的python310，内含程序运行所需的所有包，请使用该python解释器进行调试。

&emsp;&emsp;注意：需要先启动组件的守护进程才能启动组件程序。
# 二、架构设计

## 1、整体架构
&emsp;&emsp;在本系统的设计中，每个组件都应有一个对应的节点管理组件，称为守护进程，它有着消息通信的作用，负责各类消息数据、消息、指令通信，以数据流方式屏蔽各类组件的功能细节，还能作为服务注册中心，负责各类服务注册、生命周期管理、健康状态监测以及服务异常报告等。使用该组件接口会提供诸如sendMessage、register、subscribeTopic等接口方法给应用组件使用。应用组件只需要调用组件接口提供的诸多方法，不需要关心方法具体实现细节，即可完成组件注册、消息订阅、消息发送等功能。

&emsp;&emsp;核心平台可独立支撑完整脑机接口应用，在本系统中，研究人员只需要开发最简单的数据处理算法（数据处理组件）以及系统刺激范式（系统刺激组件），即可搭建完整的在线实验系统。组件可以使用组件接口提供的各种方法在组件内部构建组件功能。我们已经完成了脑电实验所需的四个基本模块的实现。分别为：
### 中控模块
&emsp;&emsp;中控系统将用于对多个子系统进行集中监控和管理。中控会监控各个组件的注册请求。各组件之间通信的topic可以向中控申请，在绑定Topic的时候无需指定topic。当组件未指定topic时，由中控分发topic。中控可以获取所有组件的状态,包括组件信息，所属组及状态，并向各个组件发送启动、停止命令。
### 刺激模块
&emsp;&emsp;刺激组件负责范式的呈现。范式呈现过程包括trigger的发送，选择本次实验的起始block，每个block开始前的information包（包含被试者信息和jiang 呈现的block id）的发送。使用者需要实现paradigminterface接口，（框架提供了Neuracle的trigger发送，和external trigger的发送，如果有使用其它的trigger发送设备，需要实现TriggerSendInterface，在paradigm会通过该接口实现发送trigger），其中paradigminterface作为范式的呈现，TriggerSendInterface作为发送器负责trigger信息的发送。
### 采集模块
&emsp;&emsp;采集组件负责数据接收与转发。包括放大器数据接入、离线数据加载、发送数据封包等功能。使用者需要实现ReceiverInterface和DataSenderInterface两个接口。其中ReceiverInterface作为接收器负责与数据采集设备连接及数据接收，DataSenderInterface作为发送器负责数据封包及数据转发。
### 处理模块
&emsp;&emsp;处理组件负责数据的处理与反馈，处理模块分为算法端和ProcessHub两部分，这两个部分为两个独立的进程。两个进程间通过grpc进行通信。Task调用组件接口后通过守护进程与其他组件进行通信。数据由采集模块采集之后，通过kafka传输给task的守护进程后，由ProcessHub通过grpc传输给算法端。算法端对数据进行计算处理后将结果通过grpc报告给ProcessHub后由ProcessHub对结果进行处理后调用组件接口通过守护进程发送出去。使用者需要实现AlgorithmInterface接口来接入自己的算法。在本示例中，ProcessHub未对数据与报告结果做任何处理，仅作数据的转发。
# 三、实现
&emsp;&emsp;在本系统中，组件接口使用Grpc+Protobuf对守护进程进行远程调用，gRPC是一个高性能的远程过程调用（RPC）框架，而Protobuf（Protocol Buffers）则是一种轻量级的数据交换格式，可以高效地序列化结构化数据。二者结合可以守护进程则通过Kafka进行通信，者是一个分布式的，支持多分区、多副本，基于 Zookeeper 的分布式消息流平台，是一款开源的基于发布订阅模式的消息引擎系统。这样每个组件都可以通过自身的守护进程与其他组件间接地进行通信。

&emsp;&emsp;守护进程会通过注册中心zookeeper来管理各个组件的注册情况。每个组件在注册时需要提供组件id和组件类型以及组件信息，中控会通过grpc的服务端流检测组件的注册情况并作出操作，注册成功之后会由守护进程在zookeeper上将组件的各自信息记录下来。

# 四、组件使用说明
&emsp;&emsp;只需要通过修改处理模块和刺激模块，即可实现使用者自己的在线实验。


## 1、处理模块

&emsp;&emsp;想要替换现有算法，需要根据Algorithm\method\interface\AlgorithmInterface.py中的AlgorithmInterface类实现算法类，并将算法类名称和路径写入“Algorithm\config\AlgorithmConfig.yml”文件中。使用者需在算法类中重写以协程的形式重写run方法，并在获取设备信息、获取数据和汇报结果时使用await关键字异步执行。框架运行时，会主动调用run方法。因此使用者需要在run方法中读取数据，进行计算，并报告结果。

&emsp;&emsp;其中使用者可以通过调用_proxy属性的get_source方法，并传入str类型的数据源名称参数，获取数据源（SourceInterface实例）。获取到数据源之后，可以使用await关键字异步调用其“get_device”方法获取设备信息（AlgorithmDeviceObject实例），调用其“get_data”方法获取一个数据包（AlgorithmDataObject实例）。在需要汇报结果时，使用者可以实例化一个AlgorithmResultObject类型的实例，并将结果赋值给该对象的“result”属性。随后将该实例作为参数传入并调用“_proxy”属性的report方法。

## 2、刺激模块

&emsp;&emsp;使用刺激框架需要实现paradigminterface接口

&emsp;&emsp;框架会注入trigger发送器和一个proxy代理类，实现类可通过调用self._trigger_send的方法进行trigger的启动，发送，停止等操作，还可通过调用self._proxy的方法得到本次实验的起始block和发送每个block开始前的information包。使用者可以在在run方法内编写刺激逻辑。使用receive_feedback_message方法可以接收算法端处理后的反馈结果。

## 3、采集模块
&emsp;&emsp;系统提供在线和离线两种模式，离线模式下将app/Collector/Collector/application/ApplicationImplement.yml中的receiver_class_file改为Collector/receiver/virtual_receiver/VirtualReceiverImplement.py，receiver_class_name改为VirtualReceiverImplement，将数据放在app/Collector/Collector/receiver/virtual_receiver/data下，.dat数据文件中的数据是4字节的float类型以字节存储。例如一个8导的数据和一个trigger导，采样1000次，则文件会是（8+1）x4x1000字节大小。

&emsp;&emsp;在线模式则将receiver_class_file改为Collector/receiver/neuracle/NeuracleReceiverImplement.py，receiver_class_name改为NeuracleReceiverImplement。

# 五、自定义组件开发
用户可自行通过框架在通用方法中使用组件接口api结合框架中的通用数据结构构建自己的自定义组件。
## 1、通用方法定义
### (1)	initial ():
组件或服务初始化时所调用接口函数。该函数内不可调用其他支持服务，只能用于初始化自身参数。通常在该函数内读取配置信息并初始化。
### (2) startup ()/run():
组件或服务启动函数或执行函数。该函数为组件或服务的入口函数，在启动时，框架会调用该函数执行相关操作。在该函数内，可以执行相关处理操作，并调服务支持接口。如果为run()函数，则通常需要保证组件持续运行，因此需要在run()函数末尾插入等待事件，例如 await asyncio.Event.wait()，直到接收到退出指令(如asyncio.Event.set())。
### (3) shutdown ()/exit():
组件或服务关闭退出函数。当系统关闭时，框架会调用该函数发起退出操作指令。组件或服务需要自行完成关闭退出操作，并清理缓存信息。
## 2、通用数据结构定义
### (1)	DataMessageModel
数据消息核心类，其中package可以为下列任意一种消息结构(除ReportSourceInformationModel外)。
### (2)	DevicePackageModel
设备信息消息包
### (3)	DataPackageModel
数据内容消息包，其中data_position: float表示该数据包所包含的数据起始时间点，data为数据内容。
### (4)	EventPackageModel
事件消息包，其中event_position为list[float]数据类型，可包含多个事件的点数位置。event_data为list[str]数据类型，可包含多个事件的事件内容。event_position和event_data的list长度必须一致。
### (5)	InformationPackageModel
实验信息包，用于表示当前数据来自哪位被试，第几个block
### (6)	ControlPackageModel
控制指令消息包，用于传递停止消息指令。
### (7)	ResultPackageModel
结果反馈消息包，算法端处理完结果消息后，封装成此类数据格式，并发送给ProcessHUb端。其中report_source_information: list[ReportSourceInformationModel]表示发送此数据包时所用的各个数据源数据使用情况，result字段为结果报告内容。
### (8)	ReportSourceInformationModel
结果报告时数据源的数据量使用情况，即结果报告时算法分别读取了每个数据源多少数据点数。source_label:数据源的标签; position:所用数据点数。

### &emsp;&emsp;通过在通用方法中仿照示例代码使用组件接口的中Api方法结合这些通用数据结构，即可自行开发自定义组件。	

# 六、组件接口Api
## 1、Config Api
### 1.async def get_global_config(self):全局配置读取
读取/core/config内容并返回配置（配置以dict<str,str or dict>形式返回）
### 2.async def register_global_config_update(self, callback,): 全局参数配置更新回调注册
callback: 输入 dict<str,str or dict>形式参数，无返回
### 3.async def update_global_config(self, config_dict ): 手动更新全局配置
修改全局配置信息,config_dict :dict <string,str/dict>
返回值："配置修改成功通知"：枚举类型
### 4.async def cancel_add_listener_on_global_config(self) -> StatusEnum:取消全局参数配置更新回调注册
返回值："取消成功通知"：枚举类型
## 2、Message Api
### 1.	async def bind_message (self,message_model:MessageModel) -> MessageModel : 话题绑定
MessageModel内容：service_id:str, message_key:str, topic:str
绑定指定服务的指定话题，如果话题不存在则创建，订阅与发送消息前都需要先绑定消息
守护进程或中央控制器填入具体topic，也可写入明确的topic
- service_id: 指定服务ID，该参数可为空，表示创建本服务事件
- message_key: 指定messageKey
- topic: 指定topic，该参数默认为空，表示由中控填写指定topic
返回参数：事件结构体，包含service_id:str、message_key:str、topic:str
### 2.async def add_listener_on_bind_message(self, callback)：话题绑定监听
callback输入参数AddListenerOnBindMessageModel内容:service_id:str、message_key:str、topic:str
callback 返回参数MessageModel内容：service_id:str、message_key:str、topic:str
### 3.async def get_topic_by_message_key(self, message_key: str, component_id: str = None) -> topic:str :通过message_key获取topic
返回值 topic:str
### 4.async def subscribe_message(self, callback, message_key:str): 话题订阅
callback: SubscribeTopicCallbackInterface, message_key:str
直接订阅指定服务的指定话题，如果message_key未绑定，则抛出未绑定异常
- message_key: 指定messageKey
- callback: 触发回调时的调用方法输入参数message: bytes
### 5.async def send_message(self, message_key, value): 消息发送
message_key:str, value:bytes
守护进程向消息中间件写入内容
输入参数：- message_key: 指定messageKey  - value: 准备的事件内容
### 6. async def send_unary_message(self, message_key: str, message: bytes) -> None:结果汇报
守护进程向消息中间件写入内容
输入参数： - message_key: 指定messageKey - message: 准备的结果内容
### 7. async def unsubscribe_source(self, message_key: str) -> StatusEnum:取消订阅
返回值：StatusEnum枚举类型
### 8.  async def cancel_add_listener_on_bind_message(self) -> StatusEnum: 取消话题绑定监听
返回值：StatusEnum枚举类型
## 3、Component Api
### 1.async def component_register(self, component_model: ComponentModel) -> ComponentModel:组件注册
输入参数：ComponentModel 内容：
-component_id: 本服务组件ID，从配置文件中读取，如果为空，从环境变量中读取，如果为空，则以component_type+ UUID为本服务组件ID
-component_type: 本服务组件类型，不可为空。
-component_info: 组件配置信息。Dict嵌套形式，用于向中央控制器发送参数信息。
返回值：ComponentModel
### 2.async def get_component_info(self, component_id: str = None): 获取指定组件信息
输入参数： - component_id: 指定组件ID，如果为空，则指代本组件自身
返回参数：GetComponentInfoModel:
-component_id: 本服务组件ID 
-component_type: 本服务组件类型
-component_info: 组件配置信息,Dict嵌套形式。
### 3.async def add_listener_on_register_component (self, callback): 组件注册监听回调
callback输入参数AddListenerOnRegisterComponentModel：
-component_id : str, -component_type: str, -component_info : dict
callback 返回ComponentModel
-component_id : str, -component_type: str, -component_info : dict
### 4. async def update_component_info(self, component_info: dict[str, Union[str, dict]], component_id:str=None)-> StatusEnum: 修改组件配置信息
- component_id: 指定组件ID，如果为空，则指代本组件自身
- component_info : dict 更新的组件信息
返回值：更新成功枚举
### 5.async def add_listener_on_update_component_info (self, callback, component_id): 监听组件组件配置信息更新回调
输入值：
-component_id: str，监听的组件对象
-callback的输入参数AddListenerOnUpdateComponentInfoComponentModel：
-component_id : str, component_info : dict
Callback无返回值
### 6. async def unregister_component(self) -> StatusEnum:本组件注销
返回值：注销成功枚举
### 7.async def add_listener_on_unregister_component(self, callback: AddListenerOnUnregisterComponentCallbackInterface) -> None:组件注销监听
callback包含输入参数AddListenerOnUnregisterComponentModel：
-component_id : str, component_type: str, component_info : dict
callback 无需返回
### 8. async def get_all_component(self) -> list[str]:获取所有组件信息
返回值：component_id的list列表
### 9. async def cancel_add_listener_on_register_component(self, component_id: str = None) -> StatusEnum:取消组件注册监听回调
返回值：取消组件注册监听回调成功枚举
### 10.async def cancel_add_listener_on_update_component_info(self, component_id: str=None)->StatusEnum:取消监听组件组件配置信息更新回调
返回值：取消监听组件组件配置信息更新回调成功枚举
### 11. async def cancel_add_listener_on_unregister_component(self, component_id: str = None) -> StatusEnum:取消组件注销监听
返回值：取消组件注销监听成功枚举
### 12.async def update_component_state(self, component_status: ComponentStatusEnum, component_id: str = None) -> StatusEnum:更新组件状态
- component_id: 指定组件ID，如果为空，则指代本组件自身
- component_status: ComponentStatusEnum
返回值：枚举类型
### 13.async def add_listener_on_update_component_state(self, callback: AddListenerOnUpdateComponentStateCallbackInterface, component_id: str = None) -> None:监听组件状态更新
- component_id: 指定组件ID，如果为空，则指代本组件自身
callback包含输入参数AddListenerOnUpdateComponentStateModel：
component_id : str, component_status: ComponentStatusEnum
callback 无需返回
### 14. async def get_component_state(self, component_id: str = None) -> ComponentStatusEnum:获取组件状态
- component_id: 指定组件ID，如果为空，则指代本组件自身
返回值：ComponentStatusEnum枚举

### 15.async def cancel_add_listener_on_update_component_state(self, component_id: str=None) -> StatusEnum:取消组件状态更新监听
- component_id: 指定组件ID，如果为空，则指代本组件自身
返回值：StatusEnum枚举
## 4、Connection Api
### 1. async def shutdown(self) -> StatusEnum:关闭连接
返回值："关闭连接成功通知"：枚举类型
### 2. async def add_listener_on_request_component_stop(self, callback: AddListenerOnRequestComponentStopCallbackInterface)-> None:监听请求组件停止
callback包含输入参数
request : str
callback 无需返回
### 3. async def cancel_add_listener_on_request_component_stop(self) -> StatusEnum:取消监听请求组件停止
返回值："关闭连接成功通知"：枚举类型



