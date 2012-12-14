# Actuarize your Facebook friends

This is a little script I pulled together to pull my Facebook friends' age and sex data and format it to run through [xkcd's actuary.py](http://blog.xkcd.com/2012/07/12/a-morbid-python-script/) so I could amaze by friends with probabilistic predictions of their own collective demise.

I used [Temboo](http://www.temboo.com) to handle the OAuth bit, but I'm sure someone more talented than I could figure out how to do it without that. I just finally gave up.  I use the standard [Facebook Python SDK](@pythonforfacebook/facebook-sdk) with [FQL](https://developers.facebook.com/docs/reference/fql/) to pull the actual data. I'm storing the relevant keys in a CSV file (not very robust, I know).  I included an example with just the headers. The first time you authenticate, it will write the access token back to this file so you don't need to authenticate again until it expires.

This is yours to use however you like under the MIT License.