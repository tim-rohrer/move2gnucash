"""test_opening_balances.py"""

from datetime import datetime
from unittest.mock import patch

from piecash import Book, create_book

from move2gnucash.migrations import category_accounts, opening_balances, transactions


@patch("move2gnucash.migrations.fetch_accounts")
def test_opening_balances(mock_fetch, balances) -> None:
    """
    GIVEN a file name referencing an opening balances CSV and a PieCash
        Book instance,
    WHEN executed by opening_balances,
    THEN accounts (generally assets and liabilities, and Equity:Opening Balances)
        along with their opening balances.
    """
    test_date = datetime.strptime("2017_12_31", "%Y_%m_%d").date()
    mock_fetch.return_value = {
        "as_of_date": test_date,
        "data": balances,
    }
    book: Book = create_book(currency="USD")

    opening_balances("2016-12-31_testfile.csv", book)

    assert (
        len(book.accounts) == 23
    )  # Account from balances fixture plus Equity and Equity:Opening Balances
    root = book.root_account
    root_accts = {i.name: i for i in root.children}
    assets_bal = root_accts["Assets"].get_balance()
    liabilities_bal = root_accts["Liabilities"].get_balance()
    equity_bal = root_accts["Equity"].get_balance()
    assert assets_bal == liabilities_bal + equity_bal
    assert assets_bal > 0

    for tr in book.transactions:
        assert tr.post_date == test_date

    book.close()


@patch("move2gnucash.migrations.fetch_categories")
def test_category_accounts(mock_fetch, categories) -> None:
    """
    GIVEN a file name referencing a CSV containing a list of categories,
        and a PieCash Book instance,
    WHEN executed by category_accounts,
    THEN accounts representing income and expense categories will be added
        to the GnuCash book.
    """
    mock_fetch.return_value = categories
    book: Book = create_book(currency="USD")

    category_accounts("categories.csv", book)

    assert len(book.accounts[0].children) == 4
    types: list = [acc.type for acc in book.accounts]
    assert types.count("INCOME") == 7
    assert types.count("EXPENSE") == 17

    book.close()


@patch("move2gnucash.migrations.fetch_csv_data")
def test_transactions(mock_fetch, detailed_book, all_transactions) -> None:
    """
    GIVEN a file name referencing a CSV containing a list of transactions,
        a transaction type, and a PieCash Book instance with necessary
        accounts in place,
    WHEN executed by transactions,
    THEN double entry transactions will be added to the GnuCash book.
    """
    mock_fetch.return_value = all_transactions

    book = detailed_book

    transactions("transactions.csv", book)

    assert len(book.transactions) == 7
