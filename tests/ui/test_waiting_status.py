from unittest.mock import AsyncMock, Mock

import pytest

from kon.events import ToolStartEvent
from kon.ui.agent_runner import AgentRunnerMixin
from kon.ui.app import Kon
from kon.ui.input import InputBox


class _RunnerHarness(AgentRunnerMixin):
    def __init__(self) -> None:
        self._stream_started = False
        self._current_block_type = None
        self._hide_thinking = False


@pytest.mark.asyncio
async def test_input_submission_sets_waiting_before_yield(monkeypatch) -> None:
    app = Mock()
    app._is_running = False
    app._run_agent = AsyncMock()
    status = Mock()
    chat = Mock()
    app.query_one.side_effect = lambda selector, _widget: (
        status if selector == "#status-line" else chat
    )

    async def assert_waiting_before_yield(_delay: float) -> None:
        status.set_status.assert_called_once_with("waiting")
        assert app._is_running is True
        chat.add_user_message.assert_not_called()

    monkeypatch.setattr("kon.ui.app.asyncio.sleep", assert_waiting_before_yield)

    await Kon.on_input_submitted(app, InputBox.Submitted("hello"))

    chat.add_user_message.assert_called_once_with("hello", highlighted_skill=None)
    app.run_worker.assert_called_once()
    app.run_worker.call_args.args[0].close()


@pytest.mark.asyncio
async def test_agent_initialization_failure_restores_idle_status() -> None:
    runner = _RunnerHarness()
    runner._is_running = True
    runner._runtime = Mock()
    runner._runtime.prepare_for_run.return_value = None
    runner._show_pending_update_notice_if_idle = Mock()
    chat = Mock()
    status = Mock()
    info_bar = Mock()
    widgets = {"#chat-log": chat, "#status-line": status, "#info-bar": info_bar}
    runner.query_one = lambda selector, _widget: widgets[selector]

    await runner._run_agent("hello")

    chat.add_info_message.assert_called_once_with("Agent not initialized")
    status.set_status.assert_called_once_with("idle")
    assert runner._is_running is False
    runner._show_pending_update_notice_if_idle.assert_called_once_with()


@pytest.mark.asyncio
async def test_tool_start_promotes_waiting_status() -> None:
    runner = _RunnerHarness()
    chat = Mock()
    status = Mock()

    await runner._render_agent_event(
        ToolStartEvent(tool_call_id="call-1", tool_name="unknown"), chat, status, Mock()
    )

    status.set_status.assert_called_once_with("working")
    assert runner._stream_started is True
    chat.start_tool.assert_called_once_with("unknown", "call-1", "", icon="→")
