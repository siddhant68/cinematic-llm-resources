# OAuth setup

Use official Google OAuth for an installed desktop application.

## Google Cloud setup

1. Create or select a Google Cloud project.
2. Enable YouTube Data API v3.
3. Configure the OAuth consent screen.
4. Create OAuth client credentials with application type Desktop app.
5. Download the client secret JSON to a secure location outside this bundle.
6. Add the channel operator as a test user while the consent screen remains in testing, when required.

The script requests:

- `youtube.upload` for media upload
- `youtube.force-ssl` for thumbnail-adjacent metadata operations, captions, playlists, comments, and readback

Review the OAuth account and channel carefully in the browser. A valid token for the wrong Google account is a dangerous success.

## Token storage

The `--token` path stores access and refresh credentials. Treat it like a password:

- keep it outside source control
- restrict local file permissions
- do not send it in chat or package it with a skill
- delete or revoke it when the machine or project is no longer trusted

Use a separate Google Cloud project and token for test automation where practical.
