from src.exceptions import FinanceError
from src.managers.finance_system import FinanceSystem


PROJECT_NAME = "Personal Finance and Digital Asset Management System"
PROJECT_SUBTITLE = "Blockchain-style Audit Ledger"


def show_welcome():
    print("=" * 72)
    print(PROJECT_NAME)
    print(PROJECT_SUBTITLE)
    print("=" * 72)


def run_cli(system=None):
    system = system or FinanceSystem()
    show_welcome()
    try:
        system.load()
        print("System state loaded.")
    except FinanceError as error:
        print(f"Could not load saved state: {error}")
        print("Starting with an empty system.")

    while True:
        choice = choose_menu(
            "Main Menu",
            [
                "Account Management",
                "Transaction Management",
                "Category and Budget",
                "Pending Transactions",
                "Undo Last Operation",
                "Audit Ledger",
                "Save and Exit",
            ],
        )
        if choice == "1":
            account_menu(system)
        elif choice == "2":
            transaction_menu(system)
        elif choice == "3":
            category_budget_menu(system)
        elif choice == "4":
            pending_menu(system)
        elif choice == "5":
            run_action("Undo last operation", lambda: undo_last(system))
        elif choice == "6":
            audit_menu(system)
        elif choice == "7":
            run_action("Save system", system.save)
            print("Goodbye.")
            break


def choose_menu(title, options):
    while True:
        print()
        print(title)
        print("-" * 72)
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")
        choice = input("Choose an option: ").strip()
        if choice in {str(index) for index in range(1, len(options) + 1)}:
            return choice
        print("Invalid option. Please try again.")


def prompt_text(label, allow_empty=False):
    while True:
        value = input(f"{label}: ").strip()
        if value or allow_empty:
            return value
        print("This field cannot be empty.")


def prompt_float(label, allow_empty=False):
    while True:
        value = input(f"{label}: ").strip()
        if allow_empty and value == "":
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def prompt_optional_text(label):
    value = prompt_text(f"{label} (blank to skip)", allow_empty=True)
    return None if value == "" else value


def prompt_optional_float(label):
    return prompt_float(f"{label} (blank to skip)", allow_empty=True)


def run_action(label, action):
    try:
        result = action()
        if result is not None:
            print_result(result)
        print(f"{label} completed.")
        return result
    except FinanceError as error:
        print(f"Business error: {error}")
    except ValueError as error:
        print(f"Input error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")
    return None


def account_menu(system):
    while True:
        choice = choose_menu(
            "Account Management",
            ["Create account", "List accounts", "View account", "Update account", "Delete account", "Back"],
        )
        if choice == "1":
            run_action("Create account", lambda: system.create_account(
                prompt_text("Account ID"),
                prompt_text("Name"),
                prompt_text("Account type"),
                prompt_float("Initial balance"),
                prompt_text("Currency", allow_empty=True) or "USD",
            ))
        elif choice == "2":
            print_items(system.list_accounts())
        elif choice == "3":
            run_action("View account", lambda: system.get_account(prompt_text("Account ID")))
        elif choice == "4":
            account_id = prompt_text("Account ID")
            run_action("Update account", lambda: system.update_account(
                account_id,
                name=prompt_optional_text("New name"),
                account_type=prompt_optional_text("New account type"),
                balance=prompt_optional_float("New balance"),
                currency=prompt_optional_text("New currency"),
            ))
        elif choice == "5":
            run_action("Delete account", lambda: system.delete_account(prompt_text("Account ID")))
        elif choice == "6":
            return


