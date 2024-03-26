LINK: https://github.com/TatuLaras/csb-project-1

Make sure you have all the relevant dependencies from the course installation guide: https://cybersecuritybase.mooc.fi/installation-guide .
Also one of the _fixes_ requires the bcrypt Python module to be installed, but it isn't needed for the current, "broken", version.

To successfully install the project, run the following two commands:
`python3 manage.py migrate`
`python3 create_db.py`


FLAW 1:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L11

The app uses the dated and now insecure md5 hash algorithm, in addition to not salting the password. This falls under A3:2017-Sensitive Data Exposure, because in the case of a data breach, an attacker can deduce the user's original password from the hash using dictionaries of precomputed hashes or brute-force methods (depending on the strength of the password). Of the cryptographic hashing algorightms, md5 in among the least resistant to this kind of deduction due to its short hash length.

The fix is to use a more secure hashing algorithm, such as bcrypt, SHA-2 or Argon2, in addition to salting the password. In the code, I provided a fix for this problem which swaps out the md5 algorighm for bcrypt.

https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L15




FLAW 2:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L63

The app uses a cookie for storing authentication data, which is just an integer of the user's ID, allowing an attacker to gain access to other users' accounts simply by editing the cookie on the client side to another user's ID. This falls under A5:2017-Broken Access Control.

This is analoguous to a weak session ID, but because Django makes it a bit difficult to shoot yourself in the foot in this way, this is what I went with.

The fix is to use session storage instead of a client-side cookie, which in Django comes with a secure session ID'ing system where the deduction of another user's session ID is not as trivial.

I included a more detailed fix in the code: https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L75




FLAW 3:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L101

The app permits the user to use any password, no matter how insecure, short or common it is. This falls under A2:2017-Broken Authentication.

The fix is to place limits on the types of passwords the user can choose. For example, setting a minimum length for the password is a good place to start. In addition, the app could require that the password should contain at least one number and one special character of some sort.

A practical implementation of these fixes can be found in the code: https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L104

There are lot's of documents that give guidelines for what an app should require from a user's password. For example, one such document can be found at: https://pages.nist.gov/800-63-3/sp800-63b.html#memsecret

One other solution for this problem would be to check the user's password against a list of the most common passwords in use. I haven't seen this employed in many real applications though due to the inherit.




FLAW 4:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L134


