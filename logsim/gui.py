"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""
from ast import Pass
import wx
import wx.lib.agw.aui as aui

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from gui_tabs import ConsoleOutTab, CircuitDefTab, InputsTab, MonitorsTab
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
        super().__init__(parent=None, title=title, size=(1024, 768))

        self.path = path

        # Create the menu, toolbar and statusbar
        self.create_menu()
        self.create_tb()
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([-3,-1])
        self.statusbar.SetStatusText(self.path,1)

        # create an AuiManager object
        self.mgr = aui.AuiManager()
        
        # notify AUI which frame to use
        self.mgr.SetManagedWindow(self)

        # main monitor part
        self.canvas = MyGLCanvas(self, devices, monitors, self.statusbar)

        self.mgr.AddPane(self.canvas, aui.AuiPaneInfo().CenterPane())

        # bottom panel 
        notebook = aui.AuiNotebook(self, wx.ID_ANY, agwStyle=aui.AUI_NB_CLOSE_ON_ALL_TABS )

        consoleOutPanel = ConsoleOutTab(notebook)
        circuitDefPanel = CircuitDefTab(notebook, self.path, self.statusbar)
        componentsPanel = InputsTab(notebook)
        devicesPanel = MonitorsTab(notebook, self.statusbar)

        notebook.AddPage(consoleOutPanel, "Output", True)
        notebook.AddPage(circuitDefPanel, "Circuit Definition", False)
        notebook.AddPage(componentsPanel, "Inputs", False)
        notebook.AddPage(devicesPanel, "Monitors", False)

        # disable close buttons
        notebook.SetCloseButton(0, False)
        notebook.SetCloseButton(1, False)
        notebook.SetCloseButton(2, False)
        notebook.SetCloseButton(3, False)

        self.mgr.AddPane(notebook,
                          aui.AuiPaneInfo().CaptionVisible(False).
                          Right().PaneBorder(False).Floatable(False).GripperTop(False).MinSize(330,150).CloseButton(False))

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
        
        self.SetSizeHints(minW=600, minH=400)

        print("Logic Simulator: interactive graphical user interface.\n"
              "Enter 'h' for help.")

    def create_menu(self): 
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        
        # viewMenu = wx.Menu()
        # viewMenu.Append(wx.ID_)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")

        self.SetMenuBar(menuBar)
        
        self.Bind(wx.EVT_MENU, self.on_menu)
    
    def create_tb(self): 
        tb = wx.ToolBar(self,- 1, style=wx.TB_TEXT)
        self.ToolBar = tb

        tb.AddTool( 1, 'Browse', wx.Image("./logsim/imgs/browse.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Browse for a file") 
        tb.AddTool( 2, 'Save', wx.Image("./logsim/imgs/save.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Save the file") 
        tb.AddTool( 3, 'New', wx.Image("./logsim/imgs/new file.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Create a new file") 
        tb.AddStretchableSpace()
        tb.AddTool( 4, 'Run', wx.Image("./logsim/imgs/run.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Run the simulation") 
        tb.AddTool( 5, 'Continue', wx.Image("./logsim/imgs/continue.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Continue the simulation") 
        tb.AddTool( 6, 'Reset', wx.Image("./logsim/imgs/reset.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Reset the simulation") 
        
        self.spin = wx.SpinCtrl(tb, wx.ID_ANY, "10")
        # Configure spin
        self.spin.SetMin(1)
        self.spin.SetMax(1000)
        tb.AddControl(self.spin, 'Cycles')

        tb.AddStretchableSpace()
        tb.AddTool( 7, 'Save Plot', wx.Image("./logsim/imgs/save image.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Save signal trace as an image") 
        tb.AddTool( 8, 'Help', wx.Image("./logsim/imgs/help.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Help") 
        tb.AddTool( 9, 'Quit', wx.Image("./logsim/imgs/quit.png",
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap(), shortHelp="Quit Logic Simulator") 

        tb.Realize()

        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=1)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=2)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=3)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=4)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=5)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=6)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=7)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=8)
        self.Bind(wx.EVT_TOOL, self.on_tool_click, id=9)

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

    def on_tool_click(self, event):
        # print("tool %s clicked" % event.GetId())

        if event.GetId() == 1: # browse
            self.open_file()

        elif event.GetId() == 2: # save
            self.save_file()

        elif event.GetId() == 3: # new file
            self.create_file()

        elif event.GetId() == 4: # run
            print("Simulation ran for {} cycles.".format(self.spin.GetValue()))
            self.update_statusbar("Run button pressed.")

        elif event.GetId() == 5: # continue
            print("Simulation continued for {} cycles.".format(self.spin.GetValue()))
            self.update_statusbar("Continue button pressed.")

        elif event.GetId() == 6: # reset 
            print("Simulation reset.")
            self.update_statusbar("Reset button pressed.")

        elif event.GetId() == 7: # save plot
            self.save_plot()

        elif event.GetId() == 8: # help
            print("User commands:")
            print("r N       - run the simulation for N cycles")
            print("c N       - continue the simulation for N cycles")
            print("s X N     - set switch X to N (0 or 1)")
            print("m X       - set a monitor on signal X")
            print("z X       - zap the monitor on signal X")
            print("h         - help (this command)")
            print("q         - quit the program")
            self.update_statusbar("List of commands displayed in 'Output'.")

        elif event.GetId() == 9: # quit
            self.Close(True)

    def on_close(self, event):
        # deinitialize the frame manager
        self.mgr.UnInit()
        self.Destroy()
    
    def open_file(self): 
        
        """
        Launch a dialog for the user to select and open a file.

        Returns
        -------
        `None`
        """
        with wx.FileDialog(self, "Open File",
                           wildcard="Text documents (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as \
                file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()
            self.load_file(pathname)

    def load_file(self): 
        pass

    def create_file(self): 
        """
        Launch a dialog for the user to select and create a new file in that directory.

        Returns
        -------
        `None`
        """
        with wx.FileDialog(self, "Save File",
                           defaultFile="image.png",
                           wildcard="Text documents (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed saving the file chosen by the user
            pathname = file_dialog.GetPath()
            # CREATE A NEW FILE HERE AND SET THAT AS THE NEW PATH!

    def save_plot(self): 
        """
        Launch a dialog for the user to select and save a file.

        Returns
        -------
        `None`
        """
        with wx.FileDialog(self, "Save File",
                           defaultFile="image.png",
                           wildcard="PNG files (*.png)|*.png",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as \
                file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed saving the file chosen by the user
            pathname = file_dialog.GetPath()
            # self.canvas.save(pathname)
    
    def save_file(self): 
        pass # save whatever is in the circuit def file into the current loaded path (overwrite!)
        # get the value of whatever is in the textbox and then save :)