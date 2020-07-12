# modfest-site
Work-in-progress site rewrite for the ModFest event.

Endpoints (planned and implemented):
```
Display/Frontend:                                          Example URL:
[x]  /                                                     (https://modfest.net)
[x]  /link                                                 (https://modfest.net/link)
[x]  /auth                                                 (https://modfest.net/auth)
[x]  /<string:event>                                       (https://modfest.net/1.16)
[ ]  /<string:event>/join                                  (https://modfest.net/1.16/join)
[x]  /<string:event>/entries                               (https://modfest.net/1.16/entries)
[ ]  /<string:event>/vote                                  (https://modfest.net/1.16/vote)
[ ]  /<string:event>/entries/new                           (https://modfest.net/1.16/entries/new)
[ ]  /participants/<int:uid>                               (https://modfest.net/participants/0)

API/Backend:
[x]  /api/v1                                               (https://modfest.net/api/v1)
[x]  /api/v1/link?code=<string:code>                       (https://modfest.net/api/v1/link?code=aaaaaa)
```

* x = done
* \- = needs ui
*   = planned