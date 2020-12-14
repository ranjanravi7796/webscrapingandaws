from config import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET , S3_LOCATION
import pandas as pd
from io import BytesIO
import xlsxwriter
import boto3
from datetime import datetime
import requests, re
from bs4 import BeautifulSoup

headers = {
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

s3 = boto3.client("s3",
aws_access_key_id=S3_ACCESS_KEY,
aws_secret_access_key=S3_SECRET_ACCESS_KEY)

def generate_excel():

    r=requests.get("http://www.pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/", headers=headers) # We use the headers here
    c=r.content

    soup=BeautifulSoup(c,"html.parser")

    all=soup.find_all("div",{"class":"propertyRow"})

    all[0].find("h4",{"class":"propPrice"}).text.replace("\n","").replace(" ","")

    page_nr=soup.find_all("a",{"class":"Page"})[-1].text
    print(page_nr,"number of pages were found")

    l=[]
    base_url="http://www.pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS/t=0&s="
    for page in range(0,int(page_nr)*10,10):
        print( )
        r=requests.get(base_url+str(page)+".html", headers=headers)
        c=r.content
        #c=r.json()["list"]
        soup=BeautifulSoup(c,"html.parser")
        all=soup.find_all("div",{"class":"propertyRow"})
        for item in all:
            d={}
            d["Address"]=item.find_all("span",{"class","propAddressCollapse"})[0].text
            try:
                d["Locality"]=item.find_all("span",{"class","propAddressCollapse"})[1].text
            except:
                d["Locality"]=None
            d["Price"]=item.find("h4",{"class","propPrice"}).text.replace("\n","").replace(" ","")
            try:
                d["Beds"]=item.find("span",{"class","infoBed"}).find("b").text
            except:
                d["Beds"]=None
        
            try:
                d["Area"]=item.find("span",{"class","infoSqFt"}).find("b").text
            except:
                d["Area"]=None
        
            try:
                d["Full Baths"]=item.find("span",{"class","infoValueFullBath"}).find("b").text
            except:
                d["Full Baths"]=None

            try:
                d["Half Baths"]=item.find("span",{"class","infoValueHalfBath"}).find("b").text
            except:
                d["Half Baths"]=None
            for column_group in item.find_all("div",{"class":"columnGroup"}):
                for feature_group, feature_name in zip(column_group.find_all("span",{"class":"featureGroup"}),column_group.find_all("span",{"class":"featureName"})):
                    if "Lot Size" in feature_group.text:
                        #print(feature_name.text)
                        d["Lot Size"]=feature_name.text
            l.append(d)

    df = pd.DataFrame(l)
    #create an output stream
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer,startrow = 0, merge_cells = False,index=False, header=True, sheet_name='Sheet1')

   # df1.to_excel(writer,startrow = 0, merge_cells = False,index=False, header=False, sheet_name='Sheet1')
    #df2.to_excel(writer,startrow = 0, merge_cells = False, index=False, header=False,sheet_name='Sheet2')

    writer.save()
    output.seek(0)

    return output


def uploadfile_to_s3(generated_file):
    try:
        filename = 'mydemoexcel_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.xlsx'
        s3.upload_fileobj(generated_file, S3_BUCKET,filename ,ExtraArgs={
        "ACL": 'public-read'})
    except:
        print("Error occurred while uploading excel to S3 bucket")

    return "{}{}".format(S3_LOCATION,filename)