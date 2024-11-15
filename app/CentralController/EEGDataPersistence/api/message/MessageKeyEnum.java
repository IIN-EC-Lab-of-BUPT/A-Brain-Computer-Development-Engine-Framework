package com.coreplantform.EEGDataPersisence.api.message;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum MessageKeyEnum {
    COMMAND_CONTROL("command_control"),

    GROUP_1.DATA("group_1.data"),//脑电数据传输

    GROUP_2.DATA("group_2.data"),//脑电数据传输
    GROUP_3.DATA("group_3.data");//脑电数据传输
    private final String messageKey;


}
