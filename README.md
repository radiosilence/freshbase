FreshBase
=========

Simple little script to get time from Codebase and push it to FreshBooks

1. pip install -r requirements.txt
1. cp config.py.sample config.py
1. Edit config.py and make sure all the values are set. You also need to make
    sure you have the correct project/task ID from Freshbooks. You can find
    this either through using the API or Inspect Elementing a select on the
    website.
1. python freshbase.py