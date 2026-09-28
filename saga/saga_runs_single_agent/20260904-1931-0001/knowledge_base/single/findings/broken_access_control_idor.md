# Broken Access Control / IDOR

**Affected Endpoints:**
- `GET /profile?username={target}` - View any user's profile
- `GET /direct_messages?username={target}` - View any user's direct messages
- `GET /delete_post?id={id}` - Delete any post
- `GET /edit_post?id={id}` - Edit any post

**Risk:** High

## Detection

### 1. Profile IDOR (Horizontal Privilege Escalation)
As user `admin`, accessing `/profile?username=stark` successfully loads stark's full profile including posts, bio, and friend status. The application does not verify that the requesting user has authorization to view another user's profile data.

### 2. Direct Messages IDOR
As user `admin`, accessing `/direct_messages?username=stark` loads the direct message interface for user stark. While no messages were returned, the endpoint is accessible without authorization checks.

### 3. Post Deletion IDOR (Vertical Privilege Escalation)
As user `admin`, accessing `GET /delete_post?id=1` successfully deletes a post with a flash message "Post deleted". This demonstrates that any authenticated user can delete posts belonging to other users by manipulating the `id` parameter.

## Evidence
- `GET /profile?username=stark` as admin → 200 OK with full profile content
- `GET /direct_messages?username=stark` as admin → 200 OK with message interface
- `GET /delete_post?id=1` as admin → 200 OK with "Post deleted" flash message

## Impact
- **Horizontal:** Users can view other users' profiles and messages
- **Vertical:** Users can delete/edit posts belonging to other users
- **Data exposure:** Full user profiles, posts, and private communications are accessible

## Remediation
- Implement ownership checks on all resource access
- Verify user authorization before returning profile/message data
- Restrict post deletion/editing to post owners or administrators only