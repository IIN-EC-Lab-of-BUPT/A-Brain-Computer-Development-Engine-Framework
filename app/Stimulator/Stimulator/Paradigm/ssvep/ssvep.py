import asyncio
import time
from queue import Queue
from typing import Union
from psychopy import visual, event, core
import random
import os
from loguru import logger
import copy
from ApplicationFramework.api.interface.ComponentFrameworkInterface import ComponentFrameworkInterface
from Common.model.CommonMessageModel import ResultPackageModel, ScorePackageModel
from Stimulator.Paradigm.interface.paradigminterface import ParadigmInterface
from Stimulator.Paradigm.ssvep.config.ssvep_config import SSVEPConfig
from Stimulator.api.model.RandomNumberSeedsModel import RandomNumberSeedsModel
from Stimulator.facade.model.ExternalTriggerModel import ExternalTriggerModel


class SSVEP(ParadigmInterface):
    def __init__(self):
        # 继承父类，请务必保留
        super().__init__()
        '''
        内部已经初始化_proxy, 可通过self._proxy调用
        内部已经初始化_trigger_send, 可通过self._trigger_send调用
        '''
        self.__component_framework: ComponentFrameworkInterface = None
        # trigger控制
        self.__config_dict = {}
        self.current_start_subject_id = None
        self.current_start_block_id = None
        self.feedback_control_message = None

        # trial开始trigger
        self.trial_start_trig: list = None

        # 刺激结束trigger
        self.trial_end_trig: str = SSVEPConfig.TRIAL_END_TRIGGER

        # block启动trigger
        self.block_start_trig: str = SSVEPConfig.BLOCK_START_TRIGGER

        # block结束trigger
        self.block_end_trig: str = SSVEPConfig.BLOCK_END_TRIGGER

        # 数据开始记录trigger
        self.record_start_trig: str = SSVEPConfig.RECORD_START_TRIGGER

        # 数据停止记录trigger
        self.record_end_trig: str = SSVEPConfig.RECORD_END_TRIGGER

        # 总trial数量
        self.trial_num = SSVEPConfig.TRIAL_NUMBER

        # 所有刺激目标的位置
        self.stim_target_pos = SSVEPConfig.STIM_TARGET_POSITION

        # 初始化帧
        self.init_frame = None

        # 刺激帧
        self.stim_frames = []

        # 刺激帧文件路径
        self.frames_file_path = None

        # 实验事件集合
        self.event_set = []

        # 刺激事件
        self.stim_event_list: list = None

        # 起始block_id
        self.start_block_id = None

        # 当前block_id
        self.cur_block_num = None

        # 当前trial_id
        self.cur_trial_num = 0

        # 刺激目标Id
        self.stim_target_order = None

        # 范式运行flag
        self.run_flag = False

        # 当前运行阶段函数
        self.cur_step_func = self.block_start_step_func

        # 反馈结果
        self.feedback_result = None

        # 反馈信息
        self.feedback_message = Queue()

        # 随机数种子
        self.random_number_seeds = None

        # 窗口
        self.window = None

    async def initial(self, config_dict: dict[str, Union[str, dict]] = None):
        # 初始化刺激文件路径
        self.frames_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), r'ssvep/resources')
        # 获取当次实验起始block_id
        self.start_block_id = await self._proxy.choice_start_block()
        if config_dict is None:
            self.__config_dict = config_dict
        else:
            self.__config_dict.update(config_dict)
        # 打开触发器
        await self._trigger_send.open()
        # await self._trigger_send.send(ExternalTriggerModel(time.time(), "5616"))

    async def update(self, config_dict: dict[str, Union[str, dict]] = None) -> None:
        if config_dict is None:
            self.__config_dict = config_dict
        else:
            self.__config_dict.update(config_dict)

    async def prepare(self):
        # 定义psychopy窗口
        self.window = visual.Window(size=(1920, 1080), units='pix', color=(-1, -1, -1), pos=(0, 0),
                                    useFBO=True, allowStencil=True, fullscr=True, screen=0)

        # 显示系统初始化文本
        init_txt = visual.TextStim(win=self.window, text='系统初始化，请保持放松', height=60, color='white',
                                   pos=(-80, 0), units='pix')
        init_txt.draw()
        self.window.flip()

        # 加载初始化帧
        self.init_frame = os.path.join(self.frames_file_path, '1_0.jpg')

        # 加载刺激帧
        for i in range(SSVEPConfig.PRELOAD_FRAME_NUM):
            frame_path = os.path.join(self.frames_file_path, 'image_folder', '0_{}.jpg'.format(i))
            self.stim_frames.append(visual.ImageStim(win=self.window, image=frame_path))

        # 使用已获得的随机数种子
        random.seed(self.random_number_seeds)

        # 生成实验所有刺激事件
        block_num = SSVEPConfig.BLOCK_NUMBER
        # 刺激范式:无重复遍历
        event_list = list(range(1, 41))
        for i in range(block_num):
            random.shuffle(event_list)
            copied_list = copy.deepcopy(event_list)
            self.event_set.append(copied_list)
        # 刺激范式:随机刺激
        # for i in range(block_num):
        #     event_list = [random.randint(1, 41) for _ in range(40)]
        #     copied_list = copy.deepcopy(event_list)
        #     event_set.append(copied_list)

        self.cur_block_num = self.start_block_id - 1
        logger.info('当前block为: block{}'.format(self.start_block_id))

        # 发送数据开始记录trigger
        await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.RECORD_START_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.RECORD_START_TRIGGER))
        logger.info('发送数据开始记录trigger')

        # 显示系统初始化完毕文本
        record_start_wait_time = SSVEPConfig.RECORD_START_WAIT_TIME
        for i in range(record_start_wait_time, 0, -1):
            record_start_txt = visual.TextStim(win=self.window, text='系统初始化完毕，请做好实验准备', height=60,
                                               color='white', pos=(-240, 90), units='pix')
            countdown_txt = visual.TextStim(win=self.window, text='{}'.format(i), height=60, color='white',
                                            pos=(-20, -90), units='pix')
            record_start_txt.draw()
            countdown_txt.draw()
            self.window.flip()
            core.wait(1)

    async def run(self):
        self.run_flag = True
        while self.run_flag:
            await self.cur_step_func()

    async def stop(self):
        self.run_flag = False
        self.cur_step_func = self.trial_start_step_func

    def __finish_experiment(self):
        self.run_flag = False
        logger.info('实验结束')

    async def close(self):
        # 停止刺激
        self.__finish_experiment()

        # 关闭psychopy窗口
        self.window.close()

        # 关闭trigger
        # await self._trigger_send.shutdown()

    async def block_start_step_func(self):
        """
        block开始阶段函数
        """
        await self._proxy.send_information()
        await asyncio.sleep(1)
        logger.info('进入block开始阶段')
        # 发送block开始trigger信号
        await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.BLOCK_START_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.BLOCK_START_TRIGGER))
        logger.info('发送block开始trigger')

        # 刺激事件，对应40个刺激目标
        self.stim_event_list: list = self.event_set[self.cur_block_num]
        # print(self.stim_event_list)

        # trial开始trigger，对应40个刺激目标
        # 此处直接使用刺激目标trigger作为trial开始trigger
        self.trial_start_trig: list = self.event_set[self.cur_block_num]

        # block初始化阶段
        # 生成待刺激序列
        self.stim_target_order = self.__create_stim_target_order()
        logger.info('待刺激序列为:{}'.format(self.stim_target_order))

        # 绘制倒计时界面
        wait_time = SSVEPConfig.BLOCK_START_WAIT_TIME
        for i in range(wait_time, 0, -1):
            exp_start_txt = visual.TextStim(win=self.window,
                                            text='Block{}实验即将开始，请做好准备'.format(self.cur_block_num + 1),
                                            height=60, color='white',
                                            pos=(-180, 90), units='pix')
            countdown_txt = visual.TextStim(win=self.window, text='{}'.format(i), height=60, color='white',
                                            pos=(-20, -90), units='pix')
            exp_start_txt.draw()
            countdown_txt.draw()
            self.window.flip()
            core.wait(1)

        # 切换运行阶段至trial开始阶段
        self.cur_step_func = self.trial_start_step_func

    async def trial_start_step_func(self):
        """
        trial开始阶段函数
        """
        logger.info('进入trial开始阶段')
        self.feedback_message=Queue()
        # 发送trial开始trigger信号
        await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.TRIAL_START_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.TRIAL_START_TRIGGER))
        logger.info('发送trial开始trigger')

        # trial计数加1与事件保持同步
        self.cur_trial_num = self.cur_trial_num + 1

        # 绘制初始帧
        init_frame = visual.ImageStim(win=self.window, image=self.init_frame, pos=(0, 0), units='pix')
        init_frame.draw()

        # 绘制刺激目标提示框
        stim_event = self.stim_target_order[self.cur_trial_num - 1]
        stim_target = stim_event - 1
        logger.info('当前试次刺激目标为:{}'.format(SSVEPConfig.STIM_TARGET[stim_target]))

        self.__draw__target_stim_tip(stim_target)
        self.window.flip()
        core.wait(SSVEPConfig.TRIAL_START_WAIT_TIME)

        # 切换运行阶段至刺激阶段
        self.cur_step_func = self.stim_step_func

    async def stim_step_func(self):
        """
        刺激阶段函数
        """
        logger.info('进入刺激阶段')

        # 刺激帧计数
        frame_num = 0  # 开始时绘制第一帧

        # 获取刺激目标
        stim_event = self.stim_target_order[self.cur_trial_num - 1]
        stim_target = stim_event - 1

        # 获取刺激目标trigger
        stim_target_index = self.stim_event_list.index(stim_event)
        stim_target_trigger = self.trial_start_trig[stim_target_index] - 1
        stim_trigger = SSVEPConfig.TRIGGER_TARGET[stim_target_trigger]

        # 先刷6帧再发trigger可以保证更高的稳定性
        init_frame = visual.ImageStim(win=self.window, image=self.init_frame, pos=(0, 0), units='pix')
        for i in range(6):
            # 绘制初始帧
            init_frame.draw()
            self.__draw_target_tip(stim_target)
            self.window.flip()
        await self._trigger_send.send(ExternalTriggerModel(time.time(), stim_trigger))
        # await self._trigger_send.send(int(stim_trigger))
        logger.info('试次启动标签确认,发送刺激试次trigger:{}'.format(stim_trigger))

        # 开始刺激的时间
        start_stim_time = core.getTime()

        # 控制刺激时常，刺激时间为：(frame_duration/屏幕刷新率)，单位为秒
        # 例如frame_duration为240帧，屏幕刷新率为60hz时，刺激时长为4s
        frame_duration = SSVEPConfig.STIM_FRAME_NUM
        # 动态刺激
        # while frame_num < frame_duration and self.feedback_result is None:
        # 固定时长刺激
        while frame_num < frame_duration:
            stim_frame = self.stim_frames[frame_num % SSVEPConfig.PRELOAD_FRAME_NUM]
            stim_frame.draw()
            # 刺激过程中显示提示三角可能会导致刺激不稳定，如需在刺激过程中设置提示请测试刺激稳定性
            self.__draw_target_tip(stim_target)
            self.window.flip()
            frame_num = frame_num + 1
        await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.TRIAL_END_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.TRIAL_END_TRIGGER))
        # 结束刺激的时间
        end_stim_time = core.getTime()
        logger.info('试次刺激结束,总刺激时间为{},'.format(end_stim_time - start_stim_time))

        # 重新绘制初始帧
        init_frame = visual.ImageStim(win=self.window, image=self.init_frame, pos=(0, 0), units='pix')
        init_frame.draw()
        self.window.flip()

        # 切换运行阶段至trial结束阶段
        self.cur_step_func = self.trial_end_step_func

    async def trial_end_step_func(self):
        """
        trial结束阶段函数
        """

        logger.info('进入trial结束阶段')

        # 发送trial结束trigger
        # await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.TRIAL_END_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.TRIAL_END_TRIGGER))
        logger.info('发送trial结束trigger')

        # 获取刺激目标
        stim_event = self.stim_target_order[self.cur_trial_num - 1]
        stim_target = stim_event - 1

        # 绘制初始帧
        init_frame = visual.ImageStim(win=self.window, image=self.init_frame, pos=(0, 0), units='pix')
        init_frame.draw()

        # 等待结果时间为1s，需根据赛题具体情况进行调整
        await asyncio.sleep(SSVEPConfig.TRIAL_RESULT_WAIT_TIME)
        # logger.info('self.feedback_message为:{}'.format(self.feedback_message))
        if self.feedback_message.empty():
            self.window.flip()
            pass
        else:
            current_message = self.feedback_message.get()
            if current_message == "timeout":
                self.feedback_result = 0
                text = visual.TextStim(win=self.window, text='timeout', height=120, color='red',
                                       pos=(0, 0), units='pix')
                text.draw()
            else:
                self.feedback_result = int(current_message) - 1
                self.__draw_feedback()
            # self.feedback_result = self.feedback_message.get() - 1
            logger.info('当前试次判决结果为:{}'.format(SSVEPConfig.STIM_TARGET[self.feedback_result]))
            # 绘制反馈
            # self.__draw_feedback()
            self.window.flip()
            core.wait(SSVEPConfig.TRIAL_END_WAIT_TIME)

        # 如果block目标已经全部完成
        if self.cur_trial_num == SSVEPConfig.TRIAL_NUMBER:
            self.cur_step_func = self.end
        else:
            self.cur_step_func = self.trial_start_step_func

    async def end(self):
        """
        block结束阶段函数
        """
        logger.info('进入block结束阶段')
        # 发送block结束trigger
        await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.BLOCK_END_TRIGGER))
        # await self._trigger_send.send(int(SSVEPConfig.BLOCK_END_TRIGGER))
        logger.info('发送block结束trigger')

        # 等待该block数据记录停止
        self.cur_block_num += 1

        # 重置当前trial计数
        self.cur_trial_num = 0

        if self.cur_block_num < SSVEPConfig.BLOCK_NUMBER:
            # 绘制block结束提示语
            block_end_txt = visual.TextStim(win=self.window, text='当前block结束，按空格继续实验', height=60,
                                            color='white', pos=(-240, 0), units='pix')
            block_end_txt.draw()
            self.window.flip()
            # 等待空格按下
            event.waitKeys(keyList=['space'])
            # 切换运行阶段至block开始阶段
            self.cur_step_func = self.block_start_step_func
        else:
            exp_end_wait_time = SSVEPConfig.RECORD_END_WAIT_TIME
            for i in range(exp_end_wait_time, 0, -1):
                exp_end_txt = visual.TextStim(win=self.window, text='所有block结束，即将退出实验', height=60,
                                              color='white',
                                              pos=(-150, 90), units='pix')
                countdown_txt = visual.TextStim(win=self.window, text='{}'.format(i), height=60, color='white',
                                                pos=(-20, -90), units='pix')
                exp_end_txt.draw()
                countdown_txt.draw()
                self.window.flip()
                core.wait(1)
            await self._trigger_send.send(ExternalTriggerModel(time.time(), SSVEPConfig.RECORD_END_TRIGGER))
            # await self._trigger_send.send(int(SSVEPConfig.RECORD_END_TRIGGER))
            logger.info('发送数据记录结束trigger')
            # 关闭刺激
            await self.close()

    def __create_stim_target_order(self):
        """
        生成刺激序列
        :return: 返回一个随机的刺激目标Id的list,该list中元素的数量为一个block中的trial数量
        """
        # 从配置文件中获取刺激目标事件
        stim_event = self.stim_event_list
        # 从配置文件中获取一个block中的trial数量
        trial_num = SSVEPConfig.TRIAL_NUMBER
        # 获取刺激目标个数
        stim_target_num = len(stim_event)
        # 需要遍历刺激目标的次数
        cycle_num = int(trial_num / stim_target_num)
        # 刺激目标序列
        stim_target_order = []
        # 每次循环包括所有刺激目标各提示一次
        stim_target_index = [stim for stim in range(stim_target_num)]

        # 固定循环
        for i in range(cycle_num):
            for index in stim_target_index:
                stim_target_order.append(stim_event[index])
        # 随机循环
        # for i in range(cycle_num):
        #     random.shuffle(stim_target_index)
        #     for index in stim_target_index:
        #         stim_target_order.append(stim_event[index])

        # 获取剩余trial数量
        residual_num = trial_num - stim_target_num * cycle_num

        if residual_num > 0:
            # 固定选择剩余数量的目标添加到刺激序列中
            for index in range(residual_num):
                stim_target_order.append(stim_event[index])
            # 随机选择剩余数量的目标添加到刺激序列中
            # residual_stim_target_index = random.sample(stim_target_index, residual_num)
            # for index in residual_stim_target_index:
            #     stim_target_order.append(stim_event[index])

        return stim_target_order

    def __draw__target_stim_tip(self, stim_target):
        """
        刺激开始前绘制刺激目标提示框
        :param stim_target: 刺激目标
        :return: None
        """
        # 绘制目标提示框
        stim_target_index = stim_target
        target_pos = self.stim_target_pos[stim_target_index]
        rectangle_pos = [target_pos[0] + 5, target_pos[1] + 5]
        rectangle = visual.Rect(win=self.window, width=165, height=165, lineWidth=5,
                                units='pix', lineColor='red', pos=rectangle_pos, fillColor=None)
        rectangle.draw()

    def __draw_target_tip(self, stim_target):
        """
        刺激过程中绘制目标提示
        :param stim_target: 刺激目标
        :return: None
        """
        # 获取该刺激目标的位置
        target_pos = self.stim_target_pos[stim_target]

        # 计算提示红三角位置
        triangle_tip_pos = [target_pos[0] + 5, target_pos[1] - 110]

        triangle_tip = visual.Polygon(win=self.window, edges=3, units='pix', radius=30, fillColor='red',
                                      lineColor='red', pos=triangle_tip_pos)
        triangle_tip.draw()

    def __draw_feedback(self):
        """
        绘制识别结果提示框
        :param stim_target: 刺激目标
        :return: None
        """
        # 根据赛题要求绘制结果反馈提示
        # if self.feedback_result == stim_target:
        #     color = 'green'
        # else:
        #     color = 'yellow'
        color = 'blue'
        feedback_event = self.feedback_result + 1

        if feedback_event in self.stim_event_list:
            stim_target_index = self.feedback_result

            # 绘制反馈结果提示框
            target_pos = self.stim_target_pos[stim_target_index]
            rectangle_pos = [target_pos[0] + 5, target_pos[1] + 5]
            rectangle = visual.Rect(win=self.window, width=165, height=165, lineWidth=5,
                                    units='pix', lineColor=color, pos=rectangle_pos)
            rectangle.draw()

    # 接收trial反馈结果
    async def receive_feedback_message(self, feedback_message: ResultPackageModel):
        self.feedback_message.put(feedback_message.result)

    # 接收中控发送的随机数种子
    async def receive_random_number_seeds(self, random_number_seeds: RandomNumberSeedsModel):
        self.random_number_seeds = random_number_seeds.seeds

    async def set_component_framework(self, component_framework: ComponentFrameworkInterface):
        self.__component_framework = component_framework