def transaction_menu(system):
    while True:
        choice = choose_menu(
            "Transaction Management",
            [
                "Add income",
                "Add expense",
                "Add transfer",
                "List transactions",
                "View transaction",
                "Update transaction",
                "Delete transaction",
                "Search by amount range",
                "Back",
            ],
        )
        if choice == "1":
            run_action("Add income", lambda: system.add_income_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "2":
            run_action("Add expense", lambda: system.add_expense_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "3":
            run_action("Add transfer", lambda: system.add_transfer_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Source account ID"),
                prompt_text("Target account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "4":
            print_items(system.list_transactions())
        elif choice == "5":
            run_action("View transaction", lambda: system.get_transaction(prompt_text("Transaction ID")))
        elif choice == "6":
            transaction_id = prompt_text("Transaction ID")
            run_action("Update transaction", lambda: system.update_transaction(
                transaction_id,
                amount=prompt_optional_float("New amount"),
                category=prompt_optional_text("New category ID"),
                description=prompt_optional_text("New description"),
                account_id=prompt_optional_text("New account ID"),
                source_account_id=prompt_optional_text("New source account ID"),
                target_account_id=prompt_optional_text("New target account ID"),
            ))
        elif choice == "7":
            run_action("Delete transaction", lambda: system.delete_transaction(prompt_text("Transaction ID")))
        elif choice == "8":
            run_action("Search transactions", lambda: print_items(system.search_transactions_by_amount(
                prompt_float("Minimum amount"),
                prompt_float("Maximum amount"),
            )))
        elif choice == "9":
            return


def category_budget_menu(system):
    while True:
        choice = choose_menu(
            "Category and Budget",
            ["Create category", "List categories", "Create budget", "List budgets", "Calculate category spending", "Back"],
        )
        if choice == "1":
            parent_id = prompt_optional_text("Parent category ID")
            run_action("Create category", lambda: system.create_category(
                prompt_text("Category ID"),
                prompt_text("Name"),
                parent_id=parent_id,
            ))
        elif choice == "2":
            print_items(system.list_categories())
        elif choice == "3":
            run_action("Create budget", lambda: system.create_budget(
                prompt_text("Budget ID"),
                prompt_text("Category ID"),
                prompt_text("Period"),
                prompt_float("Limit amount"),
                prompt_float("Spent amount"),
            ))
        elif choice == "4":
            print_items(system.list_budgets())
        elif choice == "5":
            category_id = prompt_text("Category ID")
            total = run_action("Calculate category spending", lambda: system.calculate_category_spending(category_id))
            if total is not None:
                print(f"Total spending: {total}")
        elif choice == "6":
            return


def pending_menu(system):
    while True:
        choice = choose_menu(
            "Pending Transactions",
            ["Add pending income", "Add pending expense", "Add pending transfer", "List pending", "Process next", "Back"],
        )
        if choice == "1":
            run_action("Add pending income", lambda: system.create_pending_income_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "2":
            run_action("Add pending expense", lambda: system.create_pending_expense_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "3":
            run_action("Add pending transfer", lambda: system.create_pending_transfer_transaction(
                prompt_text("Transaction ID"),
                prompt_float("Amount"),
                prompt_text("Source account ID"),
                prompt_text("Target account ID"),
                prompt_text("Category ID"),
                prompt_text("Description", allow_empty=True),
            ))
        elif choice == "4":
            print_items(system.list_pending_transactions())
        elif choice == "5":
            run_action("Process next pending transaction", system.process_next_pending)
        elif choice == "6":
            return


def audit_menu(system):
    while True:
        choice = choose_menu("Audit Ledger", ["List audit blocks", "Validate audit chain", "Back"])
        if choice == "1":
            print_items(system.list_audit_blocks())
        elif choice == "2":
            print(f"Audit chain valid: {system.validate_audit_chain()}")
        elif choice == "3":
            return


def undo_last(system):
    transaction = system.undo_last()
    if transaction is None:
        print("No operation to undo.")
    return transaction


def print_items(items):
    items = list(items)
    if not items:
        print("No records.")
        return items
    for item in items:
        print_result(item)
    return items


def print_result(result):
    if hasattr(result, "to_dict"):
        print(result.to_dict())
    else:
        print(result)
