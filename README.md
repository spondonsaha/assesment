# Automation Testing Assessment

Automated **UI** (SauceDemo) and **API** (ReqRes) test suites built with **Python + Selenium + pytest + requests**, complete with **Allure / HTML reports** and a **Postman collection** runnable from the command line via **Newman**.

---

## 1. Tech stack

| Area      | Tooling                                                        |
|-----------|----------------------------------------------------------------|
| Language  | Python 3.10+                                                   |
| UI        | Selenium 4 (Chrome/Edge, Selenium Manager auto-provisions the driver) |
| API       | `requests` + the ReqRes public API (`https://reqres.in/api`)   |
| Test runner | pytest                                                      |
| Reporting | Allure (`allure-pytest`) **and** self-contained HTML (`pytest-html`) |
| API (CLI) | Postman collection + environment executed with Newman          |

---

## 2. Project structure

```
Assesment/
├── config/settings.py                 # URLs, credentials, expected data, timeouts
├── conftest.py                        # pytest options (--headed/--browser), failure screenshots
├── pytest.ini                         # testpaths, markers
├── run_tests.py                       # sequential runner: separate + combined runs + reports
├── requirements.txt
├── ui/                                # Selenium UI suite (Page Object Model)
│   ├── conftest.py                    # WebDriver fixture
│   ├── pages/                         # base, login, inventory, cart, checkout
│   └── tests/
│       ├── test_q1_locked_out_user.py
│       ├── test_q2_standard_user.py
│       └── test_q3_performance_glitch_user.py
├── api/                               # ReqRes API suite
│   ├── api_client.py                  # requests wrapper with mandatory status assertions
│   ├── auth.py                        # login + authToken capture
│   ├── conftest.py                    # client + shared store fixtures
│   ├── tests/
│   │   ├── test_q3_login_token.py
│   │   ├── test_q4_get_user.py
│   │   ├── test_q5_put_profile.py
│   │   ├── test_q6_patch_field.py
│   │   └── test_q8_bad_requests.py
│   └── postman/
│       ├── ReqRes_API.postman_collection.json
│       └── ReqRes.postman_environment.json
└── utils/assertions.py                # status-code + timestamp assertion helpers
```

---

## 3. Prerequisites

* **Python 3.10+**
* **Google Chrome** (or Microsoft Edge) installed
* **Node.js** (only for running the Postman collection with Newman)
* **Allure CLI** (optional, for the Allure report) — the HTML report always works without it
* **Java 8+** (only required by the Allure CLI)

---

## 4. Setup

```powershell
# From the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Optional: Allure CLI (for the Allure HTML report)
npm install -g allure-commandline
```

---

## 5. Running the UI tests (Selenium)

The three UI scenarios can be run **individually** or **all together, sequentially**.

```powershell
# --- individually ---
python -m pytest ui/tests/test_q1_locked_out_user.py --alluredir=allure-results/q1 --html=reports/html/q1-report.html --self-contained-html
python -m pytest ui/tests/test_q2_standard_user.py  --alluredir=allure-results/q2 --html=reports/html/q2-report.html --self-contained-html
python -m pytest ui/tests/test_q3_performance_glitch_user.py --alluredir=allure-results/q3 --html=reports/html/q3-report.html --self-contained-html

# --- all three, sequentially in one run ---
python -m pytest ui/tests --alluredir=allure-results/ui --html=reports/html/ui-report.html --self-contained-html
```

Options:

* Default is **headless**. Add `--headed` to watch the browser.
* Choose the browser with `--browser chrome` (default) or `--browser edge`.

```powershell
python -m pytest ui/tests --headed --browser edge
```

---

## 6. Running the API tests (Python)

```powershell
python -m pytest api/tests --alluredir=allure-results/api --html=reports/html/api-report.html --self-contained-html
```

### ReqRes rate limit (important)

The ReqRes **anonymous demo** allows only **40 requests/day per IP**. If that
limit is reached, requests return `429 rate_limit_exceeded`. To keep runs
reliable:

* **Recommended:** create a free key at <https://app.reqres.in> and export it:

  ```powershell
  $env:REQRES_API_KEY = "your-free-key"
  python -m pytest api/tests ...
  ```

  When set, the key is sent as the `x-api-key` header on every request.

