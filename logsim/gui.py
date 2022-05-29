"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
import wx
import wx.lib.agw.aui as aui

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from gui_tabs import ConsoleOutTab, CircuitDefTab, ComponentsTab, DevicesTab
from gui_canvas import MyGLCanvas # not used yet. needed for outputting the signals!

class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(1000, 800))

        # Configure the file menu
        self.create_menu()

        # Set up the tool bar
        self.create_tb()

        # add status bar at the bottom
        self.statusbar = self.CreateStatusBar(1)

        # create an AuiManager object
        self.mgr = aui.AuiManager()
        
        # notify AUI which frame to use
        self.mgr.SetManagedWindow(self)

        # main monitor part
        self.canvas = MyGLCanvas(self, devices, monitors, self.statusbar)
        self.mgr.AddPane(self.canvas, aui.AuiPaneInfo().CenterPane().Caption("pane center"))

        # bottom panel 
        notebook = aui.AuiNotebook(self, wx.ID_ANY, agwStyle=aui.AUI_NB_CLOSE_ON_ALL_TABS )

        consoleOutPanel = ConsoleOutTab(notebook)
        circuitDefPanel = CircuitDefTab(notebook, path)
        componentsPanel = ComponentsTab(notebook)
        devicesPanel = DevicesTab(notebook)

        notebook.AddPage(consoleOutPanel, "Output", True)
        notebook.AddPage(circuitDefPanel, "Circuit Definition", False)
        notebook.AddPage(componentsPanel, "Components", False)
        notebook.AddPage(devicesPanel, "Devices", False)

        # disable close buttons
        notebook.SetCloseButton(0, False)
        notebook.SetCloseButton(1, False)
        notebook.SetCloseButton(2, False)
        notebook.SetCloseButton(3, False)

        self.mgr.AddPane(notebook,
                          aui.AuiPaneInfo().CaptionVisible(True).
                          Bottom().PaneBorder(False).Floatable(False).GripperTop(True).MinSize(330,150).CloseButton(False))

        # setting docking guides fixes docking issue (problem with wxTimer)
        agwFlags = self.mgr.GetAGWFlags()
        self.mgr.SetAGWFlags(agwFlags
                               | aui.AUI_MGR_AERO_DOCKING_GUIDES
                            #    | aui.AUI_MGR_WHIDBEY_DOCKING_GUIDES
        )

        self.mgr.Update() 

        self.Bind(wx.EVT_CLOSE, self.on_close) 
        self.Centre() 
        self.Show(True)

################################
        # # Canvas for drawing signals
        # self.canvas = MyGLCanvas(self, devices, monitors)

        # # Configure the widgets
        # self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        # self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        # self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        # self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
        #                             style=wx.TE_PROCESS_ENTER)

        # # Bind events to widgets
        # self.Bind(wx.EVT_MENU, self.on_menu)
        # self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        # self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        # self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # # Configure sizers for layout
        # main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # side_sizer = wx.BoxSizer(wx.VERTICAL)

        # main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        # main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        # side_sizer.Add(self.text, 1, wx.TOP, 10)
        # side_sizer.Add(self.spin, 1, wx.ALL, 5)
        # side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        # side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        # self.SetSizeHints(600, 600)
        # self.SetSizer(main_sizer)
################################

    def create_menu(self): 
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")

        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.on_menu)
    
    def create_tb(self): 
        tb = wx.ToolBar(self,- 1)
        self.ToolBar = tb
        tb.AddTool( 1, 'Run', wx.Image("./logsim/imgs/run.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Run the simulation") 
        tb.AddTool( 2, 'Stop', wx.Image("./logsim/imgs/stop.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Stop the simulation") 
        tb.AddStretchableSpace()
        self.text = wx.StaticText(tb, wx.ID_ANY, "Cycles")
        tb.AddControl(self.text)
        self.spin = wx.SpinCtrl(tb, wx.ID_ANY, "10")
        tb.AddControl(self.spin)

        # tb.Bind(wx.EVT_TOOL, lambda evt:self.on_run_button(), id=1)
        
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        # tb.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR))
        tb.Realize()

    def update_statusbar(self, text): 
        self.statusbar.SetStatusText(text)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Yi Chen Hock, Michael Stevens and Cindy Wu\n2022",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)
        self.update_statusbar(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

    # def on_text_box(self, event):
    #     """Handle the event when the user enters text."""
    #     text_box_value = self.text_box.GetValue()
    #     text = "".join(["New text box value: ", text_box_value])
    #     self.canvas.render(text)

    def on_close(self, event):
        # deinitialize the frame manager
        self.mgr.UnInit()
        self.Destroy()