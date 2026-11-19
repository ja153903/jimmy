# Functional composition examples

Each rule in [Functional Composition](../SKILL.md) gets one example of what to avoid and what to do instead. The orchestrator and pipeline rules are covered by the `syncInvoices` example in [TypeScript patterns](../../typescript-best-practices/references/patterns.md#composition), so this file starts with the other rules and then shows the same shape in Python and in a React hook.

## Return new values

Return a new value instead of changing the argument. A caller that still holds the original should not see it change.

```ts
// Don't: the caller's cart changes under them
function applyDiscount(cart: Cart, percent: number): void {
  for (const line of cart.lines) {
    line.cents = Math.round(line.cents * (1 - percent / 100));
  }
}

// Do: return a new cart and leave the input alone
const applyDiscount = (cart: Cart, percent: number): Cart => ({
  ...cart,
  lines: cart.lines.map((line) => ({ ...line, cents: Math.round(line.cents * (1 - percent / 100)) })),
});
```

Mutation is fine when it stays inside the function and nothing else can see it. Here the array is created, filled, and returned, and no other code holds a reference to it while it changes:

```ts
// Fine: `tokens` is local, and pushing is cheaper than rebuilding it for every character
function tokenize(source: string): Token[] {
  const tokens: Token[] = [];
  for (let i = 0; i < source.length; i += 1) {
    // ...push into tokens
  }
  return tokens;
}
```

## Explicit inputs

Pass a transformation everything it reads. Hidden reads of the clock, config, or module state make the result depend on things the call site can't see, and make tests reach for mocks.

```ts
// Don't: depends on the wall clock and a module-level config object
function isOverdue(invoice: Invoice): boolean {
  return Date.now() - invoice.dueAt.getTime() > config.graceDays * DAY_MS;
}

// Do: the caller passes the time and the grace period
const isOverdue = (invoice: Invoice, now: Date, graceDays: number): boolean =>
  now.getTime() - invoice.dueAt.getTime() > graceDays * DAY_MS;

// The entry point does the effectful reads and passes them in
const overdue = invoices.filter((invoice) => isOverdue(invoice, new Date(), settings.graceDays));
```

## Modules by responsibility

Extract a shared piece when a second feature needs it, or earlier if naming it makes the step clearer. Put it in a module named for what it does, and export only what callers use.

```ts
// Don't: the receipt and the invoice email each format money in their own way
const receiptTotal = `$${(cents / 100).toFixed(2)}`;
const emailTotal = "$" + (total / 100).toLocaleString("en-US", { minimumFractionDigits: 2 });

// Do: one module, one export, imported by both features
// money.ts
export const formatCents = (cents: Cents, currency: CurrencyCode): string =>
  new Intl.NumberFormat("en-US", { style: "currency", currency }).format(cents / 100);
```

Don't create `utils.ts` or `helpers.ts`. A module's name says what it is responsible for, and a module that would only hold a single caller's code stays inline in that caller.

## Where to stop

Composition is meant to make code easier to read. A layer that only forwards a call, or a chain that hides what flows through it, makes it harder to read.

```ts
// Don't: a wrapper that adds a name and nothing else
const getUser = (id: UserId) => fetchUser(id);

// Don't: a point-free chain where the reader has to work out each value's type
const billable = pipe(prop("invoices"), filter(complement(propEq("void", "status"))), map(pick(["id", "total"])));

// Do: name the step that has meaning and write the rest out
const billable = account.invoices.filter(isBillable).map(toInvoiceRow);
```

If a named function's body is shorter than its name and is only called once, inline it.

## Python

Use the same shape in Python: comprehensions or generators for the pipeline, and frozen dataclasses for the values it returns.

```python
# Don't: one function fetches, filters, converts, writes, and prints
def sync_invoices(account_id: str) -> None:
    rows = []
    for inv in requests.get(f"{API}/accounts/{account_id}/invoices").json():
        if inv["status"] != "void" and inv["total"] > 0:
            rows.append((inv["id"], round(inv["total"] * 100)))
    db.executemany("INSERT INTO invoice_rows VALUES (?, ?)", rows)
    print("synced", len(rows))


# Do: the orchestrator lists the steps, and each step is testable on its own
@dataclass(frozen=True)
class InvoiceRow:
    id: str
    cents: int


def is_billable(inv: Invoice) -> bool:
    return inv.status != "void" and inv.total > 0


def to_invoice_row(inv: Invoice) -> InvoiceRow:
    return InvoiceRow(id=inv.id, cents=round(inv.total * 100))


def sync_invoices(account_id: AccountId, client: Client, db: Connection) -> None:
    invoices = fetch_invoices(client, account_id)  # request + parse at the boundary
    rows = [to_invoice_row(inv) for inv in invoices if is_billable(inv)]  # pure pipeline
    save_invoice_rows(db, rows)  # effect
    logger.info("invoices.synced", extra={"account_id": account_id, "count": len(rows)})
```

## React hooks

The hook is the orchestrator. It reads state, checks gates, owns the dependency array, and calls the named request and transformation functions. The pure transformation can then be tested without rendering anything.

```ts
// Don't: fetch, filter, map, and logging all happen inside the effect
useEffect(() => {
  fetch(`/api/accounts/${accountId}/invoices`)
    .then((res) => res.json())
    .then((raw) => setRows(raw.filter((i: any) => i.status !== "void").map((i: any) => ({ id: i.id, cents: i.total * 100 }))));
}, [accountId]);

// Do: the effect lists the steps, and every helper takes explicit arguments
function useInvoiceRows(accountId: AccountId | undefined): InvoiceRow[] {
  const [rows, setRows] = useState<InvoiceRow[]>([]);

  useEffect(() => {
    if (accountId === undefined) return; // gate
    const controller = new AbortController();
    fetchInvoices(accountId, controller.signal) // request + parse at the boundary
      .then((invoices) => setRows(invoices.filter(isBillable).map(toInvoiceRow))) // pure pipeline
      .catch(ignoreAbort);
    return () => controller.abort();
  }, [accountId]);

  return rows;
}
```
