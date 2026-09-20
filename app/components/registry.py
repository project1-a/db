import reflex as rx

from app.states.registry_state import AccountRow, RegistryState


BUTTON = "inline-flex items-center justify-center gap-2 rounded-md border border-[#d7d9d3] bg-white px-3 py-2 text-xs font-medium text-[#233641] hover:bg-[#eef2ee] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
CHECKBOX = "h-4 w-4 cursor-pointer rounded accent-blue-700 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-blue-700 disabled:cursor-not-allowed"


def heading_cell(label: str, icon: str) -> rx.Component:
    return rx.el.th(
        rx.el.div(
            rx.icon(icon, class_name="h-3.5 w-3.5 text-[#84918e]"),
            label,
            class_name="flex items-center gap-2",
        ),
        scope="col",
        class_name="px-5 py-4 text-left text-[11px] font-semibold uppercase tracking-wider text-[#64726f]",
    )


def account_row(row: AccountRow) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.input(
                type="checkbox",
                checked=RegistryState.selected_ids.contains(row["id"]),
                on_change=lambda _: RegistryState.toggle_row(row["id"]),
                on_click=rx.stop_propagation,
                disabled=RegistryState.loading,
                aria_label=f"Select {row['username']}",
                class_name=CHECKBOX,
            ),
            class_name="w-12 pl-5 pr-2 py-5",
        ),
        rx.el.td(
            f"#{row['id']}",
            class_name="px-5 py-5 text-xs tabular-nums text-[#7a8585]",
        ),
        rx.el.td(
            rx.el.span(
                row["username"], class_name="font-medium text-[#203440]"
            ),
            class_name="px-5 py-5 text-sm break-all min-w-48",
        ),
        rx.el.td(
            rx.el.span(
                rx.icon("circle", class_name="h-2 w-2 fill-current"),
                rx.match(
                    row["user_type"],
                    ("admin", "Admin"),
                    ("user", "User"),
                    row["user_type"],
                ),
                class_name=rx.cond(
                    row["user_type"] == "admin",
                    "inline-flex w-fit items-center gap-2 rounded-md border border-blue-800/15 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-800",
                    "inline-flex w-fit items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600",
                ),
            ),
            class_name="px-5 py-5",
        ),
        rx.el.td(
            row["created_at"],
            class_name="px-5 py-5 text-xs tabular-nums whitespace-nowrap text-[#64726f]",
        ),
        rx.el.td(
            row["updated_at"],
            class_name="px-5 py-5 text-xs tabular-nums whitespace-nowrap text-[#64726f]",
        ),
        on_click=RegistryState.toggle_row(row["id"]),
        aria_selected=RegistryState.selected_ids.contains(row["id"]),
        class_name=rx.cond(
            RegistryState.selected_ids.contains(row["id"]),
            "border-b border-blue-200 bg-blue-50 cursor-pointer transition-colors",
            "border-b border-[#e8e9e2] odd:bg-white even:bg-[#fcfcf9] hover:bg-[#f0f4ee] cursor-pointer transition-colors",
        ),
        key=row["id"],
    )


