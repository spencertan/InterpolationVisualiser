from PySide6.QtWidgets import QApplication
from Window import *
import sys

def run():
  app = QApplication(sys.argv)
  window = Window()
  window.show()
  sys.exit(app.exec())

if __name__ == '__main__':
  run()
