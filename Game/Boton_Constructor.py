from .Widget import Widget

class Button(Widget):

    def _on_click(self, event):
        if self.element in self.lista:
            self.parent.element = self.element
            return self.parent.element