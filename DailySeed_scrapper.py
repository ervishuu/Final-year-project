# load library
from bs4 import BeautifulSoup
from requests import get
import sqlite3


def mandidb():
    # -------web scraping using beautifulsoup -------------#
    connection = sqlite3.connect('mandi_database.db')
    cursor = connection.cursor()
    return connection,cursor

def scrapeData():
    connection , cursor = mandidb()
    # -------------clear table -----------------
    try:
        print("start deleting .....................")
        sql_Delete_query = """Delete from rates_data where arival_date > 01/01/2015"""
        cursor.execute(sql_Delete_query)
        connection.commit()
        print("previous all records are deleted ")
    except:
        print("something is wrong")

    list_data = [
        'bajra-pearl-milletcumbu',
        'bengal-gram-dal-chana-dal',
        'chili-red',
        'coconut',
        'cotton',
        'dry-grapes',
        'green-chilli',
        'maize',
        'onion',
        'potato',
        'rice',
        'soyabean',
        'sugarcane',
        'sunflower',
        'sweet-potato',
        'tomato',
        'water-melon',
        'wheat',
        'pomegranate',
        'mataki',
        'seetapal'
    ]
    for names in list_data:
        print(
            "==========================================================// {} //================================================================".format(
                names))
        siteUrl = "https://www.commodityonline.com/mandiprices/{}/maharashtra".format(names)
        responce = get(siteUrl)
        main_container = BeautifulSoup(responce.text, 'html.parser')
        sub_container = main_container.find('table', {'id': 'main-table2'})
        main_table = sub_container.find_all('tr')
        for rows in main_table:
            try:
                data = rows.find_all('td')
                item_list = []
                for rows2 in data:
                    try:
                        item_list.append(rows2.text)
                    except:
                        pass
                print(
                    "================================================================================================================================")

                qu ="INSERT INTO rates_data (arival_date,variety,state,market,min,max,avrageprice,commidity) VALUES('{}','{}','{}','{}','{}','{}','{}','{}')".format(item_list[1],item_list[2],item_list[3],item_list[4],item_list[5],item_list[6],item_list[7],item_list[0])
                cursor.execute(qu)
                connection.commit()
                print('Arrival Date : ', item_list[1])
                print("Variety : ", item_list[2])
                print("State : ", item_list[3])
                print("Market : ", item_list[4])
                print("Min Price (Rs./Quintal) : ", item_list[5])
                print("Max Price (Rs./Quintal) : ", item_list[6])
                print("Average price (Rs./Quintal) : ", item_list[7])
                print("Commodity : ", item_list[0])

            except:
                pass

    cursor.close()

    return "All data are scrapped sucessfully .."
