import typer
import pyvisa
from instr.psu import dp832a
from instr.load import dl3021

__version__ = "0.1.0"

app = typer.Typer()

app.add_typer(dp832a.app, name="dp832a")
app.add_typer(dl3021.app, name="dl3021")

def version_callback(value: bool):
    if value:
        print(f"Awesome CLI Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main():
    """
    AlbertaSat instrument remote control scripts
    """
    print("\n")

@app.command()
def ls():
    """
    List connected instruments
    """
    rm = pyvisa.ResourceManager("@py")
    print(f'List of resources: {rm.list_resources()}')

if __name__ == "__main__":   
    app()



