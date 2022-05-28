

"""
AuiNotebook ( AGW ) ( last edited 2009-12-14 18 :36 :49 by MikeDriscoll ) ( AGW ) @ 
http ://wiki.wxpython.org/AuiNotebook%20%28AGW%29

This [second] example shows you how to change a few notebook settings.
( And yes, it's a doozy ! )

[ Note : All menu items are nonfunctional. ]

"""
import wx
import wx.lib.agw.aui as aui

#------------------------------------------------------------------------------

class TabPanel( wx.Panel ) :
    """ A simple wx.Panel class. """
    
    def __init__( self, parent ) :
        """  """
        wx.Panel.__init__( self, parent=parent )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        txtOne = wx.TextCtrl( self, wx.ID_ANY, "" )
        txtTwo = wx.TextCtrl( self, wx.ID_ANY, "" )
        
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( txtOne, 0, wx.ALL, 5 )
        sizer.Add( txtTwo, 0, wx.ALL, 5 )
        
        self.SetSizer( sizer )
        
 #end class

#------------------------------------------------------------------------------

class AUIManager( aui.AuiManager ) :
    """ AUI Manager class """

    def __init__( self, managed_window ) :
        """  """
        
        aui.AuiManager.__init__( self )
        self.SetManagedWindow( managed_window )
        
#end class

#------------------------------------------------------------------------------

class AUINotebook( aui.AuiNotebook ) :
    """ AUI Notebook class """

    def __init__( self, parent ) :
        """  """
        
        aui.AuiNotebook.__init__( self, parent=parent )
        
        self.default_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self.SetWindowStyleFlag( self.default_style )
        
        #----

        # add some pages to the notebook
        pages = [TabPanel, TabPanel, TabPanel]

        pageCtr = 1
        for page in pages :
            label = "Tab #%i" % pageCtr
            tab = page( self )
            self.AddPage( tab, label, False )
            pageCtr += 1
        #end for
        
    #end __init__
    
#end AUINotebook class

#------------------------------------------------------------------------------