* If you run without a key and hit the limit, the suite **skips** the affected
  tests with a clear message instead of failing:

  ```
  SKIPPED ... ReqRes anonymous demo limit reached (429 - 40 requests/day per IP)...
  ```

* Force a hard failure instead of a skip:

  ```powershell
  $env:REQRES_ON_RATE_LIMIT = "fail"
  ```

---

## 7. Run everything sequentially + generate reports (`run_tests.py`)

`run_tests.py` runs each scenario on its own and then all of them together,
producing **both** an Allure report and a self-contained HTML report after
every execution.

```powershell
python run_tests.py                     # q1, q2, q3, api, then all-together
python run_tests.py --stages q1,q2      # only the chosen stages
python run_tests.py --stages all        # UI + API in one sequential execution
python run_tests.py --headed            # watch the browser
python run_tests.py --no-allure-report  # skip `allure generate` (HTML still generated)
```

Stage names: `q1`, `q2`, `q3`, `api`, `all`.

### Where the reports land

```
reports/
├── html/               # <stage>-report.html  (self-contained, open in any browser)
└── allure-report/      # <stage>/index.html   (generated when the Allure CLI is installed)
allure-results/         # raw Allure data per stage
```

Open a report directly, or serve the Allure results:

```powershell
allure serve allure-results/q1
```

---

## 8. Postman collection + Newman (API)

The collection chains requests and asserts status codes on **every** request.
The **authToken** captured by the login request is stored and reused.

```powershell
# Install Newman once
npm install -g newman

# Run the collection from the command line
newman run api/postman/ReqRes_API.postman_collection.json -e api/postman/ReqRes.postman_environment.json
```

Add reporters if you like:

```powershell
newman run api/postman/ReqRes_API.postman_collection.json -e api/postman/ReqRes.postman_environment.json -r cli,html --reporter-html-export reports/html/newman-report.html
```

> Note: the Postman collection also hits the shared ReqRes demo quota. Set the
> `REQRES_API_KEY` environment variable in the Postman environment file (key
> `apiKey`, header `x-api-key`) if you have a key.

---

## 9. Scenario → requirement mapping

### UI (`https://www.saucedemo.com/`)

| Test | Mark | What it verifies |
|------|------|------------------|
| `test_q1_locked_out_user.py` | 10 | Login with `locked_out_user` shows the lock-out error |
| `test_q2_standard_user.py` | 20 | `standard_user`: reset app state → add 3 items → checkout → verify product names + total price → finish → success message → reset → logout |
| `test_q3_performance_glitch_user.py` | 10 | `performance_glitch_user`: reset → filter Name (Z→A) → add first product → checkout → verify names + total → finish → success message → reset → logout |

### API (`https://reqres.in/api`)

| Test | Mark | What it verifies |
|------|------|------------------|
| `test_q3_login_token.py` | 10 | `POST /login` → 200, captures `authToken` |
| `test_q4_get_user.py` | 10 | `GET /users/{id}` → 200, name & email match |
| `test_q5_put_profile.py` | 10 | `PUT /users/{id}` → 200, verifies `updatedAt` |
| `test_q6_patch_field.py` | 10 | `PATCH /users/{id}` → 200, only the targeted field changed |
| `test_q8_bad_requests.py` | 20 | Bad requests using stored data → asserted 4xx (400/404) |

**Every** API request validates its HTTP response code (see
`api/api_client.py` → `utils/assertions.assert_status_code`).

---

## 10. Notes & design decisions

* **Page Object Model** keeps the Selenium tests readable and maintainable.
* **Explicit waits only** (no `time.sleep`); `performance_glitch_user` is slow,
  so Q3 uses a larger explicit-wait timeout (`UI_GLITCH_TIMEOUT`, default 60s).
* Element reads retry on `StaleElementReferenceException` because SauceDemo is a
  React app that re-renders on interaction.
* A **custom `User-Agent`** is sent to ReqRes (its WAF blocks the default
  `Python-urllib` UA with `403`).
* The `/login` token is captured and stored; the legacy demo endpoints do not
  require it as a bearer token.
* Failure screenshots are attached to the Allure report automatically.
