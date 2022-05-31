"""Description of that this does

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.

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

    def __init__(self, parent, devices, monitors):
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

        # Width and height of drawing
        self.drawing_width = 0
        self.drawing_height = 0

        # Horizontal starting position of signal waveforms and grid
        self.grid_origin = 0
        # Waveform drawing parameters to be tweaked
        # Initial x and y coordinates (i.e. left and bottom borders)
        self.initial_x = 20
        self.initial_y = 40
        # Horizontal width of one clock cycle
        self.waveform_width = 30
        # Vertical height between low and high signals
        self.waveform_height = 30
        # Multiplicative factor,
        # scales horizontal space for the device name
        self.margin_scale = 9
        # Horizontal spacing between device name and waveform
        self.margin_offset = 9
        # Vertical spacing between signals of different devices
        self.device_vertical_spacing = 50
        # Vertical offset of device label from low signal line
        self.device_label_offset = 10
        assert self.device_vertical_spacing >= self.waveform_height
        # Vertical offset of clock name label and clock labels
        self.clock_name_label_offset = 10
        self.clock_label_offset = 12
        # Vertical spacing between clock axis and first signal
        self.clock_vertical_spacing = 30

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

    def render_signals(self, set_scroll = True, flush_pan = False):
        # Set left margin width
        cycle_chars = 4  # 'cycle' label ~4 characters wide
        if self.monitors.get_margin() is not None:
            margin = max(self.monitors.get_margin(), cycle_chars)
        else:
            margin = cycle_chars

        # Set waveform/grid origin
        self.grid_origin = \
            self.initial_x + margin * self.margin_scale + self.margin_offset

        # Scale waveform horizontally
        curr_waveform_width = self.waveform_width * self.zoom

        # Update drawing height
        self.drawing_height = \
            self.initial_y * 2 + self.clock_vertical_spacing + \
            self.device_vertical_spacing * \
            len(self.monitors.monitors_dictionary)
        # Use initial_y as top margin as well

        # Update drawing width
        self.drawing_width = \
            self.grid_origin + curr_waveform_width * \
            self.parent.cycles_completed + self.initial_x
        # Use initial_x as right margin as well

        # Enforce pan limits
        self.enforce_pan_x_limits(self.pan_x)
        self.enforce_pan_y_limits(self.pan_y)

        if flush_pan:
            # Flush pan to the right
            width_limit = max(0, self.drawing_width - self.width)
            self.pan_x = -width_limit
            self.init = False

        # This should run after self.pan_x and self.pan_y are updated,
        # so that glTranslated uses the correct values
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        if not self.monitors.monitors_dictionary:
            # No monitors, reset
            self.drawing_width = 0
            self.drawing_height = 0
            if set_scroll:
                self.parent.set_scroll()  # make sure the scrollbar is disabled

            GL.glFlush()
            self.SwapBuffers()
            return

        # Draw the cycle axis
        cycles = len(list(self.monitors.monitors_dictionary.values())[0])
        x = self.initial_x
        y = self.initial_y - self.clock_name_label_offset
        self.render_text("Cycle", x - self.pan_x, y - self.pan_y,
                         font=GLUT.GLUT_BITMAP_HELVETICA_12, flush=False)
        # account for pan
        x = self.grid_origin  # reset x coordinate for the grid
        y = self.initial_y
        GL.glColor3f(0.0, 0.0, 0.0)  # clock axis is black
        GL.glBegin(GL.GL_LINE_STRIP)
        GL.glVertex2f(x - self.pan_x, y - self.pan_y)
        GL.glVertex2f(x + cycles * curr_waveform_width, y - self.pan_y)
        # account for pan
        GL.glEnd()

        # Interval for the vertical grid lines
        grid_interval = max(math.floor(1.1 / self.zoom),
                            1)  # 1.1 is a fudge factor

        # Draw vertical grid lines and labels
        x = self.grid_origin  # reset x coordinate
        y = self.initial_y  # reset y coordinate
        number_devices = len(self.monitors.monitors_dictionary)
        for i in range(0, cycles + 1, grid_interval):
            # Only draw every grid_interval
            if x < self.grid_origin - self.pan_x:
                # Don't bother drawing if grid lines to the left of
                # visible area
                x += grid_interval * curr_waveform_width
                continue

            GL.glColor3f(0.85, 0.85, 0.85)  # grid lines are light grey
            GL.glBegin(GL.GL_LINE_STRIP)
            GL.glVertex2f(x, y - self.pan_y)  # account for pan
            y_top = y + self.device_vertical_spacing * number_devices + \
                self.clock_vertical_spacing
            GL.glVertex2f(x, y_top)
            GL.glEnd()
            # Cycle labels
            self.render_text(str(i), x,
                             y - self.clock_label_offset - self.pan_y,
                             font=GLUT.GLUT_BITMAP_HELVETICA_10, flush=False,
                             clear=False)  # account for pan
            x += grid_interval * curr_waveform_width

        # Reset y coordinate and offset
        y = self.initial_y + self.clock_vertical_spacing

        # Draw waveforms
        for device_id, output_id in reversed(
                self.monitors.monitors_dictionary):
            # reversed() because we draw from bottom to top
            if y < self.initial_y + self.clock_vertical_spacing - self.pan_y:
                # Don't bother drawing if waveforms are below the
                # visible area or obscuring the cycle axis
                y += self.device_vertical_spacing
                continue

            monitor_name = self.devices.get_signal_name(device_id, output_id)
            # Align text to the left
            x = self.initial_x
            y += self.device_label_offset  # Offset for label
            self.render_text(monitor_name, x - self.pan_x, y,
                             font=GLUT.GLUT_BITMAP_9_BY_15, flush=False,
                             clear=False)  # account for pan

            x = self.grid_origin  # reset x coordinate
            y -= self.device_label_offset  # return to low signal line
            signal_list = self.monitors.monitors_dictionary[
                (device_id, output_id)]
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)

            for signal in signal_list:
                if x < self.grid_origin - self.pan_x - curr_waveform_width:
                    # Don't bother drawing if waveforms are to the left
                    # of visible area
                    x += curr_waveform_width
                    continue
                elif x < self.grid_origin - self.pan_x:
                    # Partially visible, add offset to avoid waveform
                    # obscuring labels
                    offset = self.grid_origin - self.pan_x - x
                else:
                    # No need to change anything
                    offset = 0

                # Signals for a particular device
                if signal == self.devices.HIGH:
                    GL.glVertex2f(x + offset, y + self.waveform_height)
                    GL.glVertex2f(x + curr_waveform_width,
                                  y + self.waveform_height)
                if signal == self.devices.LOW:
                    GL.glVertex2f(x + offset, y)
                    GL.glVertex2f(x + curr_waveform_width, y)
                if signal == self.devices.RISING:
                    GL.glVertex2f(x + offset, y)
                    GL.glVertex2f(x + curr_waveform_width,
                                  y + self.waveform_height)
                if signal == self.devices.FALLING:
                    GL.glVertex2f(x + offset, y + self.waveform_height)
                    GL.glVertex2f(x + curr_waveform_width, y)
                if signal == self.devices.BLANK:
                    pass
                x += curr_waveform_width

            # end for signal in signal_list
            GL.glEnd()
            y += self.device_vertical_spacing  # move up for the next device

        # end for device_id, output_id in
        # reversed(self.monitors.monitors_dictionary)

        # Set scrollbar
        if set_scroll:
            self.parent.set_scroll()

        # We have been drawing to the back buffer, flush the graphics
        # pipeline and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    
    def enforce_pan_y_limits(self, new_pan_y: float) -> None:
        height_limit = max(0, self.drawing_height - self.height)
        self.pan_y = max(min(new_pan_y, 0), - height_limit)

    def enforce_pan_x_limits(self, new_pan_x: float) -> None:
        width_limit = max(0, self.drawing_width - self.width)
        self.pan_x = max(min(new_pan_x, 0), - width_limit)

    def adjust_pan_x(self, event: wx.Event, old_zoom: float) -> None:
        offset = event.GetX() - self.pan_x - self.grid_origin
        if offset > 0:
            # The mouse is within the grid
            pos = offset / old_zoom
            new_x = pos * self.zoom + self.grid_origin
            new_pan_x = event.GetX() - new_x
            self.enforce_pan_x_limits(new_pan_x)
        else:
            # Mouse is to the left of the grid
            pass

    # def render(self, text):
    #     """Handle all drawing operations."""
    #     self.SetCurrent(self.context)
    #     if not self.init:
    #         # Configure the viewport, modelview and projection matrices
    #         self.init_gl()
    #         self.init = True

    #     # Clear everything
    #     GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    #     # Draw specified text at position (10, 10)
    #     self.render_text(text, 10, 10)

    #     # Draw a sample signal trace
    #     GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
    #     GL.glBegin(GL.GL_LINE_STRIP)
    #     for i in range(10):
    #         x = (i * 20) + 10
    #         x_next = (i * 20) + 30
    #         if i % 2 == 0:
    #             y = 75
    #         else:
    #             y = 100
    #         GL.glVertex2f(x, y)
    #         GL.glVertex2f(x_next, y)
    #     GL.glEnd()

    #     # We have been drawing to the back buffer, flush the graphics pipeline
    #     # and swap the back buffer to the front
    #     GL.glFlush()
    #     self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render_signals()
        # size = self.GetClientSize()
        # text = "".join(["Canvas redrawn on paint event, size is ",
        #                 str(size.width), ", ", str(size.height)])
        # self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])

        self.render_signals()

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

    def save(self, filename: str) -> None:
        """
        Save the current view to a PNG image file.

        Parameters
        ----------
        `filename`: filename for the image file

        Returns
        -------
        `None`
        """
        self.update_dimensions()
        data = GL.glReadPixels(0, 0, self.width, self.height, GL.GL_RGB,
                               GL.GL_UNSIGNED_BYTE, None)
        image = Image.frombytes("RGB", (self.width, self.height), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save(filename, format="png")