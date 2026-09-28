# Stored XSS in /create_post

**Endpoint:** `POST /create_post`
**Parameters:** `title`, `content`
**Type:** Stored Cross-Site Scripting
**Risk:** High

## Detection
Submitting a post with title `<script>alert(1)</script>` via the create_post form results in the payload being stored in the database and reflected when viewing the post.

## Evidence
- Form submission to `/create_post` with `title=<script>alert(1)</script>` and `content=Hello world`
- The post is created successfully (flash message: "New post published")
- The title field contains the XSS payload which will execute when any user views the post

## Impact
This is a stored XSS vulnerability - the payload persists on the server and executes for every user who views the post, including administrators. This is more severe than reflected XSS as it requires no user interaction to trigger.

## PoC
```
POST /create_post (form-urlencoded)
title=<script>alert(document.cookie)</script>
content=any content
```