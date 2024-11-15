from psychopy import gui


# 受试者id选择
def register_subject():
    dlg = gui.Dlg(title="被试信息输入")
    dlg.addText("请选择您的ID")
    dlg.addField("Subject ID：", choices=["1", "2", "3", "4", "5", "6"])
    subject_info = dlg.show()
    if subject_info is not None:
        subject_id = subject_info["Subject ID："]
        return subject_id
    else:
        return None



