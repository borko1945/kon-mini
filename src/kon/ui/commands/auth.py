"""/login and /logout commands - provider OAuth flows."""

from __future__ import annotations

from ...llm import copilot_login, get_copilot_token
from ...llm import is_copilot_logged_in as has_saved_copilot_credentials
from ..chat import ChatLog
from ..floating_list import ListItem
from ..selection_mode import SelectionMode
from .base import CommandSupport


class AuthCommands(CommandSupport):
    def _handle_login_command(self, args: str) -> None:
        providers = [("github-copilot", "GitHub Copilot", has_saved_copilot_credentials())]

        self._show_selection_picker(
            [
                ListItem(
                    value=provider_id,
                    label=name,
                    description="saved credentials" if has_credentials else "",
                )
                for provider_id, name, has_credentials in providers
            ],
            SelectionMode.LOGIN,
        )

    def _select_login_provider(self, provider_id: str) -> None:
        if provider_id == "github-copilot":
            self.run_worker(self._copilot_login_flow(), exclusive=False)

    async def _copilot_login_flow(self) -> None:
        import webbrowser

        chat = self.query_one("#chat-log", ChatLog)
        had_saved_credentials = has_saved_copilot_credentials()

        def on_user_code(url: str, code: str) -> None:
            webbrowser.open(url)
            self.call_later(
                chat.add_info_message,
                f"Opening browser to: {url}\n"
                f"Enter this code: {code}\n\n"
                "Waiting for authorization...",
            )

        try:
            if await get_copilot_token():
                chat.add_info_message("Already logged in to GitHub Copilot")
                return

            if had_saved_credentials:
                chat.add_info_message(
                    "Your saved GitHub Copilot session is no longer valid.", warning=True
                )
            else:
                chat.add_info_message("Starting GitHub Copilot login...")

            await copilot_login(on_user_code=on_user_code)
            chat.add_info_message(
                "Successfully logged in to GitHub Copilot!\n"
                "You can now use /model to select Copilot models."
            )
        except Exception as e:
            chat.add_info_message(f"Login failed: {e}", error=True)

    def _handle_logout_command(self, args: str) -> None:
        providers = []
        if has_saved_copilot_credentials():
            providers.append(("github-copilot", "GitHub Copilot"))

        if not providers:
            chat = self.query_one("#chat-log", ChatLog)
            chat.add_info_message("No providers logged in")
            return

        self._show_selection_picker(
            [
                ListItem(value=provider_id, label=name, description="")
                for provider_id, name in providers
            ],
            SelectionMode.LOGOUT,
        )

    def _select_logout_provider(self, provider_id: str) -> None:
        from kon.llm import clear_copilot_credentials

        chat = self.query_one("#chat-log", ChatLog)

        if provider_id == "github-copilot":
            clear_copilot_credentials()
            chat.add_info_message("Logged out of GitHub Copilot")
