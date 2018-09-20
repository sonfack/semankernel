import os
from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename

from src.common import ontology


#configure
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['rdf', 'owl'])


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def api():
    return """ 
                <p><b>/api</b> : for help</p>
                <p><b>/api/indexes</b> : to get out all indexes available in the database</p>
                <p><b>/api/index/indexName</b> : to get all types of the given index <i>ex : ontology</i></p>
                <p><b>/api/index/indexName/typeName</b> : to get all the documents of the given type<i>ex : po for plant ontology</i></p>
                <p>/<b>api/index/indexName/typeName/id</b> : to get the value of the docuement referenced by the id
                <i>ex : 2  ; a document is a concept in the given typeName(ontology)</i></p>
            """
# welcome page
@app.route('/home')
def home():
    return render_template('index.html')

# admin page
@app.route('/administrator')
def admin():
    return render_template('admin.html')

@app.route('/administrator/ontology', methods=['POST'])
def saveOntology():
    if request.method == 'POST':
        if 'ontologyFile' not in request.files:
            message = 'No file to upload'
            return render_template('admin.html', message=message)
        else:
            file = request.files['ontologyFile']
            if file.filename == '':
                message = 'No selected file'
                return render_template('admin.html', message=message)
            else:
                if file and allowed_file(file.filename):
                    onto = ontology.Ontology()
                    filename = secure_filename(file.filename)
                    print(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    index = request.form['index']
                    type = request.form['type']
                    if onto.storeOntology(UPLOAD_FOLDER+'/'+filename,type, index):
                        message = 'Ontology saved successfully'
                        return render_template('admin.html', message=message)
                    else:
                        message = 'Something went wrong while save ontology in database'
                        return render_template('admin.html', message=message)
    else:
        redirect(url_for('home'))

# print out all ontologies in the databasea
@app.route('/api/indexes', methods=['GET'])
def ontologies():
    onto = ontology.Ontology()
    allindexes = onto.noIndexQuery()
    if allindexes:
        print(allindexes)
        return render_template()
    else:
        message = 'Problem on your request'
        return render_template('index.html', message=message
                               )

# print out the list of all the concepts of a given ontologyName
@app.route('/api/ontology/<ontologyName>', methods=['GET'])
def concepts():
    pass

# print out a concept of a given ontologyName given the concept's id
@app.route('/api/ontology/<string:ontologyName>/<int:concetpId>')
def concept(ontologyName, conceptId):
    print(ontologyName)
    print(conceptId)


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug=True)