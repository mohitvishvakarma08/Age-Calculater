# UML Diagrams

The diagrams use Mermaid and can be rendered by Markdown viewers that support Mermaid.

## Use-case diagram

```mermaid
flowchart LR
    User((User))
    Calculate[Calculate age]
    Validate[Validate dates]
    View[View age and totals]
    History[Review calculation history]
    Export[Export report]
    User --> Calculate
    Calculate --> Validate
    Calculate --> View
    User --> History
    User --> Export
    Export --> PDF[PDF]
    Export --> XLSX[Excel]
    Export --> DOCX[Word]
    Export --> TXT[Text table]
```

## Class and component view

```mermaid
classDiagram
    class FlaskApp {
        +index()
        +calculate_route()
        +export_route()
    }
    class AgeCalculator {
        +calculate(birth, end)
        +predict_age_group(years)
        +parse_iso_date(value, field_name)
        +get_request_data()
    }
    class AgeGroupKNN {
        +fit(samples, labels)
        +predict(samples)
    }
    class BrowserClient {
        +validateDateField()
        +displayResult()
        +saveToHistory()
        +renderHistory()
        +getDownloadName()
    }
    class Exporters {
        +writeTextTable()
        +writeWorkbook()
        +writeDocument()
        +writePdfTable()
    }
    FlaskApp --> AgeCalculator
    AgeCalculator --> AgeGroupKNN
    FlaskApp --> Exporters
    BrowserClient --> FlaskApp
    BrowserClient --> BrowserStorage
    class BrowserStorage {
        +age-calculator-history
    }
```

## Sequence diagram: calculate and save history

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Flask as Flask API
    participant Calculator as Calculation logic
    participant Storage as localStorage

    User->>Browser: Enter name and dates
    Browser->>Browser: Validate dd/mm/yyyy
    User->>Browser: Select Calculate age
    Browser->>Flask: POST /api/calculate
    Flask->>Flask: Validate JSON and ISO dates
    Flask->>Calculator: calculate(birth, end)
    Calculator-->>Flask: Age result and totals
    Flask-->>Browser: JSON result
    Browser->>Storage: Save latest result
    Browser-->>User: Render result cards
```
