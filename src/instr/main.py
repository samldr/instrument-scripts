import typer
import pyvisa
from rich import print
import pdb
from typing_extensions import Annotated
from enum import Enum

# from instr.utils import ResourceManager
from instr.psu.dp832a import DP832A


DP832A_IP = "192.168.57.71" # Rigol DP832 #01

class FunctionType(str, Enum):
    voltage = "voltage"
    current = "current"


class ProtectionType(str, Enum):
    ovp = "ovp"
    ocp = "ocp"

app = typer.Typer()
dp832a_app = typer.Typer()
app.add_typer(dp832a_app, name="dp832a")
channel_app = typer.Typer()
dp832a_app.add_typer(channel_app, name="ch")



## ROOT COMMANDS (instr ...)
@app.callback()
def main():
    """
    AlbertaSat instrument remote control scripts
    """
    global rm
    rm = pyvisa.ResourceManager("@py")



@app.command()
def ls():
    """
    List connected instruments
    """
    print(f'List of resources: {rm.list_resources()}')



### DP832A COMMANDS (instr dp832a ...)
@dp832a_app.callback()
def main():
    """
    Rigol DP832/A power supply subcommands
    """
    global dp
    dp = DP832A(rm, DP832A_IP)

@dp832a_app.command()
def about():
    """
    Show information about the connected power supply
    """
    res = dp.about()
    print(f'[bold]Connected to {res["manufacturer"]} {res["model"]} [/bold]\nS/N: {res["serial"]} \nFW Version: {res["firmware"]} \nIP: {DP832A_IP}')


@dp832a_app.command()
def status():
    """
    Show status of all channels
    """
    res = dp.status()
    for ch, ch_data in res.items():
        print(f'[bold]Channel {ch[-1]}[/bold]')
        print(f'Status: {ch_data["status"]}\nMeasured Voltage: {ch_data["voltage"]} V\nMeasured Current: {ch_data["current"]} A')


@dp832a_app.command()
def query(
    command: Annotated[str, typer.Argument(help="SCPI command")],
    ):
    """
    Manually send a command to the power supply
    """
    print(f'{dp.query(command)}')


### DP832A CHANNEL COMMANDS (instr dp832a ch ...)
@channel_app.callback()
def channel_callback(
    channel: Annotated[int, typer.Argument(min=1, max=3, help="Channel to modify (1, 2, or 3)")],
):
    """
    Channel-specific commands
    """
    global ch
    ch = channel


@channel_app.command()
def set(
    type: Annotated[FunctionType, typer.Argument(help="Function to set")],
    value: Annotated[int, typer.Argument(help="Value to set in mV/mA")]
):
    """
    Set the voltage or current limit
    """
    try:
        dp.set_function(ch, type.value, value)
    except Exception as e:
        print(f"Error setting CH{ch} {type.value} to {value}: {e}")
    else:
        print(f'Set CH{ch} {type.value} to {value}')

@channel_app.command()
def on():
    """
    Turn the channel output on
    """
    res = dp.output_on(ch)
    print(f'Output for CH{ch}: {res}') 


@channel_app.command()
def off():
    """
    Turn the channel output off
    """
    res = dp.output_off(ch)
    print(f'Output for CH{ch}: {res}') 

@channel_app.command()
def mode(
   type: Annotated[ModeType, typer.Argument(help="Mode of operation")],
):
    """
    Set the channel mode (constant voltage or constant current)
    """
    try:
        dp.set_mode(ch, type.value)
    except Exception as e:
        print(f"Error setting CH{ch} mode to {type.value}: {e}")
    else:
        print(f'Set CH{ch} mode to {type.value}')



if __name__ == "__main__":   
    app()
