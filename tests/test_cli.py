from src.cli import run_cli
from src.managers.finance_system import FinanceSystem
from src.storage.json_storage import JsonStorage


def run_cli_with_inputs(monkeypatch, tmp_path, inputs):
    system = FinanceSystem(JsonStorage(tmp_path / "system_state.json"))
    iterator = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(iterator))
    run_cli(system)
    return system


def test_cli_save_and_exit(monkeypatch, tmp_path, capsys):
    run_cli_with_inputs(monkeypatch, tmp_path, ["7"])

    output = capsys.readouterr().out
    assert "Save system completed." in output
    assert "Goodbye." in output


def test_cli_invalid_main_menu_option_does_not_crash(monkeypatch, tmp_path, capsys):
    run_cli_with_inputs(monkeypatch, tmp_path, ["invalid", "7"])

    output = capsys.readouterr().out
    assert "Invalid option" in output
    assert "Goodbye." in output


def test_cli_create_account_from_menu(monkeypatch, tmp_path, capsys):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1",
            "1",
            "cash",
            "Cash Wallet",
            "cash",
            "100",
            "USD",
            "6",
            "7",
        ],
    )

    assert system.get_account("cash").balance == 100
    assert "Create account completed." in capsys.readouterr().out


def test_cli_add_income_transaction_from_menu(monkeypatch, tmp_path):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "cash", "Cash Wallet", "cash", "100", "USD", "6",
            "2", "1", "tx-1", "50", "cash", "salary", "Monthly salary", "9",
            "7",
        ],
    )

    assert system.get_account("cash").balance == 150
    assert system.get_transaction("tx-1").amount == 50


def test_cli_audit_validation_menu(monkeypatch, tmp_path, capsys):
    run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "cash", "Cash Wallet", "cash", "100", "USD", "6",
            "6", "2", "3",
            "7",
        ],
    )

    output = capsys.readouterr().out
    assert "Audit chain valid: True" in output


def test_cli_pending_process_and_undo_smoke(monkeypatch, tmp_path):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "cash", "Cash Wallet", "cash", "100", "USD", "6",
            "4", "2", "tx-1", "40", "cash", "food", "Dinner", "5", "6",
            "5",
            "7",
        ],
    )

    assert system.get_account("cash").balance == 100
