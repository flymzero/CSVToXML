#coding:utf-8
import wx
import os
from FileDeal import FILEDEAL, ListData
from ObjectListView import ObjectListView, ColumnDefn
import WXListView
from WXListView import ListCtrlView
import pyperclip
import time

class GRMUI(wx.Frame):
    #文件处理类
    fd = FILEDEAL()
    #第一个文件路径
    filename = ""
    #中间数据
    middenDatas = []
    #多个文件列表
    csvFilesPathList = []
    #输出文件名列表
    xmlNamesList = []


    def __init__(self):
        super(GRMUI, self).__init__(None, wx.ID_ANY, "GRM", size=(1000,700), pos=(20,20))
        #self.SetIcon(wx.Icon('GRM.ico', wx.BITMAP_TYPE_ICO))
        self.panel = wx.Panel(self)
        self.createMenu()
        self.addSubViews()
        self.panel.Fit()
        self.Show()
        tt = time.time()

        # if tt > 1492788449.00:
        #     dlg = wx.MessageDialog(None, u"测试过期", u"提示", wx.YES_NO | wx.ICON_QUESTION)
        #     if dlg.ShowModal() == wx.ID_YES or dlg.ShowModal() == wx.ID_NO:
        #         self.Close()
        #     dlg.Destroy()

    def createMenu(self):
        '''
        添加菜单栏
        '''
        menubar = wx.MenuBar()

        file = wx.Menu()
        fileMenu = file.Append(101, u'&打开文件', 'Open a new document')
        file.AppendSeparator()
        filesMenu = file.Append(102, u'&打开文件夹', 'Open the documents')
        help = file.Append(103, u'&帮助', 'Open the documents')
        #help = wx.Menu()

        menubar.Append(file, u'&打开')
        #menubar.Append(help, u'&帮助')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OpenFileFun, fileMenu)
        self.Bind(wx.EVT_MENU, self.OpenFilesFun, filesMenu)
        self.Bind(wx.EVT_MENU, self.QQ, help)

    def QQ(self, event):
        self.ShowMessage("--.-/--.-/---../.----/....-/----./--.../..---/...--/--.../...--")

    #打开文件
    def OpenFileFun(self, event):
        file_wildcard = u"CSV 文件 (*.csv)|*.csv"
        dlg = wx.FileDialog(self, "Open paint file...",
                            os.getcwd(),
                            style=wx.OPEN,
                            wildcard=file_wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            suc, rep =self.fd.CSVToListFun(dlg.GetPath())
            if suc:
                self.cleanAllData()
                self.filename = dlg.GetPath()
                self.csvFilesPathList.append(dlg.GetPath())
                self.getMiddenDatas(rep)
                self.csvListView.SetObjects(self.middenDatas)
                for i in range(len(self.middenDatas)):
                     self.csvListView.SetCheckState(self.middenDatas[i], True)
                self.csvListView.RefreshObjects(self.middenDatas)
                #修改保存目录
                if len(self.filePathView.GetLabelText()) == 0:
                    self.filePathView.SetLabelText(os.path.dirname(self.filename))
            else:
                self.ShowMessage(rep)
        dlg.Destroy()

    def OpenFilesFun(self, event):
        '''
        打开文件夹 
        '''
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            dirPath = dlg.GetPath()
            tempFileList = []
            for filename in os.listdir(dirPath):
                fileType = os.path.splitext(filename)[1]
                if fileType == '.csv' or fileType == '.CSV':
                    tempFileList.append(dirPath+"\\"+filename)

            if len(tempFileList) == 0:
                self.ShowMessage(u"文件夹内没有csv文件")
            else:
                suc, rep = self.fd.CSVToListFun(tempFileList[0])
                if suc:
                    self.cleanAllData()
                    self.filename = tempFileList[0]
                    self.csvFilesPathList = tempFileList
                    self.getMiddenDatas(rep)
                    self.csvListView.SetObjects(self.middenDatas)
                    for i in range(len(self.middenDatas)):
                        self.csvListView.SetCheckState(self.middenDatas[i], True)
                    self.csvListView.RefreshObjects(self.middenDatas)
                    # 修改保存目录
                    if len(self.filePathView.GetLabelText()) == 0:
                        self.filePathView.SetLabelText(os.path.dirname(self.filename))
                else:
                    self.ShowMessage(rep)
        print self.csvFilesPathList;
        dlg.Destroy()

    def addSubViews(self):
        self.gbSizer = wx.GridBagSizer(5,5)
        #text
        self.gbSizer.Add(wx.StaticText(self.panel, label=u"CSV目录"), span=(1, 4),pos=(0, 0), flag=wx.LEFT|wx.CENTER, border=10)
        self.gbSizer.Add(wx.StaticText(self.panel, label=u"XML目录"), span=(1, 6),pos=(0, 4), flag=wx.LEFT, border=10)

        self.createCSVListView()
        self.createXMLListView()
        self.addBottomViews()
        # self.gbSizer.AddGrowableCol(4)
        self.gbSizer.AddGrowableCol(6)
        self.gbSizer.AddGrowableRow(1)
        self.panel.SetSizer(self.gbSizer)

    def createCSVListView(self):
        self.csvListView = ListCtrlView(self.panel,style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.csvListView.SetEmptyListMsg(u"请先打开文件(夹)")
        keyColumn = ColumnDefn("CSV_Key", "left", 250, "key")
        self.csvListView.SetColumns([
            keyColumn
            #ColumnDefn("Value", "left", 250, "value"),
        ])
        self.csvListView.InstallCheckStateColumn(keyColumn)
        self.csvListView.Bind(WXListView.EVT_OVL_CHECK_EVENT, self.HandleCheckbox)
        self.csvListView.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.CSVRightClick)
        self.gbSizer.Add(self.csvListView, span=(8, 4), pos=(1, 0), flag=wx.LEFT|wx.TOP|wx.EXPAND, border=5)

    def createXMLListView(self):
        self.xmlListView = ObjectListView(self.panel,style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.xmlListView.SetEmptyListMsg(u"请先打开文件(夹)")
        self.xmlListView.SetColumns([
            ColumnDefn("XML_Key", "left", 200, "keyCopy"),
            ColumnDefn(u"XML_Value (填入CSV_Key,可用+累加)", "left", 400, "keyMap",isSpaceFilling=True),
        ])
        self.xmlListView.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        self.gbSizer.Add(self.xmlListView, span=(8,6), pos=(1, 4), flag=wx.TOP|wx.RIGHT|wx.EXPAND, border=5)

    #右击菜单
    def CSVRightClick(self, event):
        menu = wx.wx.Menu()
        menu.Bind(wx.EVT_MENU, self.CSVMenuSelection)
        for (id, title) in WXListView.MenuTitleDict1.items():
            menu.Append(id, title)
        self.PopupMenu(menu, event.GetPoint())
        menu.Destroy()

    # 右击菜单操作
    def CSVMenuSelection(self, event):
        str = ""
        text = WXListView.MenuTitleDict1[event.GetId()]
        if text.find("+") == -1:
            str = self.csvListView.GetSelectedObject().key
        else:
            str = "+"+self.csvListView.GetSelectedObject().key
        print str
        pyperclip.copy(str)

    #单选框按钮点击
    def HandleCheckbox(self, e):
        if e.value:
            self.xmlListView.AddObject(e.object)
        else:
            self.xmlListView.RemoveObject(e.object)

    def addBottomViews(self):
        self.gbSizer.Add(wx.StaticLine(self.panel), span=(1, 10), pos=(9, 0), flag=wx.EXPAND | wx.BOTTOM, border=10)
        #切割数据
        self.gbSizer.Add(wx.StaticText(self.panel, label=u"输入CSV_Key(截取对应XML_Value的\\后的内容作为值,不输入默认不截取)", style=wx.LEFT | wx.BOTTOM), span=(2, 2),
                         pos=(10, 4), flag=wx.LEFT, border=10)
        self.valueSplitView = wx.TextCtrl(self.panel, -1, value='')
        self.gbSizer.Add(self.valueSplitView, span=(2, 3), pos=(10, 6),
                         flag=wx.LEFT | wx.EXPAND)


        #命名规则
        self.gbSizer.Add(wx.StaticText(self.panel, label=u"输入XML文件命名规则",style=wx.LEFT|wx.BOTTOM), span=(2, 1), pos=(12, 4), flag=wx.LEFT, border=10)
        self.xmlNameView = wx.TextCtrl(self.panel, -1, value='')
        self.gbSizer.Add(self.xmlNameView, span=(2, 4), pos=(12, 5),
                          flag=wx.LEFT|wx.EXPAND)

        #保存目录
        button1 = wx.Button(self.panel, -1, u"选择保存目录(尽量英文目录)")
        self.Bind(wx.EVT_BUTTON, self.OnClickFilePath, button1)
        button1.SetDefault()
        self.gbSizer.Add(button1, span=(2, 1),
                         pos=(14, 4), flag=wx.LEFT, border=10)
        self.filePathView = wx.TextCtrl(self.panel, -1, value='')
        self.filePathView.Enable(False)
        self.gbSizer.Add(self.filePathView, span=(2, 4), pos=(14, 5),
                         flag=wx.LEFT | wx.EXPAND)

        # 保存按钮
        button2 = wx.Button(self.panel, -1, u"保存当前XML文件")
        self.Bind(wx.EVT_BUTTON, self.OnClickSaveFile, button2)
        button2.SetDefault()
        self.gbSizer.Add(button2, span=(2, 5),
                         pos=(16, 4), flag=wx.LEFT | wx.EXPAND, border=10)

        sb = wx.StaticBox(self.panel, label= u"提示")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        text = wx.StaticText(self.panel, label=u"1.左边右击“复制+key”,默认添加+号\n2.可修改xml的XML_Key名\n3.右侧xml的内容：(填入CSV_Key,可用+累加)\n4.命名：*表示原文件名,#表示数字(以1开始)\n5.命名：可最多添加{CSV_Key}获取的值作为文件名的一部分\n6.截取：截取框输入CSV_Key,内容的\\后的内容作为值")
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        text.SetFont(font)
        boxsizer.Add(text,
                       flag=wx.EXPAND, border=5)
        self.gbSizer.Add(boxsizer, pos=(10, 0), span=(8, 4),
                          flag=wx.TOP | wx.LEFT | wx.RIGHT| wx.EXPAND, border=10)

    def OnClickFilePath(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetPath()  # 文件夹路径
            self.filePathView.SetLabelText(dlg.GetPath())
        dlg.Destroy()

    def OnClickSaveFile(self, event):
        #print os.path.dirname(self.csvFilesPathList[0])
        #命名规则：
        str = self.xmlNameView.GetValue()


        datas = self.xmlListView.GetObjects()
        if len(datas) == 0:
            self.ShowMessage(u"没有xml内容")
        elif len(self.filePathView.GetLabelText()) == 0:
            self.ShowMessage(u"请先选择文件保存目录")
        else:
            dirPath = self.filePathView.GetLabelText()
            suc, rep = self.fd.end(str,dirPath,self.valueSplitView.GetValue(),self.xmlListView.GetObjects(),self.csvFilesPathList)
            if suc:
                dlg = wx.MessageDialog(None, u"是否查看xml文件", u"提示", wx.YES_NO | wx.ICON_QUESTION)
                if dlg.ShowModal() == wx.ID_YES:
                    dd = "start explorer {0}".format(self.filePathView.GetLabelText())
                    os.system(dd.encode('utf-8'))
                dlg.Destroy()
            else:
                self.ShowMessage(rep)

            # dirPath = self.filePathView.GetLabelText()
            # xmlFilesPathList = []
            # #文件命名
            # for i in range(len(self.csvFilesPathList)):
            #     TotalFileName = os.path.basename(self.csvFilesPathList[i])
            #     fileName = os.path.splitext(TotalFileName)[0]
            #     tempStr = str.replace('*',fileName)
            #     tempStr = tempStr.replace('#',"{0}".format(i+1))
            #     xmlFilesPathList.append((dirPath+"\\"+tempStr+".xml"))
            # print xmlFilesPathList
            # suc, rep = self.fd.ListToXML(xmlFilesPathList,datas,self.csvFilesPathList)
            # if suc:
            #     dlg = wx.MessageDialog(None, u"是否查看xml文件", u"提示",  wx.YES_NO | wx.ICON_QUESTION)
            #     if dlg.ShowModal() == wx.ID_YES:
            #         dd = "start explorer {0}".format(self.filePathView.GetLabelText())
            #         os.system(dd.encode('utf-8'))
            #     dlg.Destroy()
            # else:
            #     self.ShowMessage(rep)









    #原始文件转化为可读文件
    def getMiddenDatas(self, lists):
        for i in range(len(lists[0])):
            self.middenDatas.append(ListData(lists[0][i], lists[1][i]))

    #消息提醒
    def ShowMessage(self, message):
        wx.MessageBox(message.encode("gbk"), u'提示', wx.OK | wx.ICON_INFORMATION)

    #清除所有数据
    def cleanAllData(self):
        #清除列表和中间数据
        self.csvListView.RemoveObjects(self.middenDatas)
        self.xmlListView.RemoveObjects(self.middenDatas)
        self.filename = ""
        self.middenDatas = []
        self.csvFilesPathList = []
        self.xmlNamesList = []

if __name__ == '__main__':
    app = wx.App(False)
    frame = GRMUI()
    app.MainLoop()