class DemoFrame( wx.Frame ) :
    """ The demo app Frame. """
    
    ID_NotebookArtGloss     = wx.NewId()
    ID_NotebookArtSimple    = wx.NewId()
    ID_NotebookArtVC71      = wx.NewId()
    ID_NotebookArtFF2       = wx.NewId()
    ID_NotebookArtVC8       = wx.NewId()
    ID_NotebookArtChrome    = wx.NewId()
    
    #----------------------------------
    
    def __init__( self ) :
        """Constructor"""
        
        title = "AGW AUI Notebook Feature Tutorial"
        wx.Frame.__init__( self, None, wx.ID_ANY,
                          title=title, size=( 600, 400 ) )
        #-----
        
        self.themeDict = { "Glossy Theme (Default)" : 0,
                           "Simple Theme"           : 1,
                           "VC71 Theme"             : 2,
                           "Firefox 2 Theme"        : 3,
                           "VC8 Theme"              : 4,
                           "Chrome Theme"           : 5,
                          }

        # create the AUI manager
        self.aui_mgr = AUIManager( self )

        # create the AUI Notebook
        self.notebook = AUINotebook( self )

        self._notebook_style = self.notebook.default_style

        # add notebook to AUI manager
        self.aui_mgr.AddPane( self.notebook,
                             aui.AuiPaneInfo().Name( "notebook_content" ).
                             CenterPane().PaneBorder( False ) )
        self.aui_mgr.Update()

        # create menu and tool bars
        self.CreateMenu()
        self.CreateTB()
        
    #end __init__

    #----------------------------------
    
    def CreateMenu( self ) :
        """
        Create the menu
        """
        def doBind( item, handler ) :
            """ Create menu events. """
            self.Bind( wx.EVT_MENU, handler, item )

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()

        doBind( fileMenu.Append( wx.ID_ANY, "&Exit\tAlt+F4",
                                 "Exit Program" ), self.OnExit )

        optionsMenu = wx.Menu()

        doBind( optionsMenu.Append( wx.ID_ANY,
                                   "Disable Current Tab" ),
                self.OnDisableTab )

        # add the menus to the menubar
        menubar.Append( fileMenu, "File" )
        menubar.Append( optionsMenu, "Options" )

        self.SetMenuBar( menubar )
    
    #end CreateMenu def
    
    #----------------------------------
    
    def CreateTB( self ) :
        """
        Create the toolbar
        """
        TBFLAGS = ( wx.TB_HORIZONTAL |
                    wx.NO_BORDER     |
                    wx.TB_FLAT )
                    
        tb = self.CreateToolBar( TBFLAGS )
        keys = self.themeDict.keys()
        keys.sort()
        choices = keys
        cb = wx.ComboBox( tb, wx.ID_ANY, "Glossy Theme ( Default )",
                          choices=choices,
                          size=wx.DefaultSize,
                          style=wx.CB_DROPDOWN )
                          
        cb.Bind( wx.EVT_COMBOBOX, self.OnChangeTheme )
        tb.AddControl( cb )
        tb.AddSeparator()

        self.closeChoices = [ "No Close Button", "Close Button At Right",
                              "Close Button On All Tabs",
                              "Close Button On Active Tab" ]
                              
        cb = wx.ComboBox( tb, wx.ID_ANY,
                          self.closeChoices[3],
                          choices=self.closeChoices,
                          size=wx.DefaultSize,
                          style=wx.CB_DROPDOWN )
                          
        cb.Bind( wx.EVT_COMBOBOX, self.OnChangeTabClose )
        tb.AddControl( cb )

        tb.Realize()

    #end CreateTB def
    
    #----------------------------------
    
    def OnChangeTabClose( self, event ) :
        """
        Change how the close button behaves on a tab
 
        Note : Based partially on the agw AUI demo
        """
        choice = event.GetString()
        self._notebook_style &= ~( aui.AUI_NB_CLOSE_BUTTON |
                                   aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                   aui.AUI_NB_CLOSE_ON_ALL_TABS )

        # note that this close button doesn't work for some reason
        if choice == "Close Button At Right" :
            self._notebook_style ^= aui.AUI_NB_CLOSE_BUTTON
            
        elif choice == "Close Button On All Tabs" :
            self._notebook_style ^= aui.AUI_NB_CLOSE_ON_ALL_TABS
            
        elif choice == "Close Button On Active Tab" :
            self._notebook_style ^= aui.AUI_NB_CLOSE_ON_ACTIVE_TAB

        self.notebook.SetWindowStyleFlag( self._notebook_style )
        self.notebook.Refresh()
        self.notebook.Update()
    
    #end OnChangeTabClose def
    
    #----------------------------------
    
    def OnChangeTheme( self, event ) :
        """
        Changes the notebook's theme
 
        Note : Based partially on the agw AUI demo
        """

        # print event.GetString()
        evId = self.themeDict[event.GetString()]
        # print evId

        all_panes = self.aui_mgr.GetAllPanes()

        for pane in all_panes :

            if isinstance( pane.window, aui.AuiNotebook ) :
                nb = pane.window

                if evId == ID_NotebookArtGloss :

                    nb.SetArtProvider( aui.AuiDefaultTabArt() )
                    self._notebook_theme = 0

                elif evId == ID_NotebookArtSimple :
                    nb.SetArtProvider( aui.AuiSimpleTabArt() )
                    self._notebook_theme = 1

                elif evId == ID_NotebookArtVC71 :
                    nb.SetArtProvider( aui.VC71TabArt() )
                    self._notebook_theme = 2

                elif evId == ID_NotebookArtFF2 :
                    nb.SetArtProvider( aui.FF2TabArt() )
                    self._notebook_theme = 3

                elif evId == ID_NotebookArtVC8 :
                    nb.SetArtProvider( aui.VC8TabArt() )
                    self._notebook_theme = 4

                elif evId == ID_NotebookArtChrome :
                    nb.SetArtProvider( aui.ChromeTabArt() )
                    self._notebook_theme = 5

                #nb.SetWindowStyleFlag( self._notebook_style )
                nb.Refresh()
                nb.Update()
                
            #end if
            
        # end for
        
    #end OnChangeTheme def
    
    #----------------------------------
    
    def OnDisableTab( self, event ) :
        """ Disables the current tab. """
        
        page = self.notebook.GetCurrentPage()
        page_idx = self.notebook.GetPageIndex( page )

        self.notebook.EnableTab( page_idx, False )
        self.notebook.AdvanceSelection()

    #----------------------------------
    
    def OnExit( self, event ) :
        """ Close the demo. """
        
        self.Close()

#end DemoFrame class

#==============================================================================

if __name__ == "__main__" :
    
    app = wx.PySimpleApp()
    frame = DemoFrame().Show()
    app.MainLoop()

#end if