from flask import (
	Flask,
	render_template,
	redirect,
	url_for,
	request,
	make_response
)

app = Flask(__name__)
app.secret_key = 'd53e7bb364cf109017bf85cdde4c123f1ad6532b'

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    print(ip)
    print(request.headers)
    print(request.data)
    print(request.values)
    return "hello, world"

if __name__ == '__main__':
    app.run(debug=True)