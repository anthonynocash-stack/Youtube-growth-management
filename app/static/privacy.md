# CreatorFlow privacy notice

This single-operator app uses [YouTube API Services](https://developers.google.com/youtube/terms/api-services-terms-of-service). Google processes authentication/API requests under the [Google Privacy Policy](https://policies.google.com/privacy).

It stores Google OAuth tokens, YouTube analytics, Autopilot settings, content packs, upload IDs, and generated MP4 files locally. It sends prompts to the AI provider configured by the operator and sends narration to its speech endpoint. Uploaded videos and metadata are sent to YouTube when Autopilot is enabled.

Disconnecting removes the local OAuth token and stops Autopilot. To erase all local CreatorFlow data, stop the service and delete the configured SQLite database and `VIDEO_OUTPUT_DIR`. This does not delete videos already uploaded to YouTube; manage those in YouTube Studio. Revoke Google access at [Google Account permissions](https://security.google.com/settings/security/permissions).
