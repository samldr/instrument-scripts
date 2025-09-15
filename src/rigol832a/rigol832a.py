import typer
import pyvisa
import pyvisa_py
import vxi11
from rich import print
import pdb

RIGOL_TCPIP="TCPIP0::192.168.57.71::INSTR" # Dirty Room Rigol

app = typer.Typer()

@app.callback()
def main():
    global rm, inst
    rm = pyvisa.ResourceManager("@py")
    print(f'List of resources: {rm.list_resources()}')
    pdb.set_trace()
    inst = rm.open_resource(RIGOL_TCPIP)


    inst.read_termination = '\n'
    inst.write_termination = '\n'
    
    print("[bold red]WARNING: There is very important equipment connected to the power supply channels. \nJust because you can’t see it doesn’t mean you can’t damage it.\nMake sure you understand the command you’re sending.\n")

@app.command()
def status():
    print(f'List of resources: {rm.list_resources()}')
    print(f'Connected to: {inst.query('*IDN?')} at {RIGOL_TCPIP}')
    print(f'Channel 1 Summary: {inst.query('? CH1')}')



@app.command()
def list_insts():
    print("Testing")

@app.command()
def manual(command: str):
    """
    Manually send a command to the power supply.
    """
    print(f'{inst.query(command)}')

if __name__ == "__main__":
    app()

