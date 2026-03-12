from database import init_database
from appgui import AppGUI

if __name__ == "__main__":
    init_database()
    app = AppGUI()
    app.mainloop()
