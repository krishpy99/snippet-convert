import os
import io
import zipfile
from flask import Flask
from flask import render_template, request, send_file
from werkzeug.utils import secure_filename
from converter import process_directory, unzip_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Error'
        file = request.files['file']
        if file.filename == '':
            return 'File name bruh'
        if file and file.filename.endswith('.zip'):
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Unzip and process the file
            temp_dir = unzip_file(filepath)
            process_directory(temp_dir)
            # Create a new ZIP file with processed contents
            processed_zip = io.BytesIO()
            with zipfile.ZipFile(processed_zip, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file),
                                   os.path.relpath(os.path.join(root, file),
                                   temp_dir))
            processed_zip.seek(0)
            # Clean up
            os.remove(filepath)
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(temp_dir)
            return send_file(
                processed_zip,
                as_attachment=True,
                download_name='processed_snippets.zip'
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
