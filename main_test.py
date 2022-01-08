from ctypes import py_object

from bs4 import  BeautifulSoup
from google.colab import auth
from oauth2client.client import GoogleCredentials
import gspread
import requests, bs4



authority = "https://store.enterthee.jp/"

def getUrls(selector, url):
    url_list = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    urls = soup.select(selector)

    for url in urls:
        url=authority + url.get ("href")
        url_list.append(url)
    
    return url_list

def getPages(selector,url):
    url_list = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    urls = soup.select(selector)

    for url in urls:
        page = url.text

        if page =="16":
            lastUrl = url.get("href")
            lastNumber = int(lastUrl.split("/")[-1])
            # int 関数は引数に指定した数値または文字列を整数に変換して取得します。
            # 文字列名. split(“ 区切り文字 ”) とすることで、区切り文字で区切られたリストを得る事が出来ます。 また区切り文字がスペースや、改行、タブであるときは、特に区切り文字を指定しなくても、区切ることができます。 
            baseUrl = "/".join(lastUrl.split("/")[0:-1])
            
            for i in range(lastNumber):
                pagesUrl = authority + baseUrl + "/" + str(i+1)
                url_list.append(pagesUrl)
        return url_list
    
    def getItemAttribute(item_url):
        ItemDictionary = {}
        r = requests.get(item_url)
        soup = BeautifulSoup(r.text, "lxml")

        # 商品名
        name = soup.select(".product-main h1")
        if len(name) >0:
            ItemDictionary["name"]=name[0].text
        else:
            ItemDictionary["name"]=""
        
        #item size
        size = soup.select('span[class*="variants-ui__option-value-name option-value-name mdc-ripple-surface mdc-ripple-upgraded"]')
        if len(size):
            ItemDictionary["size"]=size[0].text
        else:
            ItemDictionary["size"]=""
        
        #item size details
        size_details = soup.select(".merkmal-title p")
        if len(size_details) >0:
            ItemDictionary["size_detail"]=size_details[0].text
        else:
            ItemDictionary["size_detail"]=""

        #size table
        size_table = soup.select(".merkmal-t table")
        if len(size_table) >0:
            ItemDictionary["size_table"]=size_table[0].text
        else:
            ItemDictionary["size_table"]=""
        
        # item material
        material =soup.find('.fib_cares_product p')
        if len(material) >0:
            ItemDictionary["material"]=size_table[0].text
        else:
            ItemDictionary["material"]=""
        
        return ItemDictionary


        # Syncing the item information to SpreadSheet

    def insertSpread(ItemDictionaryList):

            auth.authenticate_user()
            gc = gspread.authorize(GoogleCredentials.get_application_default())
            # SpreadSheet Open
            spreadsheet_key = '17Q9_9j_1w4F7WFVLKymUTf_IQgMLKDdI9Y0rdKi2F3o'
            worksheet = gc.open_by_key(spreadsheet_key).get_worksheet(0)


            for items in ItemDictionaryList:
                registData = []
                registData.append(items.get("name"))
                registData.append(items.get("size"))
                registData.append(items.get("size_detail"))
                registData.append(items.get("size_table"))
                registData.append(items.get("material"))
                worksheet.append_row(registData)
        
            paging_url_list = getPages('a[href*="collections"]',
            "https://store.enterthee.jp/collections/all?page=16")

            item_url_list = []
            for url in paging_url_list:
                item_url = getUrls('.productitem--title a[href*="products"], url')
                item_url_list.append (item_url)

            item_attiribute_list = []
            for item_url in item_url_list:
                for url in item_url:
                    item_attribute = getItemAttribute(url)
                    item_attiribute_list.append(item_attribute)

        
            insertSpread(item_attiribute_list)
