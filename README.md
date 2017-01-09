babybets
--------

A very basic flask site to enable betting on a babies arrival.

It's in the process of being refactored to be more generic and use a MySQL 
database for tracking the users etc.

Previously, I just had it hard coded for a passcode and then that code just 
be distributed to betters. The admin section was handled by a separate hard
coded username/password combo.

## TODO:

There is probably more to do than I am going to list below, but this will
be a start.

  - finish the admin section (add a page for settings)
  - email a verification link (this will require another route)
  - setup better privileges (currently the admin is assumed as id 1)
  - create tests
  - add a scoring system

## Contributions Welcome

Pull requests etc are definitely welcome :D