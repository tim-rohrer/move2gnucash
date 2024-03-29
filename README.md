# _Move2GnuCash_

Uses csv-exported from apps, initially Quicken, to create a GnuCash book. CSV data is preferred because it is more common than QIF or OFX/QFX, at least with Quicken for Mac.

## Credits

Although this is a complete new app, `csv2cash` was used to study approach to the problem. If it weren't for a few shortcomings (most related to features needed for my Quicken data), `csv2cash` would have likely been sufficient.

One area _Move2GnuCash_ will attempt to diverge from `csv2cash` is that the existing account and category names will be used to map to top-level accounts (Income, Expense, etc). If realized, this would preclude the end user from having to create a translation file to make these identifications. However, it does mean the end user needs to get their data in the desired form inside of Quicken.

## Dependencies

-   PieCash
-   Pandas

## Limitations

Due to Quicken's manner of exporting data, account balances and categories need to be in place in the GnuCash book prior to the import of transactions. While this can be done manually (you still need to make them match what is coming out of Quicken!), _Move2GnuCash_ has options for importing these through two processes described below.

The challenges are exacerbated by limitations with Quicken's export of _All Transactions_ because we cannot group all non-investment accounts together into one export file. It becomes easier to export all transactions as one file and then let _Move2GnuCash_ divide the data into investment and non-investment transactions for processing.

_Move2GnuCash_ assumes all investment transaction history (in support of cost basis tracking) is present in the file even if non-investment transactions are limited to recent history (i.e., the chosen date for account balances described below). The implication is that non-investment transactions prior to th opening balances date will be filtered out while investment transactions will be retained.

## Exports from Quicken

_Move2GnuCash_ requires a minimum of two files from Quicken for each import process. Because exported CSV files from Quicken contain a varying number of extraneous lines and comments, these will have to be edited to get to final form.

### Account Balances

Pick a date to mark the beginning of which Quicken transactions you wish to migrate. GnuCash wants to have the Opening Balances as of that date for each account. For example, I conducted my migration using two runs, the first being for non-investing accounts, and the second for investing accounts. Each process had different start dates.

With non-investment accounts, I chose 1 January 2017 as the start date, and so I created a balances file by exporting to CSV a Quicken Net Worth report containing all accounts I was transferring except Investment accounts.

**See `sample_balances_user.csv` for how to format an input file for this first of _move2gnucash_**. A future version might see more automated file handling.

~~I then removed the top header lines (except the date), moved the labels from the first column to the second column, and removed the the other unnecessary formatting lines. In the end, the format of your file should look like this sample:~~

~~
| | Accounts | 12/31/2016 |
| ------------------- | -------- | ---------- |
| Assets | |
| Cash | |
| - Cash | 77.12 |
| - Checking One | 440.84 |
| - Checking Two | 235.38 |
| - Total Cash | 753.34 |
| Savings | |
| - Spouse Savings | 987.12 |
| - Family Savings | 3250 |
| - Total Savings | 4237.12 |
| Property | |
| - 2012 Silverado | 30975 |
| - 2012 Camper | 0 |
| - Total Property | 39975 |
| Total Assets | 44965.46 |
| Liabilities | |
| Credit Card | |
| - Apple Card | 0 |
| - Credit Card | -973.4 |
| - Total Credit Card | -973.4 |
| Loan | |
| - Student Loan | -10500 |
| - Total Loan | -10650 |
| Total Liabilities | -11623 | |
~~

