#coding:utf-8
import csv
import codecs
import xml.dom.minidom
import os
import sys
default_encoding="utf-8"
if(default_encoding!=sys.getdefaultencoding()):
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class FILEDEAL:

    def CSVToListFun(self, filePath):
        '''
        文件转dict 
        '''
        lists = []
        with open(filePath, 'r') as f:
            try:
                reader = csv.reader(( (line.replace('\0','') for line in f) ) )
            except:
                return (False,"读取文件({0})错误".format(filePath))

            for i, row in enumerate(reader):
                print row
                if i<=1:
                    lists.append(row)

            if len(lists) != 2 or len(lists[0]) == 0 or len(lists[0]) != len(lists[1]):
                return (False, "文件({0})信息数量错误".format(filePath))
            lists[0][0] = lists[0][0].replace(codecs.BOM_LE, "")
            return (True, lists)


    def csvToChangedDatasList(self,orgFilesPath):
        ChangedDatasList = []
        for i in range(len(orgFilesPath)):
            orgFilePath = orgFilesPath[i]
            fileName = os.path.splitext(os.path.basename(orgFilePath))[0]
            tempKeyList = []
            tempValuesList = []
            #with open(orgFilePath, 'r') as f:
            with  codecs.open(orgFilePath, 'rb',encoding='utf-16') as f:
                # for line in f:
                #     print line#.replace('\0', '').replace(codecs.BOM_LE, "").decode('gbk','ignore').encode('gbk')
                try:
                    reader = csv.reader(((line.replace('\0', '') for line in f)))#.replace(codecs.BOM_LE, "").decode("utf-8")
                    print reader
                except:
                    return (False, "读取文件({0})错误".format(orgFilePath))
                for i, row in enumerate(reader):
                    if len(row)>0:
                        if i == 0:
                            tempKeyList = row
                            tempKeyList[0] = tempKeyList[0].replace(codecs.BOM_LE, "")
                        else:
                            tempValuesList.append(row)
                            print row
            for j in range(len(tempValuesList)):
                dic = dict(zip(tempKeyList, tempValuesList[j]))
                dic["MMZZEERROO"] = fileName+ (str(j) if j>0 else "")
                ChangedDatasList.append(dic)
        return (True, ChangedDatasList)

    def end(self, nameGZ, saveDir, valueSplit, middenDatas, orgFilesPath):
        suc, dicList = self.csvToChangedDatasList(orgFilesPath)
        if not suc:
            return (suc, dicList)
        else:
            # 检查命名规则：
            if len(nameGZ) == 0:
                return (False, u"请设置xml文件命名规则保存")
            if len(dicList) > 1 and nameGZ.find("#") == -1 and nameGZ.find("*") == -1 and (nameGZ.find("{") == -1 or nameGZ.find("}") == -1):
                return (False, u"文件数量与xml文件命名规则不匹配")

            for i in range(len(dicList)):
                dic = dicList[i]

                # 替换内容的\
                if len(valueSplit) > 0 and dic.has_key(valueSplit):
                    str = dic[valueSplit]
                    tempList = str.split("\\")
                    if len(tempList) > 0:
                        dic[valueSplit] = tempList[len(tempList) - 1]

                # 修改文件名
                dic["MMZZEERROO"] = self.changeName(nameGZ, dic, i)

                # 多个内容+++
                for j in range(len(middenDatas)):
                    middenData = middenDatas[j]
                    valueStr = ""
                    keyMapList = middenData.keyMap.split("+")
                    for k in range(len(keyMapList)):
                        if dic.has_key(keyMapList[k]):
                            valueStr += dic[keyMapList[k]]
                    dic[middenData.key] = valueStr



                # 去除多余的
                for (x, v) in dic.items():
                    if x == "MMZZEERROO":
                        continue
                    tempBool = False
                    for y in range(len(middenDatas)):
                        ddd = middenDatas[y]
                        if ddd.key == x:
                            tempBool = True
                    if not tempBool:
                        del dic[x]


                #修改key
                for m in range(len(middenDatas)):
                    tempData = middenDatas[m]
                    if tempData.key != tempData.keyCopy and dic.has_key(tempData.key):
                        dic[tempData.keyCopy] = dic[tempData.key]
                        del dic[tempData.key]

                #xml
                doc = xml.dom.minidom.Document()
                root = doc.createElement("DOCCONTENT")
                root.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
                doc.appendChild(root)
                for (k,v)in dic.items():
                    if k == "MMZZEERROO":
                        continue
                    nodeName = doc.createElement(k)
                    print v
                    nodeName.appendChild(doc.createTextNode(v))
                    root.appendChild(nodeName)
                path = saveDir+"\\"+dic["MMZZEERROO"]+".xml"
                with open(path, 'w') as fp:
                    try:
                        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
                    except:
                        return (False, "写入文件({0})错误".format(path))
            return (True, "ok")

    def changeName(self,orgName,dic, i):
        newName = orgName;
        for (k,v) in dic.items():
            if k == "MMZZEERROO":
                continue
            str = "{"+k+"}"
            newName = newName.replace(str,v)

        MMZZEERROO = dic["MMZZEERROO"]
        newName = newName.replace('*', MMZZEERROO)
        newName = newName.replace('#', "{0}".format(i + 1))
        return newName



    # 原始文件转化为可读文件
    def getMiddenDatas(self, lists):
        temp = []
        for i in range(len(lists[0])):
            temp.append(ListData(lists[0][i], lists[1][i]))
        return temp

    # 把源文件（多个）转化为
    def change(self, orgFilesPath):
        pass

    def ListToXML(self, paths, middleDatas, csvFilesPathList):
        csvLists = []
        for m in range(len(csvFilesPathList)):
            suc, rep = self.CSVToListFun(csvFilesPathList[m])
            if not suc:
                return (suc, rep)
            else:
                csvLists.append(self.getMiddenDatas(rep))

        for n in range(len(paths)):
            path = paths[n]

            doc = xml.dom.minidom.Document()
            root = doc.createElement("DOCCONTENT")
            root.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
            doc.appendChild(root)

            for i in range(len(middleDatas)):
                data = middleDatas[i]
                nodeName = doc.createElement(data.keyCopy)
                valueStr = ""
                keyMapList = data.keyMap.split("+")
                for j in range(len(keyMapList)):
                    tempStr = keyMapList[j]
                    for k in range(len(csvLists[n])):
                        if tempStr == csvLists[n][k].key:
                            valueStr += csvLists[n][k].value
                nodeName.appendChild(doc.createTextNode(valueStr))
                root.appendChild(nodeName)
            with open(path, 'w') as fp:
                try:
                    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
                except:
                    return (False, "写入文件({0})错误".format(path))
        return (True, "ok")


