from psychopy import gui


# 受试者id选择
def choice_start_block():
    dlg = gui.Dlg(title="被试信息输入,选择起始开始block")
    dlg.addText("请选择您的ID")
    dlg.addField("Subject ID：", choices=["1", "2", "3", "4", "5", "6"])
    dlg.addText("请选择起始Block ID")
    dlg.addField("Block ID：", choices=[int(i) for i in range(1, 10)])  # 添加Block ID的下拉选择字段
    subject_info = dlg.show()
    if subject_info is not None:
        subject_id = subject_info["Subject ID："]
        block_id = subject_info["Block ID："]  # 获取Block ID
        return subject_id, block_id
    else:
        return None



