# Automation Assessment

This is my solution to the automation assessment. I split it into two parts:

- `saucedemo_ui.py` for the UI questions (SauceDemo)
- `postman/` for the API questions (ReqRes)

## UI questions

I used Python and Selenium for these. The script opens Chrome and runs the three scenarios one after another.

**Q1. Locked out user**
I log in as `locked_out_user` and check that the error message is shown. The message I expect is `Epic sadface: Sorry, this user has been locked out.`

**Q2. Standard user purchase**
I log in as `standard_user` and reset the app state first. Then I add three products to the cart (Backpack, Bike Light, Bolt T-Shirt) and go through checkout. On the overview page I check the product names and the total price. After that I finish the order and check the success message, then reset the app state and log out.

**Q3. Performance glitch user**
This user is slow, so I gave the waits a bit more room. I log in, reset the app state, and sort the products by Name (Z to A). I take the first product after sorting and buy only that one. On the overview page I check the name and the total, finish the order, check the success message, then reset and log out.

To run the UI script:

```powershell
pip install selenium
python saucedemo_ui.py
```

It opens a visible Chrome window. If you want it to run without the window, set `SELENIUM_HEADLESS=1` before running:

```powershell
$env:SELENIUM_HEADLESS="1"; python saucedemo_ui.py
```

## API questions

For the API part I made a Postman collection with an environment file. Every request has tests that check the status code and the response body. The collection saves the token from the login request so the later requests can use it.

- **Q3** - I log in with the given email and password, then save the `token` from the response.
- **Q4** - I get a user by id and check the name and email.
- **Q5** - I send a PUT request with an updated name and job, then check the response and that `updatedAt` is there.
- **Q6** - I send a PATCH request that only changes the job, and check that nothing else changed.
- **Q8** - I send a few bad requests (missing password, unknown user, unknown id, register without password) and check they return a 4xx with the right error message.

You can run it in Postman by importing `postman/ReqRes_API.postman_collection.json` and `postman/ReqRes.postman_environment.json`, then running the collection. Or from the terminal with Newman:

```powershell
newman run postman/ReqRes_API.postman_collection.json -e postman/ReqRes.postman_environment.json
```

One thing to keep in mind: ReqRes only allows 40 requests per day for anonymous use. If it starts returning 429, it's just the daily limit, so wait a bit and run it again.