class ListData(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.keyCopy = key
        self.keyMap = key

class ChangedData(object):
    def __init__(self, key, value, fileName):
        self.key = key
        self.value = value
        self.fileName = fileName

    # def ListToXML1(self,paths, middleDatas):
    #     for m in range(len(paths)):
    #         path = paths[m]
    #
    #         doc = xml.dom.minidom.Document()
    #         root = doc.createElement("DOCCONTENT")
    #         root.setAttribute('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    #         doc.appendChild(root)
    #     #print middleDatas
    #     for i in range(len(middleDatas)):
    #         data = middleDatas[i]
    #         nodeName = doc.createElement(data.keyCopy)
    #         valueStr = ""
    #         keyMapList = data.keyMap.split("+")
    #         for j in range(len(keyMapList)):
    #             tempStr = keyMapList[j]
    #             for k in range(len(middleDatas)):
    #                 if tempStr == middleDatas[k].key:
    #                     valueStr += middleDatas[k].value
    #         nodeName.appendChild(doc.createTextNode(valueStr))
    #         root.appendChild(nodeName)
    #     fp = open(path, 'w')
    #     doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
    #     print "ok"


    # def TxtToListFun(self, filePath):
    #     '''
    #     文件转dict
    #     '''
    #     if filePath:
    #         file_object = codecs.open(filePath, "r")
    #         try:
    #             text = file_object.read()
    #             print text
    #             file_object.close()
    #         except:
    #             return (False,"读取文件({0})错误".format(filePath))
    #         print self.strToDictFun(text)
    #         return (False, "文件路径为空")
    #
    #     else:
    #         return (False, "文件路径为空")
    #
    # def strToDictFun(self, str):
    #     print("%s",str)
    #     # if str[0] == ';':
    #     #     str = str[1:]
    #     # if str[len(str)-1] == ';':
    #     #     str = str[:len(str)-1]
    #     list = str.split(';')
    #     for i in range(len(list)):
    #         print list[i].decode('utf-8','ignore')
    #     return 43

class CnEncoding():
    '''The encoding converter'''

    def __init__(self, st, encoding=''):
        '''
        Initial the converter. 'st' could be an str or unicode object.
        'encoding' refers the original encoding.
        If do not know anything about the encoding,
        use the default value or leave it blank.
        '''
        if isinstance(st, unicode):
            self._encoding = 'utf-8'
            self._st = st.decode('utf-8')
        elif isinstance(st, str):
            if encoding == '':
                self._encoding = guess_coding(st)
            else:
                self._encoding = encoding
            self._st = st
            print self._st
        else:
            raise ValueError('%s is not a str nor unicode object.' % st)

    def __str__(self):
        return self._st

    def __unicode__(self):
        return self._st.decode(self._encoding)

    def to_encode(self, encoding='utf-8'):
        '''
        return an printable str object in specific encoding.
        '''
        return self._st.decode(self._encoding).encode(encoding)

def guess_coding(st):
    '''Guess the codepage by try-except'''
    fits_coding = ['utf-8', 'gbk', 'gb18030']
    if not isinstance(st, str):
        raise ValueError('%s is not a str object.' % st)
    for code in fits_coding:
        try:
            st.decode(code)
            return code
        except UnicodeDecodeError:
            pass
    return 'unknow'