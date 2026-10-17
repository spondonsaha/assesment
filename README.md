# Automation Testing Assessment

Simple automation scripts: a Selenium script that opens a visible Chrome window
and runs the SauceDemo scenarios, and a `requests` script that runs the ReqRes
API checks.

## Setup

```powershell
pip install selenium requests
```

Chrome is required for the UI script (Selenium downloads the driver on its own).

## UI tests (SauceDemo)

```powershell
python saucedemo_ui.py
```

A Chrome window opens and runs, one after another:

* **Q1** – `locked_out_user` shows the lock-out error
* **Q2** – `standard_user`: reset app state → add 3 items → checkout → verify product names & total price → finish → success message → reset → logout
* **Q3** – `performance_glitch_user`: reset → filter Name (Z→A) → add first product → checkout → verify names & total → finish → success message → reset → logout

At the end it prints a PASS/FAIL summary. Press Enter to close the browser.

## API tests (ReqRes)

```powershell
python reqres_api.py
```

Covers: **Q3** login + authToken, **Q4** get user (name/email), **Q5** PUT profile
(`updatedAt`), **Q6** PATCH single field, **Q8** bad requests return 4xx.

> ReqRes allows 40 requests/day for anonymous use. If that limit is hit you'll get
> a friendly message — just try again later.

## Postman

Import the files in the `postman/` folder, or run from the command line:

```powershell
newman run postman/ReqRes_API.postman_collection.json -e postman/ReqRes.postman_environment.json
```
