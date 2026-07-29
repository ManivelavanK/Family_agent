# Twilio WhatsApp Business Sandbox Setup Guide

This guide explains how to set up the Twilio WhatsApp Sandbox to enable real WhatsApp notifications from the KinNest Grandparent Agent.

---

## 1. Create a Twilio Account
1. Go to the [Twilio Sign Up Page](https://www.twilio.com/try-twilio) and register for a free trial account.
2. Verify your email address and phone number.
3. Once logged in, select **Developer** as your role and answer the introductory questions to access your main console home page.

---

## 2. Obtain Your Account SID
1. Go to the [Twilio Console](https://console.twilio.com).
2. Locate the **Project Info** section on the main dashboard page.
3. Copy the string labeled **Account SID** (starts with `AC...`).
4. Paste it into your [.env](file:///c:/projects/grandparent_agent/.env) file:
   ```env
   TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

---

## 3. Obtain Your Auth Token
1. In the same **Project Info** section on the Console, find the **Auth Token** field.
2. Click **Show** to reveal the token, and copy it.
3. Paste it into your [.env](file:///c:/projects/grandparent_agent/.env) file:
   ```env
   TWILIO_AUTH_TOKEN=your_auth_token_here
   ```

---

## 4. Activate the WhatsApp Sandbox
1. From the left navigation menu, go to **Messaging > Try it out > Send a WhatsApp Message**.
2. This page shows the Twilio WhatsApp Business Sandbox dashboard.
3. The page displays the sandbox phone number and your unique sandbox join keyword.

---

## 5. Find the Sandbox WhatsApp Number
- The Twilio Sandbox number is listed on the **Send a WhatsApp Message** console page.
- It is typically: `+1 415 523 8886` (represented in code configurations as `whatsapp:+14155238886`).
- Copy and save this to your [.env](file:///c:/projects/grandparent_agent/.env) file:
   ```env
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

---

## 6. Join the Sandbox
1. Add the Twilio Sandbox phone number (e.g., `+1 415 523 8886`) as a contact on your personal phone.
2. Open WhatsApp, go to the new contact chat window, and send your unique join code. The code format is:
   ```text
   join <keyword>
   ```
   *(For example: `join flag-orange`)*
3. You will receive an automated response confirmation from the Twilio Sandbox:
   > *"You are all set!..."*
4. Add your personal phone number to your [.env](file:///c:/projects/grandparent_agent/.env) file:
   ```env
   DEFAULT_FAMILY_PHONE=whatsapp:+91XXXXXXXXXX
   ```

---

## 7. Verify Successful Setup
1. Start the FastAPI server:
   ```powershell
   .\venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```
2. Verify that the terminal console logs print the confirmation on startup:
   ```text
   WhatsApp Service running in REAL mode
   ```
3. Open `http://127.0.0.1:8000/docs` in your browser.
4. Locate the **WhatsApp Notifications** category and execute `POST /api/v1/notification/test`.
5. Confirm that a test WhatsApp message is successfully delivered to your phone.

---

## 8. Common Errors & Troubleshooting

### Authentication Error (Code 20003)
- **Problem**: Twilio rejects the connection.
- **Cause**: The `TWILIO_ACCOUNT_SID` or `TWILIO_AUTH_TOKEN` is incorrect or missing.
- **Solution**: Double check both values in your `.env` file and make sure no trailing whitespaces or quotes were added.

### Sandbox Not Joined (Code 21608)
- **Problem**: You receive a success response but no message, or the logs report: *"The recipient has not joined the Twilio WhatsApp Sandbox yet."*
- **Cause**: The recipient's phone number has not joined the sandbox session or the session has expired (sandbox sessions expire after 24 hours of inactivity).
- **Solution**: Send `join <keyword>` from the recipient's WhatsApp to the sandbox number again to refresh the connection.

### Invalid Number (Code 21211)
- **Problem**: Twilio reports the phone number is invalid.
- **Cause**: The phone number format is incorrect, missing country code, or contains spaces.
- **Solution**: Format the number with a leading `+` and country code (e.g. `+919999999999`). Do not include hyphens, parenthesis, or spaces.
