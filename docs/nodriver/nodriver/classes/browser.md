# Browser class

# cookies

You can load and save all cookies from the browser.
    
    
    # save. when no filepath is given, it is saved in '.session.dat'
    await browser.cookies.save()
    
    
    # load. when no filepath is given, it is loaded from '.session.dat'
    await browser.cookies.load()
    
    
    # export for requests or other library
    requests_style_cookies = await browser.cookies.get_all(requests_cookie_format=True)
    
    # use in requests:
    session = requests.Session()
    for cookie in requests_style_cookies:
        session.cookies.set_cookie(cookie)

# Browser class
