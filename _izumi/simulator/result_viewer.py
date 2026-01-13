import sys, json,os,re
from PyQt6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,QWidget,QVBoxLayout
)
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt

STATE_COLORS = {
    "Idle": "#eeeeee",
    "Busy": "#aaaaaa",
    "WaitBackoff": "#ffcc00",
    "WaitDIFS": "#66ccff",
    "WaitSIFS": "#99ddff",
    "Receiving": "#00cc66",
    "Sending": "#ff6666",
}

ROW_HEIGHT = 15
TIME_SCALE = 1    # 1 time unit = 5px
SLOT_TIME = 9.0   # Backoffの1スロットの長さ（シミュレータと一致させる）


class TimeRuler(QGraphicsView):
    def __init__(self, max_time):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.max_time = max_time
        self.setFixedHeight(40)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.draw()

    def draw(self):
        step = 100      # 時間刻み
        px = TIME_SCALE

        for t in range(0, int(self.max_time)+1, step):
            x = 150 + t * px
            self.scene.addLine(x, 0, x, 15)
            self.scene.addText(str(t)).setPos(x+2, 15)

        self.scene.setSceneRect(0, 0, self.max_time * px + 200, 30)



class TimelineViewer(QGraphicsView):
    def __init__(self, data):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.devices = sorted(set(d["device"] for d in data), key=lambda x: int(list(re.findall(r'\d+',x)+[-1])[0]))
        self.device_y = {d: i for i, d in enumerate(self.devices)}

        self.max_time = self.draw_timeline(data)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def draw_timeline(self, data):
        dev_map = {}
        for e in data:
            dev_map.setdefault(e["device"], []).append(e)

        max_time = 0

        for dev, events in dev_map.items():
            y = self.device_y[dev] * ROW_HEIGHT
            self.scene.addText(dev).setPos(0, y)

            for i, e in enumerate(events):
                t0 = e["time"]
                t1 = events[i+1]["time"] if i+1 < len(events) else t0 + 10
                max_time = max(max_time, t1)
                self.draw_state(y, t0, t1, e["state"])

        self.scene.setSceneRect(0, 0, max_time * TIME_SCALE + 200,
                                 len(self.devices) * ROW_HEIGHT)
        return max_time

    def draw_state(self, y, t0, t1, state):
        x0 = 150 + t0 * TIME_SCALE
        w  = (t1 - t0) * TIME_SCALE

        color = QColor(STATE_COLORS[state])
        pen = QPen(Qt.GlobalColor.black)

        if state == "WaitBackoff":
            t = t0
            while t < t1:
                x = 150 + t * TIME_SCALE
                w = min(SLOT_TIME, t1 - t) * TIME_SCALE
                self.scene.addRect(x, y, w, ROW_HEIGHT-0, pen, QBrush(color))
                t += SLOT_TIME
        else:
            self.scene.addRect(x0, y, w, ROW_HEIGHT-0, pen, QBrush(color))



class MainWidget(QWidget):
    def __init__(self, data):
        super().__init__()

        self.timeline = TimelineViewer(data)
        self.ruler = TimeRuler(self.timeline.max_time)

        # 横スクロール同期
        self.timeline.horizontalScrollBar().valueChanged.connect(
            self.ruler.horizontalScrollBar().setValue
        )
        self.ruler.horizontalScrollBar().valueChanged.connect(
            self.timeline.horizontalScrollBar().setValue
        )

        layout = QVBoxLayout()
        layout.addWidget(self.ruler)
        layout.addWidget(self.timeline)
        self.setLayout(layout)

# -----------------------------

if __name__ == "__main__":
    example_json = """
    [
      {"device":"AP","time":0,"state":"Idle"},
      {"device":"AP","time":10,"state":"Sending"},
      {"device":"AP","time":25,"state":"Idle"},

      {"device":"STA1","time":0,"state":"Idle"},
      {"device":"STA1","time":5,"state":"WaitBackoff"},
      {"device":"STA1","time":18,"state":"Sending"},
      {"device":"STA1","time":30,"state":"Idle"}
    ]
    """

    with open(os.path.join(os.path.dirname(__file__),'result','log_0_24_20260113095230.json'),'r',encoding='utf-8') as f:
        example_json = json.load(f)

    print(sorted(example_json.keys(),key=lambda x:int(list(re.findall(r'\d+',x)+[0])[0])))

    d = [{
        "device": k,
        "time": i[0],
        "state": i[2]
    } for k in sorted(example_json.keys(),key=lambda x:int(list(re.findall(r'\d+',x)+[0])[0])) for i in list([(0,k,'WaitBackoff')]+example_json[k])]




    #data = json.loads(example_json)

    app = QApplication(sys.argv)
    w = MainWidget(d)
    w.setWindowTitle("Wireless MAC Timeline Viewer")
    w.resize(1000, 400)
    w.show()
    sys.exit(app.exec())
