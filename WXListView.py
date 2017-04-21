#coding:utf-8
import  wx.lib.newevent
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

OvlCheckEvent, EVT_OVL_CHECK_EVENT = wx.lib.newevent.NewEvent()

class ListCtrlView(ObjectListView):

    def SetCheckState(self, modelObject, state):
        """
        This is the same code, just added the event inside
        """
        if self.checkStateColumn is None:
            return None
        else:
            r = self.checkStateColumn.SetCheckState(modelObject, state)

            # Just added the event here ===================================
            e = OvlCheckEvent(object=modelObject, value=state)
            wx.PostEvent(self, e)
            # =============================================================

            return r

    def _HandleLeftDownOnImage(self, rowIndex, subItemIndex):
        """
        This is the same code, just added the event inside
        """
        column = self.columns[subItemIndex]
        if not column.HasCheckState():
            return

        self._PossibleFinishCellEdit()
        modelObject = self.GetObjectAt(rowIndex)
        if modelObject is not None:
            column.SetCheckState(modelObject, not column.GetCheckState(modelObject))

            # Just added the event here ===================================
            e = OvlCheckEvent(object=modelObject, value=column.GetCheckState(modelObject))
            wx.PostEvent(self, e)
            # =============================================================

            self.RefreshIndex(rowIndex, modelObject)


#获取右击菜单内容
menuList1 = [u"复制 key",u"复制 +key"]

MenuTitleDict1 = {}
for title in menuList1:
    MenuTitleDict1[wx.wx.NewId()] = title
