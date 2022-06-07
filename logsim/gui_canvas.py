"""
Draws signal trace plot.

Classes:
--------
`MyGLCanvas`: handles all canvas drawing operations.

"""
import math
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
from PIL import Image


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, global_vars):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.parent = parent
        self.devices = devices
        self.monitors = monitors

        # self.cycles_completed = 0
        self.global_vars = global_vars

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Canvas width and height
        self.width = 0
        self.height = 0

        # Width and height of plot
        self.plot_width = 0
        self.plot_height = 0

        # Horizontal starting position of plot
        self.origin_x = 0

        # signal drawing parameters
        self.initial_x = 30
        self.initial_y = 50

        # width of one clock cycle
        self.wavelength = 30

        # height of signal amplitude
        self.amplitude = 30

        self.margin_scale = 10
        self.margin_offset = 10

        # vertical spacing between different components
        self.component_vspace = 50

        # offset of component label from the bottom line
        self.component_label_offset = 15
        assert self.component_vspace >= self.amplitude

        # vertical offset of clock name label and axis numbers
        self.clock_name_offset = 12
        self.clock_axis_labels_offset = 10
        # vertical space between clock axis and first signal
        self.clock_vspace = 30

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def update_dimensions(self) -> None:
        """
        Update the canvas dimensions.

        Returns
        -------
        `None`
        """
        size = self.GetClientSize()
        self.width, self.height = size.width, size.height

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render_signals(self, set_scroll=True, flush_pan=False):
        """Render the signal trace."""
        # set left margin width
        cycle_chars = 4  # cycle name is about 4 characters wide
        if self.monitors.get_margin() is not None:
            margin = max(self.monitors.get_margin(), cycle_chars)
        else:
            margin = cycle_chars

        # set plot origin_x
        self.origin_x = self.initial_x + margin * \
            self.margin_scale + self.margin_offset

        # scale plot horizontally
        self.curr_wavelength = self.wavelength * self.zoom

        # update plot height (initial_y is used as bottom/top margin)
        self.plot_height = self.initial_y*2 + self.clock_vspace + \
            self.component_vspace*len(self.monitors.monitors_dictionary)

        # update plot width (initial_x is used as left/right margin)
        # print(self.parent.GetParent().cycles_completed)
        self.plot_width = self.origin_x + self.curr_wavelength * \
            self.global_vars.cycles_completed + self.initial_x

        # enforce pan limits
        self.enforce_pan_x_limits(self.pan_x)
        self.enforce_pan_y_limits(self.pan_y)

        if flush_pan:
            # flush pan to the right
            width_limit = max(0, self.plot_width - self.width)
            self.pan_x = -width_limit
            self.init = False

        self.SetCurrent(self.context)

        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if not self.monitors.monitors_dictionary:
            # no monitors present
            self.plot_width = 0
            self.plot_height = 0
            if set_scroll:
                self.parent.GetParent().set_scroll()  # disable scrollbar

            GL.glFlush()
            self.SwapBuffers()
            return

        self.draw_cycle_axis()
        self.draw_signal_grid()
        # self.draw_signal_grid2()
        # self.draw_signal_grid3()
        self.draw_signal_trace()

        # Set scrollbar
        if set_scroll:
            self.parent.GetParent().set_scroll()

        # We have been drawing to the back buffer, flush the graphics
        # pipeline and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_cycle_axis(self):
        """Draw the axis for the number of cycles."""
        cycles = len(list(self.monitors.monitors_dictionary.values())[0])
        x = self.initial_x
        y = self.initial_y - self.clock_name_offset
        self.render_text(_(u"Cycle"), x - self.pan_x, y - self.pan_y,
                         font=GLUT.GLUT_BITMAP_HELVETICA_12, flush=False)
        # account for pan
        x = self.origin_x
        y = self.initial_y
        GL.glColor3f(0.0, 0.0, 0.0)  # clock axis is black
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(x - self.pan_x, y - self.pan_y)
        GL.glVertex2f(x + cycles * self.curr_wavelength, y - self.pan_y)
        # account for pan
        GL.glEnd()

        # Interval for the vertical grid lines
        axis_interval = max(math.floor(1.1 / self.zoom),
                            1)  # 1.1 is a fudge factor

        # Draw vertical grid lines and labels
        x = self.origin_x  # reset x coordinate
        y = self.initial_y  # reset y coordinate
        number_devices = len(self.monitors.monitors_dictionary)
        for i in range(0, cycles + 1, axis_interval):
            # draw every grid_interval
            if x < self.origin_x - self.pan_x:
                # Don't bother drawing if grid lines to the left of
                # visible area
                x += axis_interval * self.curr_wavelength
                continue

            GL.glColor3f(0.80, 0.80, 0.80)  # grid lines are light grey
            # make it a dotted line
            y_bottom = y - self.pan_y
            y_top = y + self.component_vspace * number_devices + \
                self.clock_vspace
            
            dashed_length = 1
            dashed_spacing = 5
            while y_bottom <= y_top:
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(x, y_bottom)
                GL.glVertex2f(x, y_bottom + dashed_length)
                GL.glEnd()
                y_bottom += dashed_length + dashed_spacing
            # GL.glVertex2f(x, y - self.pan_y)  # account for pan
            # y_top = y + self.component_vspace * number_devices + \
            #     self.clock_vspace
            
            # GL.glVertex2f(x, y_top)

            # Cycle labels
            self.render_text(str(i), x,
                             y - self.clock_name_offset - self.pan_y,
                             font=GLUT.GLUT_BITMAP_HELVETICA_10, flush=False,
                             clear=False)  # account for pan
            x += axis_interval * self.curr_wavelength

    def draw_signal_grid(self):
        """Draw signal trace lines."""
        # Reset y coordinate and offset
        y = self.initial_y + self.clock_vspace

        for device_id, output_id in \
                reversed(self.monitors.monitors_dictionary):
            if y < self.initial_y + self.clock_vspace - self.pan_y:
                # Don't render signals below visible area/obscuring cycle axis
                y += self.component_vspace
                continue
            
            x = self.origin_x  # reset x coordinate
            signal_list = self.monitors.monitors_dictionary[
                (device_id, output_id)]

            GL.glColor3f(0.80, 0.80, 0.80)  # grid lines is light grey
            
            for signal in signal_list:
                if x < self.origin_x - self.pan_x - self.curr_wavelength:
                    # Don't render signals to the left of visible area
                    x += self.curr_wavelength
                    continue
                elif x < self.origin_x - self.pan_x:
                    # Partially visible, add offset to avoid waveform
                    # obscuring labels
                    offset = self.origin_x - self.pan_x - x
                else:
                    offset = 0
                
                # LOW signal grid lines for a particular device
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(x + offset, y)
                GL.glVertex2f(x + self.curr_wavelength, y)
                GL.glEnd()

                # HIGH signal grid lines for a particular device
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(x + offset, y + self.amplitude)
                GL.glVertex2f(x + self.curr_wavelength,
                                y + self.amplitude)
                GL.glEnd()

                # Vertical lines
                GL.glBegin(GL.GL_LINE_STRIP)
                GL.glVertex2f(x + offset, y)
                GL.glVertex2f(x + offset,
                                y + self.amplitude)
                GL.glEnd()

                x += self.curr_wavelength

            y += self.component_vspace

    # def draw_signal_grid2(self):
    #     """Draw signal trace lines."""
    #     # Reset y coordinate and offset
    #     y = self.initial_y + self.clock_vspace

    #     for device_id, output_id in \
    #             reversed(self.monitors.monitors_dictionary):
    #         if y < self.initial_y + self.clock_vspace - self.pan_y:
    #             # Don't render signals below visible area/obscuring cycle axis
    #             y += self.component_vspace
    #             continue
            
    #         x = self.origin_x  # reset x coordinate
    #         signal_list = self.monitors.monitors_dictionary[
    #             (device_id, output_id)]

    #         GL.glColor3f(0.80, 0.80, 0.80)  # grid lines is light grey
    #         GL.glBegin(GL.GL_LINE_STRIP)

    #         for signal in signal_list:
    #             if x < self.origin_x - self.pan_x - self.curr_wavelength:
    #                 # Don't render signals to the left of visible area
    #                 x += self.curr_wavelength
    #                 continue
    #             elif x < self.origin_x - self.pan_x:
    #                 # Partially visible, add offset to avoid waveform
    #                 # obscuring labels
    #                 offset = self.origin_x - self.pan_x - x
    #             else:
    #                 offset = 0
                
    #             # LOW signal grid lines for a particular device
    #             GL.glVertex2f(x + offset, y + self.amplitude)
    #             GL.glVertex2f(x + self.curr_wavelength,
    #                             y + self.amplitude)

    #             x += self.curr_wavelength

    #         GL.glEnd()
    #         y += self.component_vspace
        
    # def draw_signal_grid3(self):
    #     """Draw signal trace lines."""
    #     # Reset y coordinate and offset
    #     y = self.initial_y + self.clock_vspace

    #     for device_id, output_id in \
    #             reversed(self.monitors.monitors_dictionary):
    #         if y < self.initial_y + self.clock_vspace - self.pan_y:
    #             # Don't render signals below visible area/obscuring cycle axis
    #             y += self.component_vspace
    #             continue
            
    #         x = self.origin_x  # reset x coordinate
    #         signal_list = self.monitors.monitors_dictionary[
    #             (device_id, output_id)]

    #         GL.glColor3f(0.80, 0.80, 0.80)  # grid lines is light grey
    #         # GL.glBegin(GL.GL_LINE_STRIP)

    #         for signal in signal_list:
    #             if x < self.origin_x - self.pan_x - self.curr_wavelength:
    #                 # Don't render signals to the left of visible area
    #                 x += self.curr_wavelength
    #                 continue
    #             elif x < self.origin_x - self.pan_x:
    #                 # Partially visible, add offset to avoid waveform
    #                 # obscuring labels
    #                 offset = self.origin_x - self.pan_x - x
    #             else:
    #                 offset = 0
                
    #             # LOW signal grid lines for a particular device
    #             GL.glBegin(GL.GL_LINE_STRIP)
    #             GL.glVertex2f(x + offset, y)
    #             GL.glVertex2f(x,
    #                             y + self.amplitude)
    #             GL.glEnd()
                
    #             x += self.curr_wavelength

    #         # GL.glEnd()
    #         y += self.component_vspace

    def draw_signal_trace(self):
        """Draw individual signal trace."""
        # Reset y coordinate and offset
        y = self.initial_y + self.clock_vspace

        for device_id, output_id in \
                reversed(self.monitors.monitors_dictionary):
            if y < self.initial_y + self.clock_vspace - self.pan_y:
                # Don't render signals below visible area/obscuring cycle axis
                y += self.component_vspace
                continue

            monitor_name = self.devices.get_signal_name(device_id, output_id)

            x = self.initial_x
            y += self.component_label_offset
            self.render_text(monitor_name, x - self.pan_x, y,
                             font=GLUT.GLUT_BITMAP_9_BY_15, flush=False,
                             clear=False)  # account for pan

            x = self.origin_x  # reset x coordinate
            y -= self.component_label_offset  # return to low signal line
            signal_list = self.monitors.monitors_dictionary[
                (device_id, output_id)]
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)

            for signal in signal_list:
                if x < self.origin_x - self.pan_x - self.curr_wavelength:
                    # Don't render signals to the left of visible area
                    x += self.curr_wavelength
                    continue
                elif x < self.origin_x - self.pan_x:
                    # Partially visible, add offset to avoid waveform
                    # obscuring labels
                    offset = self.origin_x - self.pan_x - x
                else:
                    offset = 0

                # Signals for a particular device
                if signal == self.devices.HIGH:
                    GL.glVertex2f(x + offset, y + self.amplitude)
                    GL.glVertex2f(x + self.curr_wavelength,
                                  y + self.amplitude)
                if signal == self.devices.LOW:
                    GL.glVertex2f(x + offset, y)
                    GL.glVertex2f(x + self.curr_wavelength, y)
                if signal == self.devices.RISING:
                    GL.glVertex2f(x + offset, y)
                    GL.glVertex2f(x + self.curr_wavelength,
                                  y + self.amplitude)
                if signal == self.devices.FALLING:
                    GL.glVertex2f(x + offset, y + self.amplitude)
                    GL.glVertex2f(x + self.curr_wavelength, y)
                if signal == self.devices.BLANK:
                    pass
                x += self.curr_wavelength

            GL.glEnd()
            y += self.component_vspace

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join([_(u"Canvas redrawn on paint event, size is "),
                        str(size.width), ", ", str(size.height)])
        self.render_signals()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        # # Calculate object coordinates of the mouse position
        # size = self.GetClientSize()
        # ox = (event.GetX() - self.pan_x) / self.zoom
        # oy = (size.height - event.GetY() - self.pan_y) / self.zoom

        old_zoom = self.zoom

        scroll_delta = 25

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.ButtonUp():
            pass

        if event.Leaving():
            # set to undefined
            self.last_mouse_x = None
            self.last_mouse_y = None

        if event.Dragging():
            if self.last_mouse_x is None or self.last_mouse_y is None:
                # If last mouse position undefined, use the position at
                # the start of the drag as reference
                self.last_mouse_x = event.GetX()
                self.last_mouse_y = event.GetY()

            # Enforce pan limits
            new_pan_x = self.pan_x + (event.GetX() - self.last_mouse_x)
            new_pan_y = self.pan_y - (event.GetY() - self.last_mouse_y)
            self.enforce_pan_x_limits(new_pan_x)
            self.enforce_pan_y_limits(new_pan_y)

            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        # Vertical scroll (normal scroll)
        if event.GetModifiers() == wx.MOD_NONE and \
                event.GetWheelRotation() != 0:
            sign = 1 if event.GetWheelRotation() > 0 else -1
            # Enforce pan limits
            new_pan_y = self.pan_y - sign * scroll_delta
            self.enforce_pan_y_limits(new_pan_y)
            self.init = False

        # Horizontal scroll (shift + scroll)
        if event.GetModifiers() == wx.MOD_SHIFT and \
                event.GetWheelRotation() != 0:
            sign = 1 if event.GetWheelRotation() < 0 else -1
            # Enforce pan limits
            new_pan_x = self.pan_x - sign * scroll_delta
            self.enforce_pan_x_limits(new_pan_x)
            self.init = False

        # Horizontal zoom in (ctrl + scroll)
        if event.GetModifiers() == wx.MOD_CONTROL and \
                event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (event.GetWheelRotation() / (
                          20 * event.GetWheelDelta())))
            self.adjust_pan_x(event, old_zoom)
            self.init = False

        # Horizontal zoom out (ctrl + scroll)
        if event.GetModifiers() == wx.MOD_CONTROL and \
                event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.adjust_pan_x(event, old_zoom)
            self.init = False

        self.Refresh()

    def enforce_pan_y_limits(self, new_pan_y):
        """Limit y pan."""
        height_limit = max(0, self.plot_height - self.height)
        self.pan_y = max(min(new_pan_y, 0), - height_limit)

    def enforce_pan_x_limits(self, new_pan_x):
        """Limit x pan."""
        width_limit = max(0, self.plot_width - self.width)
        self.pan_x = max(min(new_pan_x, 0), - width_limit)

    def adjust_pan_x(self, event, old_zoom):
        """Adjust x pan."""
        offset = event.GetX() - self.pan_x - self.origin_x
        if offset > 0:
            # The mouse is within the grid
            pos = offset / old_zoom
            new_x = pos * self.zoom + self.origin_x
            new_pan_x = event.GetX() - new_x
            self.enforce_pan_x_limits(new_pan_x)
        else:
            # Mouse is to the left of the grid
            pass

    def render_text(self, text: str, x_pos: float, y_pos: float,
                    z_pos: float = 0, font=GLUT.GLUT_BITMAP_HELVETICA_12,
                    flush: bool = True, clear: bool = True):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def save(self, filename):
        """Save the current view to a PNG image file."""
        self.update_dimensions()
        data = GL.glReadPixels(0, 0, self.width, self.height, GL.GL_RGB,
                               GL.GL_UNSIGNED_BYTE, None)
        image = Image.frombytes("RGB", (self.width, self.height), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(filename, format="png")
