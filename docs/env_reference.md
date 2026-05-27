## Publishing

| Variable | Values | Default | Description |
|---|---|---|---|
| `PUBLISH_MODE` | `disabled` `mock` `real` | `disabled` | Controls publish behavior globally |

## Social Targets

| Variable | Values | Default | Description |
|---|---|---|---|
| `SOCIAL_TARGETS` | comma-separated list | | Registry of named social targets to publish to |

Each target must be defined using a `SOCIAL__{TARGET_KEY}__...` block.

Example:

```bash
SOCIAL_TARGETS=gs_facebook_main,gs_instagram_main
SOCIAL__GS_FACEBOOK_MAIN__PLATFORM=facebook
SOCIAL__GS_FACEBOOK_MAIN__ENABLED=true
SOCIAL__GS_FACEBOOK_MAIN__PAGE_ID=111111111
SOCIAL__GS_FACEBOOK_MAIN__ACCESS_TOKEN=EAAxxxxx
SOCIAL__GS_INSTAGRAM_MAIN__PLATFORM=instagram
SOCIAL__GS_INSTAGRAM_MAIN__ENABLED=true
SOCIAL__GS_INSTAGRAM_MAIN__PAGE_ID=333333333
SOCIAL__GS_INSTAGRAM_MAIN__ACCESS_TOKEN=EAAzzzzz
```

### Target variables

| Variable | Required | Description |
|---|---|---|
| `SOCIAL__{TARGET_KEY}__PLATFORM` | Yes | `facebook` or `instagram` |
| `SOCIAL__{TARGET_KEY}__ENABLED` | Yes | `true` / `false` to enable the target in real mode |
| `SOCIAL__{TARGET_KEY}__PAGE_ID` | Real mode | Page ID or Instagram account ID |
| `SOCIAL__{TARGET_KEY}__ACCESS_TOKEN` | Real mode | Access token for the target |
| `SOCIAL__{TARGET_KEY}__NAME` | No | Optional human-readable target name |

## Facebook

Facebook publishing uses named targets instead of a single global page config. Define each Facebook page as a separate target in `SOCIAL_TARGETS`.

### Getting a Page Access Token

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create an App → Business type
3. Add the Pages API product
4. Generate a Page Access Token for your Page
5. Use the Token Debugger to verify it has `pages_manage_posts` permission

## Instagram

Instagram publishing also uses named targets. Real Instagram support is not implemented yet, so use `PUBLISH_MODE=mock` for now.

| Variable | Required | Description |
|---|---|---|
| `INSTAGRAM_ENABLED` | `true` `false` | `false` | Reserved for future real implementation |

Real Instagram publishing is not yet implemented. Set `PUBLISH_MODE=mock`.
