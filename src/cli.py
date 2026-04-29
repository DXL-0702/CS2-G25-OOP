PROJECT_NAME = "Personal Finance and Digital Asset Management System"
PROJECT_SUBTITLE = "Blockchain-style Audit Ledger"


PLACEHOLDER_MENU_ITEMS = [
    "1. Account Management        (planned in later issues)",
    "2. Transaction Management    (planned in later issues)",
    "3. Category and Budget       (planned in later issues)",
    "4. Pending Transactions      (planned in later issues)",
    "5. Undo Last Operation       (planned in later issues)",
    "6. Audit Ledger              (planned in later issues)",
    "7. Save and Exit             (planned in later issues)",
]


def show_welcome():
    print("=" * 72)
    print(PROJECT_NAME)
    print(PROJECT_SUBTITLE)
    print("=" * 72)
    print("Current stage: Phase 0 project skeleton")
    print("Core business features will be implemented in later issues.")
    print()


def show_main_menu():
    print("Main Menu Preview")
    print("-" * 72)
    for item in PLACEHOLDER_MENU_ITEMS:
        print(item)
    print("-" * 72)


def run_cli():
    show_welcome()
    show_main_menu()
