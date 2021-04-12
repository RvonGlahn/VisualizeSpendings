import pickle


categories = {
        "Supermarkt": ["REWE", "NAHKAUF", "Netto", "LIDL", "Lidl", "ALDI", "JUMBO", "PINGO", "EDEKA", "DM", "Rossmann",
                       "WUCHERPFENNIG", "MERCADONA", "mercado", "WAITROSE", "CONSUM", "SUPER", "super", "NP",
                       "KAUFLAND"],
        "Nahverkehr": ["RYANAIR", "BISI", "DB", "HVV", "BVG", "BUS", "Ticket", "TICKET", "UBER", "STRASSENBAHN", "Bahn",
                       "TFL", "SERVIENTRADAS", "GVH", "uestra"],
        "Kleidung": ["H&M", "H+M", "MUSTANG", "PULL", "BEAR", "SPRINGFIELD", "BERSHKA", "ZARA", "WEEKDAY", "DONO",
                     "ASOS", "SHOE4YOU", "Backyard", "ZALANDO", "Reserved", "Esprit", "C&A"],
        "Shopping": ["FIELMANN", "AMZN", "AMAZON", "DECATHLON", "JUMPERBAND", "tasko", "Obi", "BAUHAUS", "ZWEI",
                     "THOMANN", "ELEKTRONIK"],
        "Wohnen": ["LOGOS", "Miete", "Haus", "Treppenhausreinigung", "Treppenhausreinigung", "Apartments"],
        "Bargeld": ["bank", "BANK"],
        "Versicherungen": ["versicherung"],
        "Einkommen": ["Gehalt", "Einkommen", "Rente"],
        "Urlaub": ["Hotel", "Airport", "RYANAIR", "Airline", "Airbnb", "Guide", "booking"],
        "Sonstige": ["sonstige"],
        "Ignorieren": ["qwertzui"]
    }


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(r'category.pkl', 'rb') as f:
        return pickle.load(f)


save_obj(categories, "category")
