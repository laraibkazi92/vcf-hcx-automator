import typer
import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine

app = typer.Typer(
    name="vcf-hcx",
    help="VCF HCX Automator - CLI for managing VMware HCX workflows",
    add_completion=True,
)

def coro(f: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Any]:
    """Decorator to run async commands with asyncio."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

from .commands.inventory import app as inventory_app
from .commands.mobility_group import app as mobility_group_app

app.add_typer(inventory_app, name="inventory")
app.add_typer(mobility_group_app, name="mobility-group")
