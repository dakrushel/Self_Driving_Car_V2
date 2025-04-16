class OnScreenJoystick:
    """
    A canvas-based joystick: the user drags a 'knob' inside a circular base.
    The callback is called with dx, dy in range [-1, 1].
    """
    def __init__(self, parent, center_x, center_y, base_radius, knob_radius, command_callback):
        self.parent = parent
        self.cx = center_x
        self.cy = center_y
        self.base_r = base_radius
        self.knob_r = knob_radius
        self.command_callback = command_callback

        # Draw base
        self.base = parent.create_oval(
            self.cx - self.base_r, self.cy - self.base_r,
            self.cx + self.base_r, self.cy + self.base_r,
            outline="#666", width=2, fill="#333"
        )

        # Draw knob
        self.knob = parent.create_oval(
            self.cx - self.knob_r, self.cy - self.knob_r,
            self.cx + self.knob_r, self.cy + self.knob_r,
            outline="#aaa", width=1, fill="#aaa"
        )

        self.dragging = False

        # Bind events
        parent.tag_bind(self.knob, "<ButtonPress-1>", self.start_drag)
        parent.tag_bind(self.knob, "<B1-Motion>", self.drag)
        parent.tag_bind(self.knob, "<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.dragging = True

    def drag(self, event):
        if not self.dragging:
            return

        dx = event.x - self.cx
        dy = event.y - self.cy
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > self.base_r:
            ratio = self.base_r / dist
            dx *= ratio
            dy *= ratio

        # Move knob
        self.parent.coords(
            self.knob,
            self.cx + dx - self.knob_r, self.cy + dy - self.knob_r,
            self.cx + dx + self.knob_r, self.cy + dy + self.knob_r
        )

        # Normalize to [-1, 1]
        norm_x = dx / self.base_r
        norm_y = dy / self.base_r
        self.command_callback(norm_x, norm_y)

    def end_drag(self, event):
        self.dragging = False
        # Reset knob to center
        self.parent.coords(
            self.knob,
            self.cx - self.knob_r, self.cy - self.knob_r,
            self.cx + self.knob_r, self.cy + self.knob_r
        )
        self.command_callback(0, 0)
