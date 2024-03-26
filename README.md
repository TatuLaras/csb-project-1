LINK: https://github.com/TatuLaras/csb-project-1

Make sure you have all the relevant dependencies from the course installation guide: https://cybersecuritybase.mooc.fi/installation-guide .
Also one of the _fixes_ requires the bcrypt Python module to be installed, but it isn't needed for the current, "broken", version.

To successfully install the project, run the following two Python scripts in the project root:
`python3 manage.py migrate`
`python3 create_db.py`

After which the project can be run with:
`python3 manage.py runserver`



Note: I am using the 2017 version of the OWASP top 10.


FLAW 1:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L11

The app uses the dated and now insecure md5 hash algorithm, in addition to not salting the password. This falls under A3:2017-Sensitive Data Exposure, because in the case of a data breach, an attacker can deduce the user's original password from the hash using dictionaries of precomputed hashes or other brute-force methods (depending on the strength of the password). Of the popular cryptographic hashing algorithms, md5 in among the least resistant to this kind of deduction, due to its short hash length.

The fix is to use a more secure hashing algorithm, such as bcrypt, SHA-2, or Argon2, in addition to salting the password. In the code, I provided a fix for this problem which swaps out the md5 algorithm for bcrypt.

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

One other solution for this problem would be to check the user's password against a list of the most common passwords in use. I haven't seen this employed in many real applications though.




FLAW 4:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L134

The app doesn't sanitize inputs properly for the register form username field, enabling SQL injection attacks. This falls under A1:2017-Injection.

The fix for this flaw is to sanitize the input properly. In the Python sqlite3 -module, this is done by using the a question mark as a placeholder in the query and binding the user input to that. Alternatively, one could take the approach recommended by Django by using the built-in ORM (Object-Relational Model) tools to handle your database traffic. That way most of your database queries are done through the ORM objects and the tools handle the querying for you, sanitizing the inputs properly for you. In fact, I went out of my way to not use the tools recommended in the Django documentation to even make introducing this flaw possible.

An example of a properly sanitized user input can be found in the code: https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/loginViews.py#L141




FLAW 5:
https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/templates/csbproject1/dashboard.html#L43

Note: I am linking to a HTML template, but the security flaw and its fix occur inside the template values, which are processed in the backend.

The app outputs user-generated input onto the site as raw HTML, enabling the possibility for cross-site scripting (XSS) attacks, in which a malicious script tag in the content of a post will be run on each client. This (pretty obviously) falls under A7:2017-Cross-Site Scripting (XSS).

The fix is to not output anything user-generated as raw HTML, but instead rendering it as text, replacing critical characters such as < and > with HTML entities. For security reasons, the default behaviour of Django is to do exactly that, unless bypassed with a "|safe" -filter. In this fictional application, maybe the developer wanted to enable users to style their posts with HTML tags, such as strong or h1. In this case, a more sophisticated approach is needed, where only unwanted tags such as script tags are escaped, but the rest are preserved.

An example of this "|safe" -filter and how disabling it leads to the prevention of XSS attacks can be found in the code: https://github.com/TatuLaras/csb-project-1/blob/master/csbproject1/templates/csbproject1/dashboard.html#L47



