from flask import Flask, request, jsonify,render_template,send_file,json
from config import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET , S3_LOCATION
import flask_excel as excel
import pandas as pd
import numpy as np
from io import BytesIO
import xlsxwriter
import boto3
import pickle
from datetime import datetime

app = Flask(__name__)
s3 = boto3.client("s3",
aws_access_key_id=S3_ACCESS_KEY,
aws_secret_access_key=S3_SECRET_ACCESS_KEY)

def generateexcel(str1,str2):
    df1 = pd.DataFrame([x for x in str1])
    df2 = pd.DataFrame([x for x in str2])

    #create an output stream
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df1.to_excel(writer,startrow = 0, merge_cells = False,index=False, header=False, sheet_name='Sheet1')
    df2.to_excel(writer,startrow = 0, merge_cells = False, index=False, header=False,sheet_name='Sheet2')

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


@app.route("/",methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        data = request.get_json()
        str1 = data['string1']
        str2 = data['string2']
        print(str1)
        output = generateexcel(str1,str2)
        
        file_url = uploadfile_to_s3(output)

        response_data = {'file_url':file_url}
        response = app.response_class(response=json.dumps(response_data),
                                  status=200,
                                  mimetype='application/json')
        #finally return the file
        return response

    else:
        return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)