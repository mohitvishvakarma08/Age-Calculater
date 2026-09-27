# User Workflow

```mermaid
flowchart TD
    Start([Open Age Calculator]) --> Input[Enter name and dates]
    Input --> ClientCheck{Browser input valid?}
    ClientCheck -- No --> Message[Show validation message]
    Message --> Input
    ClientCheck -- Yes --> Submit[Submit calculation]
    Submit --> ServerCheck{Server request valid?}
    ServerCheck -- No --> APIError[Show API error]
    APIError --> Input
    ServerCheck -- Yes --> Result[Show age, totals, and birthday details]
    Result --> History[Save to recent history]
    Result --> Choice{Next action}
    Choice -->|Click history item| Restore[Restore selected result]
    Restore --> Result
    Choice -->|Save result| Export[Choose PDF, Excel, Word, or Text]
    Export --> Download[Download named report]
    Choice -->|Clear| Input
    Choice -->|Clear history| EndHistory[Remove local history]
    Choice -->|Finish| End([End])
```

## Error paths

- Empty or malformed dates are rejected in the browser.
- Impossible calendar dates are rejected before submission.
- Missing or invalid JSON receives HTTP 400 from Flask.
- A calculation date before the birth date receives HTTP 400.
- Incomplete export data receives HTTP 400.
- Unsupported export formats receive HTTP 400.