_Move2GnuCash_ function `opening_book` retrieves the date (balances as of close of business) from the first line. The second line, because it has no associated figure in the second column, will be created as a [placeholder account](https://www.gnucash.org/docs/v4/C/gnucash-help/acct-create.html#accts-placeholder) and will be the parent of the next account created, and so on, until the accounts containing transactions are created (the hyphens will be removed).

The above list of balances will result in an initial [Chart of Accounts](https://www.gnucash.org/docs/v4/C/gnucash-help/chart-create.html) shown here in this figure.

The `opening_book` function will also create an **Equity** account with a sub-account of **Opening Balances**. This account will be used for the second entry required when an opening balance is recorded in an account. Note that balance equals the sum of the assets and liabilities recorded during the import.

Before running `opening_book`, you may want to use the opening balances file to adjust the account structure. For example, GnuCash typically uses **Current Assets**, **Fixed Assets** and **Investments** as sub-accounts under **Assets**.

If you do change these, make sure to also change the _Total_ line in the file because that is how _Move2GnuCash_ knows when to jump back up the account tree.

Let's say we want to change _Cash_ to _Current Assets_, the total line should then read _Total Current Assets_. Each placeholder account requires a total line. Please note, the numeric value associated with the total line is ignored, so feel free to remove those. As another example, the _Assets_ section could be reworked:

| Accounts                  | 12/31/2016 |
| ------------------------- | ---------- |
| Assets                    |            |
| Current Assets            |            |
| - Cash                    | 77.12      |
| - Total Cash              |            |
| Checking Accounts         |            |
| - Checking One            | 440.84     |
| - Checking Two            | 235.38     |
| - Total Checking Accounts |            |
| Savings                   |            |
| - Spouse Savings          | 987.12     |
| - Family Savings          | 3250       |
| - Total Savings           |            |
| Total Current Assets      |            |
| Fixed Assets              |            |
| - 2012 Silverado          | 30975      |
| - 2012 Camper             | 0          |
| - Total Fixed Assets      | 39975      |
| Total Assets              | 44965.46   |

### Transaction Data

Again, Quicken (and perhaps other personal finance programs) will export extraneous data that must be removed. The csv file(s) will need to be cleaned up prior to use.

TODO: Finish this documenting.

## Regarding the term: "Splits"

GnuCash uses [double entry accounting](https://www.investopedia.com/terms/d/double-entry.asp). PieCash uses the term splits to refer to these particulars in a [transaction](https://piecash.readthedocs.io/en/master/tutorial/index_new.html#creating-a-new-transaction), which can be confusing for those used to Quicken, and perhaps Mint.

_Move2GnuCash_ will map CSV entries to account for splits by creating multi-split transactions for GnuCash.

For example, consider this csv file which would reflect an expense in Quicken where \$11.50 is charged to the Dining category and \$0.95 reflects the sales tax charged by the state:

| Split | Date       | Type            | Payee/Security  | Category  | Amount | Account        |
| ----- | ---------- | --------------- | --------------- | --------- | ------ | -------------- |
| S     | 01/22/2023 | Payment/Deposit | Breakfast Place | Dining    | -10.55 | My Credit Card |
| S     | 01/22/2023 | Payment/Deposit | Breakfast Place | Sales Tax | -0.95  | My Credit Card |

GnuCash treats categories as just another account. When the transaction is created by _Move2GnuCash_/PieCash, it will include three splits in order to capture the changes to all three accounts. Extending the idea presented in the PieCash tutorial examples, it might look like this:

```python
trans1 = Transaction(
    currency=usd,
    description="Breakfast Place",
    splits=[
        Split(value=Decimal("-11.50"), account="My Credit Card"),
        Split(value=Decimal("10.55"), account="Dining"),
        Split(value=Decimal("0.95"), account="Sales Tax")
    ],
)
```

In a double entry accounting system, the debits and credits must balance.

## Regarding Memos, Notes and Tags

_Move2GnuCash_ captures as much of these three fields as possible, but limitations in Quicken's exporter and GnuCash may result in data loss depending on how you record these in your own system.

GnuCash has a `notes` field with each transaction and a `memo` field for each split. There is no support for tags. To capture the tags, we combine these with a split's `memo`.

Quicken's exporter overwrites an empty split memo/notes field with the contents of the transaction's notes; if the split memo/note is not empty, the transaction note is not applied. The implication is that if all split memos have data, any transaction level note or member will not be exported, and will not migrate to GnuCash.

## Initial To-Do

-   [x] Read generic csv file contents into a Pandas DataFrame.

-   [x] Create GnuCash book with accounts and opening balances transaction fixtures.
    -   [x] Write account list to file.
    -   [x] Write transactions list to file.
-   [x] Map Opening Balances (Net Worth) DataFrame to:
    -   [x] Accounts list.
    -   [x] Opening Balances transactions list
-   [x] Module to prepare transactions for addition to GnuCash book.
    -   [x] Create Note/Memos field based on existing notes and tags.
    -   [x] Identify Quicken split transaction.
-   [ ] Final processing and writing of info to GnuCash.
    -   [ ] Accounts from categories.
    -   [ ] Summary of import.
