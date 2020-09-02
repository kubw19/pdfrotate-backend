from flask import Flask, request, redirect, send_file, jsonify
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
import uuid
from flask_cors import CORS, cross_origin
import urllib.parse


app = Flask(__name__)
app.config.from_object('config')
cors = CORS(app)

@app.route('/')
def hello():
	return "Nothing to see here ;)"


@app.route('/uploadPDF', methods=['GET', 'POST'])
def upload_pdf():
	if request.method == 'POST':
		angle = None
		try:
			angle = int(request.form["angle"])
		except:
			pass
		if not angle or abs(angle) % 90 != 0:
			return {"message": "invalid angle"}, 400
		
		if 'file' not in request.files:
			return {"message": "no file attached"}, 400

		file = request.files['file']

		if file.filename == '':
			return {"message": "no file attached"}, 400

		if file:
			try:
				temp_name = str(uuid.uuid4())
				path = os.path.join(app.config["TEMP_DIR"], temp_name)
				file.save(path)
			except:
				return {"message": "unspecified error"}, 400

			try:
				download_url = rotate_pages(path, file.filename, angle)
			except:
				return {"message": "attached file is not valid PDF file"}, 400
			finally:
				os.remove(path)
			return  {
						"download_url": download_url
					}
		
		return {"message": "unspecified error"}, 400


@app.route('/downloadPDF/<uuid>/<filename>', methods=['GET'])
def download_pdf(uuid, filename):
	if request.method == 'GET':
		return send_file(app.config["DOWNLOAD_DIR"] + "/" + uuid, attachment_filename=urllib.parse.unquote(filename), mimetype='application/download')



def rotate_pages(pdf_path, filename, angle):
	pdf_writer = PdfFileWriter()
	pdf_reader = PdfFileReader(pdf_path)
	for page in pdf_reader.pages:        
		rotated = page.rotateClockwise(angle)
		pdf_writer.addPage(rotated)
	path, pdf_name = os.path.split(pdf_path)
	new_path = app.config["DOWNLOAD_DIR"] + "/" + pdf_name
	with open(new_path, 'wb') as fh:
		pdf_writer.write(fh)
		return app.config["DOMAIN"] + "/downloadPDF/" + pdf_name + urllib.parse.quote("/rotated_" + filename)
	return None


if __name__ == '__main__':
	app.run()