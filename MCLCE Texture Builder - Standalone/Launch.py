import Global
import Interface

# entry point requirement
Global.name = str(__name__)
if Global.name == "__main__":
    Interface.launch()