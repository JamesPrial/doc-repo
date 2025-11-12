# NODRIVER

[CLICK HERE FOR DOCS](https://ultrafunkamsterdam.github.io/nodriver/)

**This package provides next level webscraping and browser automation using a relatively simple interface.**

  * **This is the official successor of the** [Undetected-Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver/) **python package.**

  * **No more webdriver, no more selenium**




Direct communication provides even better resistance against web applicatinon firewalls (WAF's), while performance gets a massive boost. This module is, contrary to undetected-chromedriver, fully asynchronous.

What makes this package different from other known packages, is the optimization to stay undetected for most anti-bot solutions.

Another focus point is usability and quick prototyping, so expect a lot to work -as is- , with most method parameters having best practice defaults. Using 1 or 2 lines, this is up and running, providing best practice config by default.

While usability and convenience is important. It's also easy to fully customizable everything using the entire array of [CDP](https://chromedevtools.github.io/devtools-protocol/) domains, methods and events available.

# Some features

  * A blazing fast undetected chrome (-ish) automation library

  * No chromedriver binary or Selenium dependency

  * This equals bizarre performance increase and less detections!

  * Up and running in 1 line of code*

  * uses fresh profile on each run, cleans up on exit

  * save and load cookies to file to not repeat tedious login steps

  * smart element lookup, by selector or text, including iframe content. this could also be used as wait condition for a element to appear, since it will retry for the duration of <timeout> until found. single element lookup by text using tab.find(), accepts a best_match flag, which will not naively return the first match, but will match candidates by closest matching text length.

  * descriptive __repr__ for elements, which represent the element as html

  * utility function to convert a running undetected_chromedriver.Chrome instance to a nodriver.Browser instance and contintue from there

  * packed with helpers and utility methods for most used and important operations




## Quick start

## Main objects

## CDP object
