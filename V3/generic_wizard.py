from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QStackedWidget, QMessageBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QDate, QRect
from db_manager import DBManager
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

# Hilfsklasse für Icon-Buttons mit Hover-Effekt
class HoverIconButton(QPushButton):
    def __init__(self, icon_normal, icon_hover, icon_size, icon_size_hover, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_normal = QIcon(icon_normal)
        self.icon_hover = QIcon(icon_hover)
        self.icon_size = icon_size
        self.icon_size_hover = icon_size_hover
        self.setIcon(self.icon_normal)
        self.setIconSize(self.icon_size)
        self.setStyleSheet("background: transparent; border: none;")

    def enterEvent(self, event):
        self.setIcon(self.icon_hover)
        self.setIconSize(self.icon_size_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.icon_normal)
        self.setIconSize(self.icon_size)
        super().leaveEvent(event)

class GenericWizard(QWidget):
    def __init__(self, fields, callback=None, db_table=None, parent=None, title="Wizard", geometry_source=None):
        # Der Parent dient nur noch zur Blockierung anderer Fenster (Modalität)
        super().__init__(parent)

        # Mache den Wizard IMMER zu einem eigenständigen, rahmenlosen Dialog
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fields = fields
        self.callback = callback
        self.db_table = db_table
        self.inputs = {}
        self.title = title
        self.db = DBManager()

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: white;
                font-size: 14pt;
                font-family: 'Ubuntu', sans-serif;
            }
            /* Die Regel für nahtlose Seiten bleibt, da sie korrekt war */
            QStackedWidget > QWidget {
                background-color: transparent;
                border: none;
            }
            QLineEdit, QDateEdit, QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0,0,0,0.02), stop:1 rgba(255,255,255,0.05));
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 44pt;
                padding: 25px 30px;
                qproperty-alignment: AlignCenter;
                selection-background-color: #a2ffb5;
                selection-color: #232323;
            }
            QComboBox::drop-down { border: none; }
            QPushButton#btn_cancel {
                border: none; background: transparent; font-size: 22pt; color: red;
            }
            QPushButton#btn_cancel:hover { color: #ff5f5f; }
            QPushButton#btn_save {
                background-color: #2ecc71; border: none; border-radius: 10px;
                font-size: 16pt; color: white; padding: 10px 30px;
            }
            QPushButton#btn_save:hover { background-color: #48e88b; }
            
            /* Kalender-Styling vom DriverWizard */
            QDateEdit::drop-down { border: none; width: 40px; background: transparent; }
            QDateEdit::down-arrow { image: none; border: none; width: 0px; height: 0px; }
            QCalendarWidget {
                background-color: #2c2c2c; color: white; font-size: 14pt;
                border: 2px solid #555; border-radius: 10px;
            }
            QCalendarWidget QToolButton {
                background-color: #444; color: white; border: 1px solid #666;
                border-radius: 5px; padding: 5px;
            }
            QCalendarWidget QToolButton:hover { background-color: #555; }
            QCalendarWidget QMenu {
                background-color: #2c2c2c; color: white; border: 1px solid #555;
            }
            QCalendarWidget QSpinBox {
                background-color: #444; color: white; border: 1px solid #666;
                border-radius: 3px;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #2c2c2c; color: white;
                selection-background-color: #2ecc71; selection-color: white;
            }
        """)

        # Standardmäßig die Geometrie des Elternteils nehmen
        source = parent
        if geometry_source:
            # Wenn eine Quelle angegeben ist, diese verwenden
            source = geometry_source
        
        if source:
            self.setGeometry(source.geometry())

        # Setze die Schriftart explizit auf Ubuntu
        font = QFont('Ubuntu')
        self.setFont(font)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        self.setLayout(layout)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.create_pages()
        QTimer.singleShot(50, self.set_initial_focus)
        self.show()
        self.raise_()
        self.setFocus()
        self.center_on_screen()

    def create_pages(self):
        for i, field_config in enumerate(self.fields):
            label_text, db_column, input_type = field_config[:3]
            options = field_config[3] if len(field_config) > 3 else []
            
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(20, 60, 20, 40)
            page_layout.addStretch(3)

            label = QLabel(label_text.upper())
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("font-size: 18pt; letter-spacing: 2px; color: #aaa;")
            label_wrapper = QHBoxLayout()
            label_wrapper.addStretch()
            label_wrapper.addWidget(label)
            page_layout.addLayout(label_wrapper)

            # --- Widget-Erstellung basierend auf input_type ---
            field: QWidget
            if input_type == "date":
                field = QDateEdit()
                field.setDate(QDate.currentDate())
                field.setCalendarPopup(True)
                field.dateChanged.connect(lambda: QTimer.singleShot(300, self.next_page))
            elif input_type == "combo":
                field = QComboBox()
                field.addItems(options)
                field.setEditable(True)
                le = field.lineEdit()
                if le is not None:
                    le.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    le.returnPressed.connect(self.next_page)
            else: # "text" or default
                field = QLineEdit()
                field.textChanged.connect(lambda _, w=field: self.adjust_font_size(w))
                field.returnPressed.connect(self.next_page)

            field.setMinimumHeight(110)
            field.setMinimumWidth(850)
            if isinstance(field, (QLineEdit, QDateEdit)):
                 field.setAlignment(Qt.AlignmentFlag.AlignCenter)
            field.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            if hasattr(field, "setFont"):
                 font = field.font()
                 font.setPointSize(44)
                 field.setFont(font)

            # --- Pfeil-Navigation ---
            nav_row = QHBoxLayout()
            nav_row.setSpacing(20)
            nav_row.addStretch()
            # Linker Pfeil (nur wenn nicht erste Seite)
            if i > 0:
                btn_prev = QPushButton()
                btn_prev.setObjectName("btn_prev")
                btn_prev.setFixedSize(60, 60)
                btn_prev.setStyleSheet("""
                    QPushButton#btn_prev {
                        border-radius: 30px;
                        background: transparent;
                        color: #aaa;
                        font-size: 32pt;
                    }
                    QPushButton#btn_prev:hover {
                        color: #ff9900;
                        font-size: 44pt;
                        min-width: 80px;
                        min-height: 80px;
                    }
                """)
                btn_prev.setText("<")
                btn_prev.clicked.connect(lambda _, idx=i: self.stack.setCurrentIndex(idx-1))
                nav_row.addWidget(btn_prev)
            else:
                nav_row.addSpacing(60)
            # Eingabefeld
            nav_row.addWidget(field, stretch=2)
            # Rechter Pfeil (außer letzte Seite)
            if i < len(self.fields) - 1:
                btn_next = QPushButton()
                btn_next.setObjectName("btn_next")
                btn_next.setFixedSize(60, 60)
                btn_next.setStyleSheet("""
                    QPushButton#btn_next {
                        border-radius: 30px;
                        background: transparent;
                        color: #aaa;
                        font-size: 32pt;
                    }
                    QPushButton#btn_next:hover {
                        color: #ff9900;
                        font-size: 44pt;
                        min-width: 80px;
                        min-height: 80px;
                    }
                """)
                btn_next.setText(">")
                btn_next.clicked.connect(lambda _, idx=i: self.stack.setCurrentIndex(idx+1))
                nav_row.addWidget(btn_next)
            else:
                btn_save = HoverIconButton(
                    "Style/assets/icons/check_white.svg",
                    "Style/assets/icons/check_orange.svg",
                    QSize(40, 40),
                    QSize(56, 56)
                )
                btn_save.setObjectName("btn_save")
                btn_save.setFixedSize(60, 60)
                btn_save.clicked.connect(self.save)
                nav_row.addWidget(btn_save)
            nav_row.addStretch()
            page_layout.addSpacing(40)
            page_layout.addLayout(nav_row)

            # X-Button zentriert zwischen Eingabefeld und unterem Rand
            x_row = QHBoxLayout()
            x_row.addStretch()
            cancel_btn = HoverIconButton(
                "Style/assets/icons/close_gray.svg",
                "Style/assets/icons/close_red.svg",
                QSize(32, 32),
                QSize(48, 48)
            )
            cancel_btn.setObjectName("btn_cancel")
            cancel_btn.setFixedSize(40, 40)
            cancel_btn.clicked.connect(self.close_wizard)
            x_row.addWidget(cancel_btn)
            x_row.addStretch()
            page_layout.addSpacing(30)
            page_layout.addLayout(x_row)
            page_layout.addStretch(5)

            self.stack.addWidget(page)
            self.inputs[db_column] = field

            if db_column == "kennzeichen" and isinstance(field, QLineEdit):
                def check_license_plate():
                    if not isinstance(field, QLineEdit):
                        return True
                    kennzeichen = field.text().strip()
                    if kennzeichen:
                        db = DBManager()
                        exists = db.get_fahrzeug_by_plate(kennzeichen)
                        if exists:
                            QMessageBox.warning(field, "Fehler", f"Das Kennzeichen '{kennzeichen}' existiert bereits!")
                            field.setFocus()
                            field.selectAll()
                            return False
                    return True
                field.editingFinished.connect(check_license_plate)
    
    def adjust_font_size(self, line_edit: QLineEdit, max_size=44, min_size=18):
        """Dynamische Schriftgrößenanpassung wie im VehicleWizard"""
        font = line_edit.font()
        metrics = line_edit.fontMetrics()
        text_width = metrics.horizontalAdvance(line_edit.text())
        available_width = line_edit.width() - 60
        if available_width <= 0:
            return

        ratio = text_width / available_width
        if ratio < 0.5:
            size = max_size
        elif ratio < 1.0:
            size = int(max_size - (max_size - min_size) * ratio)
        else:
            size = min_size

        font.setPointSize(size)
        line_edit.setFont(font)

    def set_initial_focus(self):
        if self.fields and self.inputs:
            first_key = self.fields[0][1]
            widget = self.inputs.get(first_key)
            if widget:
                widget.setFocus()
                if isinstance(widget, QLineEdit):
                    widget.selectAll()

    def focus_current_field(self):
        current_index = self.stack.currentIndex()
        if current_index < len(self.fields):
            db_column = self.fields[current_index][1]
            widget = self.inputs.get(db_column)
            if widget:
                widget.setFocus()
                if isinstance(widget, QLineEdit):
                    widget.selectAll()

    def next_page(self):
        index = self.stack.currentIndex()
        if index < self.stack.count() - 1:
            self.stack.setCurrentIndex(index + 1)
            QTimer.singleShot(50, self.focus_current_field)
        else:
            self.save()

    def save(self):
        data = {}
        for label, db_col, f_type, *opts in self.fields:
            widget = self.inputs[db_col]
            data[db_col] = widget.text() if isinstance(widget, QLineEdit) else widget.currentText()

        if self.callback:
            self.callback(data)

        self.close()

    def close_wizard(self):
        self.close()

    def center_on_screen(self):
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
        self.move(x, y) 