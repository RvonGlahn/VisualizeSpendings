### MoneyMe

This Programm was created from scratch without any planning as a test to see how it would work out.
I did it out of curiosity and I´ll never do it again...
The purpose is to visualize the spendings ordered by category  and year/month.
It helps to get an idea of where you spend your money if  you have different bank accounts or use PayPal a lot. 

This code works offline and none of the data gets transferred anywhere.

You find the diagrams in the /temp folder.

### Installation

Requirements

+ Anaconda
+ Python 3.7

Set up an anaconda virtual environment and execute

> pip install -r requirements.txt



### Customize

As I´ve already mentioned the code is a mess. 
I just customized it to my needs. Excecuting it with other input it could break. 
The csv files are all structured differently and need extra treetment for every bank.
Maybe I add some preprocessing if I find some motivation.

One big thing was that errors occured when there was a character that couldn't be decoded. 
If the programm stops and you see a weird character in your spendings text.
Go to module/GlobalVar and add this charakter to the fault list. 

