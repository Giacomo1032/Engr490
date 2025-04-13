from tkinter import *
from tkinter import messagebox
from math import sin, cos, radians


class Gauge(Frame):
    def __init__(
        self,
        parent,
        title="GAUGE",
        value=0,
        max_v=250,
        min_v=0,
        max_angle=240,
        size=320,
        partition=4,
        loc=(50, 80),
        col_range=[[255, 0, 0], [0, 255, 0], [255, 0, 0]],  # Red -> Green -> Red
    ):
        super().__init__(parent)
        self.value = value
        self.max_v = max_v
        self.min_v = min_v
        self.max_angle = max_angle
        self.size = size
        self.partition = partition
        self.loc = loc
        self.col_range = col_range
        self.tick_wid = 3
        self.arc_wid = 10
        # self.value_var = IntVar()  # Commented out as it's no longer needed
        self.title = title
        self.initUI()

    def initUI(self):
        self.canvas = Canvas(self, width=self.size + 100, height=self.size + 100)
        self.canvas.pack()
        self.color_set = generateColors(self.col_range, self.partition)
        self.canvas.create_text(
            self.loc[0] + self.size / 2,
            self.loc[1] - 30,
            text=self.title,
            font=("Helvetica", 12, "bold"),
        )
        self.drawArcs()
        self.drawTicks()
        self.drawPointer(self.value)
        self.drawDisplay(self.value)

        # entry = Entry(self, textvariable=self.value_var, width=5)
        # entry.pack(pady=5)
        # submit_btn = Button(self, text="UPDATE", command=self.handleUpdate)
        # submit_btn.pack()

    """
    def handleUpdate(self):
        try:
            value = float(self.value_var.get())
            if self.min_v <= value <= self.max_v:
                self.setValue(value)
            else:
                messagebox.showinfo(
                    "Invalid Value",
                    f"Value must be between {self.min_v} - {self.max_v}",
                )
        except ValueError:
            messagebox.showinfo("Invalid Value", "Please enter a valid number.")
    """

    def setValue(self, value):
        self.value = value
        self.canvas.delete("pointer")
        self.canvas.delete("display_box")
        self.drawPointer(self.value)
        self.drawDisplay(self.value)

    def drawArcs(self):
        for i in range(self.partition):
            self.canvas.create_arc(
                self.loc[0],
                self.loc[1],
                self.loc[0] + self.size,
                self.loc[1] + self.size,
                start=self.max_angle / self.partition * i - (self.max_angle - 180) / 2,
                extent=self.max_angle / self.partition,
                style="arc",
                outline=self.color_set[i],
                width=self.arc_wid,
                tags="arc",
            )

    def drawTicks(self):
        for i in range(self.partition + 1):
            value = self.max_v / self.partition * i
            length = self.arc_wid * 2
            offset = self.arc_wid / 2
            cx = self.loc[0] + self.size / 2
            cy = self.loc[1] + self.size / 2
            theta = 180 - (value * self.max_angle / (self.max_v - self.min_v) - (self.max_angle - 180) / 2)
            tip_x, tip_y = self.getLocOnArc(cx, cy, self.size / 2 + offset, theta)
            end_x, end_y = self.getLocOnArc(cx, cy, self.size / 2 + offset - length, theta)
            self.canvas.create_line(tip_x, tip_y, end_x, end_y, width=self.tick_wid, fill="#2b2d42")
            tag_x, tag_y = self.getLocOnArc(cx, cy, self.size / 2 + offset - length - 15, theta)
            self.canvas.create_text(tag_x, tag_y, text=round(value, 1), font=("Helvetica", 12, "italic"))

    def drawPointer(self, value):
        PIVOT_SIZE = 5
        PIVOT_COL = "silver"
        POINTER_UP = 0.8
        cx = self.loc[0] + self.size / 2
        cy = self.loc[1] + self.size / 2
        theta = 180 - (value * self.max_angle / (self.max_v - self.min_v) - (self.max_angle - 180) / 2)
        tip_x, tip_y = self.getLocOnArc(cx, cy, self.size * POINTER_UP / 2, theta)
        end_x, end_y = self.getLocOnArc(cx, cy, self.size * (1 - POINTER_UP) / 2, theta + 180)
        self.canvas.create_line(tip_x, tip_y, end_x, end_y, width=4, tags="pointer")
        self.drawPivot(cx, cy, PIVOT_SIZE, PIVOT_COL)

    def drawPivot(self, x, y, size, color):
        self.canvas.create_oval(
            x - size,
            y - size,
            x + size,
            y + size,
            fill=color,
            outline="",
        )

    def drawDisplay(self, value):
        section = (
            self.partition
            - 1
            - (value - self.min_v) * self.partition // (self.max_v - self.min_v)
        )
        text = self.canvas.create_text(
            self.loc[0] + self.size / 2,
            self.loc[1] + self.size + 15,
            text=value,
            font=("Helvetica", 12),
            fill="white",
            tags="display",
        )
        bbox = self.canvas.bbox(text)
        box = self.canvas.create_rectangle(
            bbox, outline="", fill=self.color_set[int(section)], tags="display_box"
        )
        self.canvas.tag_raise(text, box)

    def getLocOnArc(self, cx, cy, r, theta):
        theta = radians(theta)
        x = r * cos(theta) + cx
        y = cy - r * sin(theta)
        return x, y


def hexColor(rgb):
    red = int(rgb[0])
    green = int(rgb[1])
    blue = int(rgb[2])
    return "#{:02x}{:02x}{:02x}".format(red, green, blue)


def generateColors(c_range, steps):
    colors = []
    num_segments = len(c_range) - 1  # Number of color segments (e.g., red to green, green to red)
    steps_per_segment = steps // num_segments  # Steps per color segment

    for i in range(num_segments):
        start_color = c_range[i]
        end_color = c_range[i + 1]
        for j in range(steps_per_segment):
            red = start_color[0] + (end_color[0] - start_color[0]) * j / steps_per_segment
            green = start_color[1] + (end_color[1] - start_color[1]) * j / steps_per_segment
            blue = start_color[2] + (end_color[2] - start_color[2]) * j / steps_per_segment
            colors.append(hexColor([red, green, blue]))
    colors.append(hexColor(c_range[-1]))  # Add the last color
    return colors


if __name__ == "__main__":
    root = Tk()
    root.geometry("700x700+300+100")
    root.title("Gauge Dashboard")

    frame = Frame(root)
    frame.pack(pady=10)


    root.mainloop()