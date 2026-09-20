import reflex as rx

import logging
from datetime import datetime, timezone
from typing import TypedDict

from sqlalchemy import text


class AccountRow(TypedDict):
    id: int
    username: str
    user_type: str
    created_at: str
    updated_at: str


class RegistryState(rx.State):
    accounts: list[AccountRow] = []
    selected_ids: list[int] = []
    search: str = ""
    user_type: str = "All"
    loading: bool = False
    error: str = ""
    last_loaded: str = ""

    @rx.var
    def visible_accounts(self) -> list[AccountRow]:
        query = self.search.strip().casefold()
        return [
            row
            for row in self.accounts
            if query in row["username"].casefold()
            and (
                self.user_type == "All"
                or row["user_type"] == self.user_type.lower()
            )
        ]

    @rx.var
    def all_selected(self) -> bool:
        visible = self.visible_accounts
        return bool(visible) and all(
            row["id"] in self.selected_ids for row in visible
        )

    def _reconcile_selection(self):
        visible = {row["id"] for row in self.visible_accounts}
        self.selected_ids = sorted(set(self.selected_ids) & visible)

    @rx.event
    def change_search(self, value: str):
        self.search = value
        self._reconcile_selection()

    @rx.event
    def change_type(self, value: str):
        if value in {"All", "Admin", "User"}:
            self.user_type = value
            self._reconcile_selection()

    @rx.event
    def clear_filters(self):
        self.search = ""
        self.user_type = "All"
        self._reconcile_selection()

    @rx.event
    def toggle_row(self, account_id: int):
        if self.loading or self.error:
            return
        visible = {row["id"] for row in self.visible_accounts}
        selected = set(self.selected_ids) & visible
        if account_id in visible:
            selected.symmetric_difference_update({account_id})
        self.selected_ids = sorted(selected)

    @rx.event
    def toggle_all(self):
        if self.loading or self.error:
            return
        self.selected_ids = (
            []
            if self.all_selected
            else sorted({row["id"] for row in self.visible_accounts})
        )

    @rx.event
    def clear_selection(self):
        self.selected_ids = []

    @rx.event(background=True)
    async def load_accounts(self):
        async with self:
            if self.loading:
                return
            self.loading = True
            self.error = ""
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT id, username, user_type, created_at, updated_at FROM users ORDER BY id ASC"
                    )
                )
                rows = result.mappings().all()
            accounts: dict[int, AccountRow] = {}
            for row in rows:
                account_id = int(row["id"])
                accounts[account_id] = {
                    "id": account_id,
                    "username": str(row["username"] or ""),
                    "user_type": str(row["user_type"] or "").lower(),
                    "created_at": row["created_at"]
                    .astimezone(timezone.utc)
                    .strftime("%d %b %Y · %H:%M")
                    if row["created_at"]
                    else "—",
                    "updated_at": row["updated_at"]
                    .astimezone(timezone.utc)
                    .strftime("%d %b %Y · %H:%M")
                    if row["updated_at"]
                    else "—",
                }
            async with self:
                self.accounts = list(accounts.values())
                self._reconcile_selection()
                self.last_loaded = datetime.now(timezone.utc).strftime(
                    "%H:%M:%S UTC"
                )
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                self.accounts = []
                self.selected_ids = []
                self.error = "We couldn’t load the account registry. Please try refreshing."
        finally:
            async with self:
                self.loading = False
