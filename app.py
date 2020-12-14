from flask import Flask, request, jsonify,render_template,json
from functions import generate_excel,uploadfile_to_s3

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        data = request.get_json()

        output = generate_excel()
        
        file_url = uploadfile_to_s3(output)

        response_data = {'file_url':file_url}
        response = app.response_class(response=json.dumps(response_data),
                                  status=200,
                                  mimetype='application/json')

        return response

    else: #if the request is GET, simply display home page
        return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)