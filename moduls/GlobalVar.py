from moduls import money_data
#from moduls import visualize

card = money_data.Card()        # dataframe for transactions of a card

categories = []                 # categories to filter spendings
first_card = True

category_dict = None            # load old and save all new categories in the dict

visual_df = None                # df that contains Data for Date, Ausgabenart, Betrag and Kartentyp

fault_list = ["+", "*", "^", ".", "@", "?", "(", ")"]  # fault list of characters that might raise errors