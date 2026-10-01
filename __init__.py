import random

from aqt import gui_hooks, mw
from aqt.qt import (
    QColor,
    QDialog,
    QEasingCurve,
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QPushButton,
    QTimer,
    QVBoxLayout,
    Qt,
)

_state = {"reveal": False, "syncro": False, "box": None}


class MessageBox(QDialog):
    def __init__(self, msg: str) -> None:
        super().__init__(mw)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(420)
        self._closing = False

        outside = QVBoxLayout(self)
        outside.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("cartao")
        card.setStyleSheet(
            """
            #cartao {
                background-color: #fff5f7;
                border: 2px solid #ffb3c6;
                border-radius: 24px;
            }
            #coracao { font-size: 56px; background: transparent; }
            #texto {
                color: #c2185b;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
            }
            #botao {
                background-color: #ff6b9d;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
            }
            #botao:hover { background-color: #ff4d8d; }

            #assinatura {
                color: #a9a9a9;
                font-size: 12px;
                font-weight: light;
                font-style: italic;
                background: transparent;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 90))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        cfg = mw.addonManager.getConfig(__name__)
        emoji = random.choice(cfg["emojis"])
        heart = QLabel(f"{emoji}")
        heart.setObjectName("coracao")
        heart.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text = QLabel(msg)
        text.setObjectName("texto")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)

        button = QPushButton("OK")
        button.setObjectName("botao")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.fade_out)

        asign = QLabel("Victor Marin")
        asign.setObjectName("assinatura")
        asign.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(heart)
        layout.addWidget(text)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(asign)

        outside.addWidget(card)

    def fade_in(self, end_pos: QPoint) -> None:
        start_pos = QPoint(end_pos.x(), end_pos.y() + 30)

        self.setWindowOpacity(0.0)
        self.move(start_pos)
        self.show()
        self.raise_()
        self.activateWindow()

        opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        opacity_anim.setDuration(600)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(600)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim = QParallelAnimationGroup(self)
        self._anim.addAnimation(opacity_anim)
        self._anim.addAnimation(pos_anim)
        self._anim.start()

    def fade_out(self) -> None:
        if self._closing:
            return
        self._closing = True

        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(350)
        anim.setStartValue(self.windowOpacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.close)

        self._anim_out = anim
        anim.start()


def show_message() -> None:
    if _state["reveal"]:
        return
    _state["reveal"] = True

    cfg = mw.addonManager.getConfig(__name__)
    msg = random.choice(cfg["messages"])

    box = MessageBox(msg)
    _state["box"] = box

    box.adjustSize()
    geo = mw.geometry()
    end_pos = QPoint(
        geo.center().x() - box.width() // 2,
        geo.center().y() - box.height() // 2,
    )
    box.fade_in(end_pos)


def init_sync() -> None:
    _state["syncro"] = True


def end_sync() -> None:
    _state["syncro"] = False
    QTimer.singleShot(1000, show_message)


def try_show() -> None:
    if not _state["syncro"]:
        show_message()


def when_open_profile() -> None:
    _state["reveal"] = False
    _state["syncro"] = False
    QTimer.singleShot(3000, try_show)


gui_hooks.profile_did_open.append(when_open_profile)
gui_hooks.sync_will_start.append(init_sync)
gui_hooks.sync_did_finish.append(end_sync)