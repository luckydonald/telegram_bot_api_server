# tg bot api server

Powered by pytgbot, the endorsed python Telegram API client.

## Bot VS User
This API allows you to both use a API bot or a User account in the fully same way.
It is a standalone API implementation, so this API will work even if api.telegram.org is down.
It therefore supports the regular `/bot<token>/...` we're all used to and similarly `/user<token>/...`.

## Getting the User token
### `authorizePhone`
Use this method to get a unique session token for your account by providing phone number and security code in multiple steps.

First you call this function with just the `phone` number, and will get back a `phone_code_hash` and the `session`.
Those have to be provided again with the second call, when you'll additionally provide the `code` and if needed the `password`.
Returns an object of [Something](#something)

Parameter | Type | Required | Description
--------- | ---- | -------- | -----------
phone | Integer | Yes | Phone number to use. Just leave out the proceeding `+` in front of the country code, and add no special characters
phone_code_hash | String | Optional | This is the data returned from the first call.
session | String | Optional | This is the data returned from the first call.
code | String | Optional | The one time code either sent to your phone via SMS or to an already logged in account. This is the second call.
password | String | Optional | If your Account is protected with a two factor authentification password (2FA) you have to specify it on the second call.

### `Something`
Contains information about the current status of registering.

Field | Type | Description
----- | ---- | -----------
TODO | TODO | TODO

## Regular Methods
All other known [Bot API Methods](core.telegram.org/bots/api) will be supported.
Check the [normal Documentation](core.telegram.org/bots/api) for those.

### Already Supported Methods
- [x] [setWebhook](https://core.telegram.org/bots/api#setwebhook)
- [x] [deleteWebhook](https://core.telegram.org/bots/api#deletewebhook)
- [x] [getUpdates](https://core.telegram.org/bots/api#getupdates)
- [x] [getMe](https://core.telegram.org/bots/api#getme)
- [x] [getUpdates](https://core.telegram.org/bots/api#getupdates)
- [x] [sendMessage](https://core.telegram.org/bots/api#sendmessage)
- [x] [sendChatAction](https://core.telegram.org/bots/api#sendchataction)
- [x] [sendLocation](https://core.telegram.org/bots/api#sendlocation)
- [x] [editMessageLiveLocation](https://core.telegram.org/bots/api#editmessagelivelocation)
- [x] [stopMessageLiveLocation](https://core.telegram.org/bots/api#stopmessagelivelocation)
- [x] [sendVenue](https://core.telegram.org/bots/api#sendvenue)

