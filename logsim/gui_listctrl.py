import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import wx.lib.agw.ultimatelistctrl as ULC


class ListCtrl(ULC.UltimateListCtrl, ListCtrlAutoWidthMixin):
    """
    Widget representing the list of switches with toggles for each.

    UltimateListCtrl is used to allow buttons to be placed inside
    lists. ListCtrlAutoWidthMixin is used to make columns resize by
    themselves.

    Constructor parameters
    ----------------------
    `parent`: Parent window.
    `id`: Window identifier.
    `kwargs`: Additional keyword arguments.
    """

    def __init__(self, parent, id, **kwargs) -> None:
        """
        Call both parent constructors. Constructor.

        Parameters
        ----------
        `parent`: Parent window.
        `id`: Window identifier.
        `kwargs`: Additional keyword arguments.
        """
        ULC.UltimateListCtrl.__init__(self, parent, id, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        # make the first column (name) resize instead of the second
        # column (value) as this looks nicer

    def _doResize(self) -> None:
        """
        Modify resizing logic to leave space for the scrollbar.

        Returns
        -------
        `None`
        """
        ListCtrlAutoWidthMixin._doResize(self)
        # if self.GetScrolledWin().HasScrollbar(wx.VERTICAL):
        #     scrollbar_width = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        #     # wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X) gives the
        #     # vertical scrollbar width
        #     self.SetColumnWidth(
        #         self._resizeCol,
        #         self.GetColumnWidth(self._resizeCol) - scrollbar_width
        #     )
