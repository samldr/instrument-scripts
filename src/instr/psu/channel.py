import typer
import pyvisa
from rich import print
import pdb
from typing_extensions import Annotated
from enum import Enum
# from instr.psu.dp832a import Connector

app = typer.Typer()

class FunctionType(str, Enum):
    voltage = "voltage"
    current = "current"

@app.callback()
def channel_callback(
    channel: Annotated[int, typer.Argument(min=1, max=3, help="Channel to modify (1, 2, or 3)")],
):
    """
    Channel-specific commands
    """
    global ch
    ch = channel


@app.command()
def set(
    type: Annotated[FunctionType, typer.Argument(help="Function to set")],
    value: Annotated[int, typer.Argument(help="Value to set in mV/mA")]
):
    """
    Set the voltage or current limit
    """

@app.command()
def on():
    """
    Turn the channel output on
    """
    inst.query(f':OUTP CH{ch}, ON')


@app.command()
def off():
    """
    Turn the channel output off
    """
    inst.query(f':OUTP CH{ch}, OFF')
    

if __name__ == "__main__":
    app()