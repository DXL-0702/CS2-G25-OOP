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


def test_cli_invalid_number_input_reprompts_and_continues(monkeypatch, tmp_path, capsys):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "cash", "Cash Wallet", "cash", "not-a-number", "100", "USD", "6",
            "7",
        ],
    )

    output = capsys.readouterr().out
    assert "Please enter a valid number." in output
    assert system.get_account("cash").balance == 100


def test_cli_negative_account_balance_reports_business_error(monkeypatch, tmp_path, capsys):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "bad", "Bad Account", "cash", "-1", "USD", "6",
            "7",
        ],
    )

    output = capsys.readouterr().out
    assert "Business error" in output
    assert system.list_accounts() == []


def test_cli_insufficient_funds_expense_reports_business_error(monkeypatch, tmp_path, capsys):
    system = run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "1", "cash", "Cash Wallet", "cash", "100", "USD", "6",
            "2", "2", "tx-1", "150", "cash", "food", "Dinner", "9",
            "7",
        ],
    )

    output = capsys.readouterr().out
    assert "Business error" in output
    assert system.get_account("cash").balance == 100
    assert system.list_transactions() == []


def test_cli_missing_records_report_business_error_without_crashing(monkeypatch, tmp_path, capsys):
    run_cli_with_inputs(
        monkeypatch,
        tmp_path,
        [
            "1", "3", "missing-account", "6",
            "2", "5", "missing-transaction", "9",
            "7",
        ],
    )

    output = capsys.readouterr().out
    assert output.count("Business error") == 2
    assert "Goodbye." in output


def test_cli_empty_undo_reports_no_operation(monkeypatch, tmp_path, capsys):
    run_cli_with_inputs(monkeypatch, tmp_path, ["5", "7"])

    output = capsys.readouterr().out
    assert "No operation to undo." in output
    assert "Goodbye." in output