def empty_message(icon: str, title: str, detail: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-7 w-7 text-[#80938d] mb-4"),
        rx.el.h3(title, class_name="text-base font-semibold text-[#203440]"),
        rx.el.p(detail, class_name="text-sm text-[#72807b] mt-2"),
        class_name="flex flex-col items-center justify-center px-6 py-24 text-center",
    )


def registry_table() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.icon("list-checks", class_name="h-4 w-4 text-blue-800"),
                rx.el.span(
                    "Account entries", class_name="text-sm font-semibold"
                ),
                rx.el.span(
                    RegistryState.visible_accounts.length(),
                    class_name="rounded-md bg-[#eeefe8] px-2 py-0.5 text-xs tabular-nums text-[#61716c]",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.span(
                "Select a row or use its checkbox",
                class_name="hidden sm:block text-xs text-[#7c8781]",
            ),
            class_name="flex items-center justify-between border-b border-[#dfe3d9] px-5 py-5 text-[#203440]",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.caption(
                    "Account registry. All timestamps are in UTC.",
                    class_name="sr-only",
                ),
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            rx.el.input(
                                type="checkbox",
                                checked=RegistryState.all_selected,
                                on_change=lambda _: RegistryState.toggle_all(),
                                disabled=RegistryState.loading
                                | (
                                    RegistryState.visible_accounts.length() == 0
                                ),
                                aria_label="Select all visible accounts",
                                class_name=CHECKBOX,
                            ),
                            scope="col",
                            class_name="pl-5 pr-2 py-4 text-left",
                        ),
                        heading_cell("ID", "hash"),
                        heading_cell("Username", "user-round"),
                        heading_cell("Type", "shield"),
                        heading_cell("Created", "calendar"),
                        heading_cell("Updated", "clock-3"),
                        class_name="border-b border-[#dfe3d9] bg-[#f6f7f1]",
                    )
                ),
                rx.el.tbody(
                    rx.cond(
                        ~RegistryState.loading,
                        rx.foreach(RegistryState.visible_accounts, account_row),
                    )
                ),
                class_name="table-auto w-full min-w-[800px]",
            ),
            class_name="w-full overflow-x-auto",
        ),
        rx.cond(
            RegistryState.loading,
            rx.el.div(
                rx.icon(
                    "loader-circle",
                    class_name="h-5 w-5 animate-spin text-blue-700",
                ),
                rx.el.span("Loading account entries…"),
                role="status",
                class_name="flex items-center justify-center gap-3 py-24 text-sm text-[#61716c]",
            ),
            rx.cond(
                RegistryState.error != "",
                empty_message(
                    "cloud-off",
                    "Registry unavailable",
                    "Refresh to reconnect and load your accounts.",
                ),
                rx.cond(
                    RegistryState.accounts.length() == 0,
                    empty_message(
                        "book-open",
                        "No accounts yet",
                        "Existing accounts will appear here when they become available.",
                    ),
                    rx.cond(
                        RegistryState.visible_accounts.length() == 0,
                        rx.el.div(
                            empty_message(
                                "search",
                                "No matching accounts",
                                "Try another username or choose a different user type.",
                            ),
                            rx.el.button(
                                "Clear filters",
                                on_click=RegistryState.clear_filters,
                                class_name=BUTTON,
                            ),
                            class_name="pb-8 text-center",
                        ),
                    ),
                ),
            ),
        ),
        rx.el.div(
            rx.el.span(
                f"{RegistryState.visible_accounts.length()} visible / {RegistryState.accounts.length()} accounts"
            ),
            rx.el.span("Timestamps in UTC"),
            class_name="flex justify-between gap-4 border-t border-[#dfe3d9] bg-[#fafbf6] px-5 py-4 text-[11px] text-[#76827d]",
        ),
        aria_busy=RegistryState.loading,
        class_name="w-full overflow-hidden rounded-lg border border-[#d7ded3] bg-white",
    )


