import typer
import pyvisa
from rich import print
import pdb
from instr.psu import channel

RIGOL_TCPIP="TCPIP0::192.168.57.71::INSTR" # Rigol DP832 #01

app = typer.Typer()
app.add_typer(channel.app, name="ch")

class Connector:
    def __init__(self):
        self.rm = None
        self.inst = None

    def connect(self):
        self.rm = pyvisa.ResourceManager("@py")
        self.inst = self.rm.open_resource(RIGOL_TCPIP)
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

    def get_resources(self):
        return self.rm, self.inst


@app.callback()
def main():
    """
    Rigol DP832/A power supply subcommands
    """
    global rm, inst
    rm = pyvisa.ResourceManager("@py")
    inst = rm.open_resource(RIGOL_TCPIP)
    inst.read_termination = '\n'
    inst.write_termination = '\n'
 
    
    # rm = Connector().rm
    # inst = Connector().inst
    # print("[bold red]WARNING: There is very important equipment connected to the power supply channels. \nJust because you can’t see it doesn’t mean you can’t damage it.\nMake sure you understand the command you’re sending.\n")

# @app.command()
# def status():
    
#     print(f'List of resources: {rm.list_resources()}')

#     print(f'Connected to: {inst.query('*IDN?')} at {RIGOL_TCPIP}')
#     #print(f'Channel 1 Summary: {inst.query('? CH1')}')


@app.command()
def about():
    """
    Show information about the connected power supply
    """
    idn = inst.query("*IDN?").split(',')
    ip = RIGOL_TCPIP.split("::")[1]
    print(f'[bold]Connected to {idn[0]} {idn[1]} [/bold]\nS/N: {idn[2]} \nFW Version: {idn[3]} \nIP: {ip}')

@app.command()
def status():
    """
    Show status of all channels
    """
    for ch in range(1,4):
        ch_status = inst.query(f':MEAS:ALL? CH{ch}').strip().split(',')

        print(f'[bold]Channel {ch}[/bold]')
        print(f'Measured Voltage: {ch_status[0]} V\nMeasured Current: {ch_status[1]} A\nMeasured Power: {ch_status[2]} W') 

@app.command()
def query(command: str):
    """
    Manually send a command to the power supply
    """
    print(f'{inst.query(command)}')

if __name__ == "__main__":
    app()

