import reflex as rx

from app.models import Base
from app.components.registry import registry
from app.states.registry_state import RegistryState

model_metadata = Base.metadata


def index() -> rx.Component:
    return registry()


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    index,
    route="/",
    title="Account registry | The account ledger",
    on_load=RegistryState.load_accounts,
)