def registry() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("book-open-check", class_name="h-5 w-5 text-blue-800"),
                rx.el.span(
                    "ACCOUNT REGISTRY",
                    class_name="text-[11px] font-semibold tracking-[0.2em]",
                ),
                class_name="flex items-center gap-3 border-b border-[#d5dad0] pb-6 text-[#4e625c]",
            ),
            rx.el.header(
                rx.el.div(
                    rx.el.p(
                        "DIRECTORY / USER ENTRIES",
                        class_name="text-[10px] font-semibold tracking-[0.18em] text-[#829085] mb-3",
                    ),
                    rx.el.h1(
                        "The account ledger",
                        class_name="text-3xl sm:text-[40px] font-semibold tracking-tight leading-tight text-[#172e3b]",
                    ),
                    rx.el.p(
                        "Find, review, and select your user accounts.",
                        class_name="mt-3 text-sm text-[#6d7b74]",
                    ),
                ),
                rx.el.button(
                    rx.icon(
                        "refresh-cw",
                        class_name=rx.cond(
                            RegistryState.loading,
                            "h-3.5 w-3.5 animate-spin",
                            "h-3.5 w-3.5",
                        ),
                    ),
                    rx.cond(
                        RegistryState.loading, "Refreshing…", "Refresh records"
                    ),
                    on_click=RegistryState.load_accounts,
                    disabled=RegistryState.loading,
                    class_name=BUTTON,
                ),
                class_name="flex flex-wrap items-center justify-between gap-6 py-9",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-3 h-4 w-4 text-[#819087]",
                    ),
                    rx.el.input(
                        placeholder="Search by username…",
                        default_value=RegistryState.search,
                        on_change=RegistryState.set_search.debounce(250),
                        aria_label="Search by username",
                        class_name="h-10 w-full rounded-md border border-[#d7dcd1] bg-white pl-10 pr-4 text-sm text-[#233641] placeholder:text-[#929c94] focus-visible:outline-2 focus-visible:outline-blue-700",
                    ),
                    class_name="relative w-full sm:w-80",
                ),
                rx.el.div(
                    rx.el.span(
                        "User type", class_name="mr-2 text-xs text-[#718077]"
                    ),
                    rx.foreach(
                        ["All", "Admin", "User"],
                        lambda label: rx.el.button(
                            label,
                            on_click=RegistryState.set_user_type(label.lower()),
                            aria_pressed=RegistryState.user_type
                            == label.lower(),
                            class_name=rx.cond(
                                RegistryState.user_type == label.lower(),
                                "rounded-md bg-blue-900 px-4 py-2 text-xs font-medium text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700",
                                "rounded-md bg-transparent px-4 py-2 text-xs font-medium text-[#67796f] hover:bg-[#e8ede3] focus-visible:outline-2 focus-visible:outline-blue-700",
                            ),
                        ),
                    ),
                    class_name="flex items-center gap-1",
                ),
                class_name="mb-5 flex flex-wrap items-center justify-between gap-4",
            ),
            rx.cond(
                RegistryState.error != "",
                rx.el.div(
                    rx.icon("circle-alert", class_name="h-4 w-4 shrink-0"),
                    RegistryState.error,
                    role="alert",
                    class_name="mb-4 flex items-center gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("check-check", class_name="h-4 w-4 text-blue-700"),
                    rx.el.span(
                        f"{RegistryState.selected_ids.length()} selected",
                        class_name="font-medium text-blue-900",
                    ),
                    rx.el.button(
                        "Clear selection",
                        on_click=RegistryState.clear_selection,
                        disabled=RegistryState.selected_ids.length() == 0,
                        class_name="ml-3 text-xs text-[#6d7f73] underline underline-offset-4 hover:text-blue-800 disabled:opacity-35 focus-visible:outline-2 focus-visible:outline-blue-700",
                    ),
                    class_name="flex items-center gap-2 text-xs",
                ),
                rx.el.span(
                    rx.cond(
                        RegistryState.last_loaded != "",
                        f"Last refreshed {RegistryState.last_loaded}",
                        "Awaiting first refresh",
                    ),
                    class_name="text-[11px] text-[#849084]",
                ),
                aria_live="polite",
                class_name="mb-4 flex flex-wrap items-center justify-between gap-3",
            ),
            registry_table(),
            rx.el.footer(
                rx.icon("info", class_name="h-3.5 w-3.5 shrink-0"),
                "Selection applies only to visible results. Refreshing keeps accounts that still match.",
                class_name="mt-5 flex items-center gap-2 text-xs text-[#829084]",
            ),
            class_name="mx-auto w-full max-w-[1400px] px-5 py-8 sm:px-10 lg:px-14",
        ),
        class_name="min-h-dvh w-full bg-[#f7f7ee] font-['Inter'] text-[#203440]",
    )
