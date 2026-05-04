from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider
from PySide6.QtCore import Qt

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        # Override click behavior to move to specific location
        if event.button() == Qt.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            
            # Calculate new value based on click position
            new_val = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), 
                                                     event.position().x() if self.orientation() == Qt.Horizontal else event.position().y(), 
                                                     self.width() if self.orientation() == Qt.Horizontal else self.height())
            self.setValue(new_val)
            self.sliderMoved.emit(new_val) # Trigger audio update
        super().mousePressEvent(event) # Allow normal behavior
