import reflex as rx

import logging
from datetime import datetime, timezone
from typing import TypedDict


class AccountRow(TypedDict):
    id: int
    username: str
    user_type: str
    created_at: str
    updated_at: str


SAMPLE_ACCOUNTS: list[AccountRow] = [
    {
        "id": 101,
        "username": "ava.mercer",
        "user_type": "admin",
        "created_at": "08 Jan 2025 · 09:15 UTC",
        "updated_at": "14 Feb 2025 · 16:42 UTC",
    },
    {
        "id": 102,
        "username": "noah.kim",
        "user_type": "user",
        "created_at": "11 Jan 2025 · 13:28 UTC",
        "updated_at": "12 Feb 2025 · 10:06 UTC",
    },
    {
        "id": 103,
        "username": "marisol.ortega",
        "user_type": "user",
        "created_at": "19 Jan 2025 · 08:47 UTC",
        "updated_at": "19 Jan 2025 · 08:47 UTC",
    },
    {
        "id": 104,
        "username": "theo.bennett",
        "user_type": "admin",
        "created_at": "27 Jan 2025 · 17:03 UTC",
        "updated_at": "15 Feb 2025 · 11:24 UTC",
    },
    {
        "id": 105,
        "username": "priya.nandakumar",
        "user_type": "user",
        "created_at": "02 Feb 2025 · 12:11 UTC",
        "updated_at": "09 Feb 2025 · 14:38 UTC",
    },
    {
        "id": 106,
        "username": "eli.rosenberg",
        "user_type": "user",
        "created_at": "05 Feb 2025 · 07:56 UTC",
        "updated_at": "16 Feb 2025 · 09:17 UTC",
    },
    {
        "id": 107,
        "username": "hana.sato",
        "user_type": "user",
        "created_at": "09 Feb 2025 · 15:19 UTC",
        "updated_at": "13 Feb 2025 · 18:05 UTC",
    },
    {
        "id": 108,
        "username": "lucas.fairchild",
        "user_type": "admin",
        "created_at": "12 Feb 2025 · 10:32 UTC",
        "updated_at": "17 Feb 2025 · 08:49 UTC",
    },
]


class RegistryState(rx.State):
    accounts: list[AccountRow] = []
    selected_ids: list[int] = []
    search: str = ""
    user_type: str = "all"
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
            and (self.user_type == "all" or row["user_type"] == self.user_type)
        ]

    @rx.var
    def all_selected(self) -> bool:
        return bool(self.visible_accounts) and all(
            row["id"] in self.selected_ids for row in self.visible_accounts
        )

    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_ids)

    def _reconcile_selection(self):
        visible = {row["id"] for row in self.visible_accounts}
        self.selected_ids = sorted(set(self.selected_ids) & visible)

    @rx.event
    def set_search(self, value: str):
        self.search = value
        self._reconcile_selection()

    @rx.event
    def set_user_type(self, value: str):
        self.user_type = value
        self._reconcile_selection()

    @rx.event
    def toggle_row(self, account_id: int):
        if self.loading:
            return
        if account_id in self.selected_ids:
            self.selected_ids.remove(account_id)
        elif any(row["id"] == account_id for row in self.visible_accounts):
            self.selected_ids.append(account_id)

    @rx.event
    def toggle_all(self):
        if not self.loading:
            self.selected_ids = (
                []
                if self.all_selected
                else sorted({row["id"] for row in self.visible_accounts})
            )

    @rx.event
    def clear_selection(self):
        self.selected_ids = []

    @rx.event
    def clear_filters(self):
        self.search = ""
        self.user_type = "all"
        self._reconcile_selection()

    @rx.event(background=True)
    async def load_accounts(self):
        async with self:
            if self.loading:
                return
            self.loading = True
            self.error = ""
        try:
            sample_accounts = [row.copy() for row in SAMPLE_ACCOUNTS]
            async with self:
                self.accounts = sample_accounts
                self._reconcile_selection()
                self.last_loaded = datetime.now(timezone.utc).strftime(
                    "%H:%M:%S UTC"
                )
                self.error = ""
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                self.accounts = []
                self.selected_ids = []
                self.error = "We couldn’t load the account registry. Please try refreshing."
        finally:
            async with self:
                self.loading = False
