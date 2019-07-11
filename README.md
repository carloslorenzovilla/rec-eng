# rec-eng
2019 Capstone Project

Hello! This is my 2019 EE capstone project. In a nutshell, it is a python script that makes recommendations on things 
like food or beverage, based on a user's consumption history. So how does it work? At the heart of the engine is a 
keyword matrix. The keyword matrix is a binary representation of a list (or menu) of items. Each item on this list
(or menu) can be broken down into a set of keywords. For example, Chicken Pozole would take on the keywords soup, 
chicken, and hominy. Or Carbonara would take on the keywords pasta, pork, cheese. To represent an entire menu, you'd
need a bag of keywords. To represent an item in binary form we use an mXn matrix, where there are m-items and n-keywords.
If the keyword applies to the item that cell takes a 1, otherwise the cell is zero. The keyword matrix allows us to
find similarities between a guest's consumption history and all the items on the list (or menu).

I did not use real data. Instead I used simulations of: list of users (guests), keyword matrix, transactional data. The
script is a main.py module and two additional modules, sims.py and rec.py, that hold the classes for simulated data
and recommendations, respectively.

I recently reworked the original project into classes, rather that just making calls to a whole bunch of functions. I
found that the use of objects are a step in the right direction as I work to implement into a Tkinter GUI. Will have 
that update soon.

Anyway, thanks for checking this out!
