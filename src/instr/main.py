import typer
import pyvisa
import time
from rich import print
from rich.table import Table
from rich.live import Live
from rich.text import Text

from typing_extensions import Annotated
from enum import Enum

from instr.psu.dp832a import DP832A

DP832A_IP = "192.168.57.73" # Rigol DP832 #01

class FunctionType(str, Enum):
    voltage = "voltage"
    current = "current"


class ProtectionType(str, Enum):
    ovp = "ovp"
    ocp = "ocp"


class MeasureType(str, Enum):
    voltage = "voltage"
    current = "current"
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
    global init



@app.command()
def ls():
    """
    List connected instruments
    """
    print(f'List of resources: {rm.list_resources()}')



### DP832A COMMANDS (instr dp832a ...)
@dp832a_app.callback()
def main(
    ip: Annotated[str, typer.Argument(help="IP address of the DP832A")],
    no_init: Annotated[bool, typer.Option("--unsafe", help="Initialize the power supply without resetting outputs", show_default=False)] = False,
):
    """
    Rigol DP832/A power supply subcommands
    """
    global dp
    dp = DP832A(rm, ip, not no_init)



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
    status = dp.status()
    with Live(make_table(status), refresh_per_second=1) as live:
        while True:
            time.sleep(1)
            status = dp.status()
            live.update(make_table(status))


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
def set(
    type: Annotated[MeasureType, typer.Argument(help="Function to set")],
    value: Annotated[int, typer.Argument(help="Value to set in mV/mA")]
):
    """
    Set the output voltage or current, or the OCP or OVP limit on the channel.
    """
    try:
        if type in [MeasureType.voltage, MeasureType.current]:
            dp.set_function(ch, type.value, value)
        elif type in [MeasureType.ovp, MeasureType.ocp]:
            dp.set_protection(ch, type.value, value)
    except Exception as e:
        print(f"Error setting CH{ch} {type.value} to {value}: {e}")
    else:
        unit='mV' if type.value in ['voltage', 'ovp'] else 'mA'
        print(f'Set CH{ch} {type.value} to {value} {unit}')


@channel_app.command()
def get(
    type: Annotated[MeasureType, typer.Argument(help="Function to get")],
):
    """
    Get the measured voltage or current, or the set OVP or OCP values on the channel.
    """
    try:
        value = dp.get_measure(ch, type.value)
    except Exception as e:
        print(f"Error getting CH{ch} {type.value}: {e}")
    else:
        unit='mV' if type.value in ['voltage', 'ovp'] else 'mA'
        print(f'Got CH{ch} {type.value}: {value} {unit}')

@channel_app.command()
def mode():
    """
    Get the channel's mode of operation.
    """
    try:
        mode = dp.get_mode(ch)
    except Exception as e:
        print(f"Error getting CH{ch} mode: {e}")
    else:
        print(f'CH{ch} mode: {mode}')


def make_table(status):

    def format_cell(value, *, unit=None):
        """
        - ON  -> green
        - OFF -> red
        - Numbers -> rounded to 3 decimals with units
        """
        # Handle ON / OFF
        if isinstance(value, str):
            v = value.upper()
            if v == "ON":
                return Text("ON", style="bold green")
            if v == "OFF":
                return Text("OFF", style="bold red")
            try:
                num = float(value)
            except ValueError:
                return Text(value)
            else:
                value = num

        # Handle numeric values
        if isinstance(value, (int, float)):
            if unit:
                text = f"{value:.3f} {unit}"
            else:
                text = f"{value:.3f}"
            return Text(text)

        # Fallback
        return Text(str(value))

    table = Table()
    table.add_column("Metric", justify="right", style=None, no_wrap=True)

    table.add_column("CH1", justify="center", header_style="bold yellow")
    table.add_column("CH2", justify="center", header_style="bold cyan")
    table.add_column("CH3", justify="center", header_style="bold magenta")

    def row(label, key, unit=None):
        cells = [
            format_cell(status[ch][key], unit=unit)
            for ch in status
        ]
        table.add_row(label, *cells)

    row("Output", "output_status")
    row("Voltage", "voltage", unit="V")
    row("Current", "current", unit="A")
    row("OVP Limit", "ovp_limit", unit="V")
    row("OCP Limit", "ocp_limit", unit="A")
    row("OVP Status", "ovp_status")
    row("OCP Status", "ocp_status")
    row("Mode", "mode")

    return table


if __name__ == "__main__":   
    app()
