import typer
import pyvisa
from rich import print
import pdb

RIGOL_TCPIP="TCPIP0::192.168.57.71::INSTR" # Rigol DP832 #01


app = typer.Typer()