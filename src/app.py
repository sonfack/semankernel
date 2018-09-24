import os
import re
from flask import Flask, render_template, request, url_for, redirect
# NLTK Stop words
from nltk.corpus import stopwords
# NLTK tokenize
from nltk.tokenize import word_tokenize
# NLTK stemming
from nltk.stem import PorterStemmer

from werkzeug.utils import secure_filename

from src.common import ontology

from stemming.porter2 import stem


#configure
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['rdf', 'owl'])


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




def resultProcessin(result):
    hits = result.get('hits')
    total = hits.get('total')
    print(total)
    resultListe = []
    if total >= 1:
        results = hits.get('hits')
        for entity in results:
            print(entity['_source'])
            resultListe.append(entity['_source'])
        return resultListe
    else:
        return False


def textProcessing(text):
    newText = text.lower()
    newText = re.sub('[0-9]', '', newText)
    newText = re.sub('[^ a-zA-Z0-9]', '', newText)
    # print(newText)

    # tokenize
    word_tokens = word_tokenize(newText)

    # load stop words
    stop_words = stopwords.words('english')
    # print(stop_words)

    # Remove stop words
    filterWords = [word for word in word_tokens if word not in stop_words]
    # print(filterWords)

    # stemming words
    # ps = PorterStemmer()
    stemWords = []

    for word in filterWords:
        stemWords.append(stem(word))
    print(stemWords)
    return stemWords


def allowed_file(filename):
 return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/help')
@app.route('/')
def api():
    return """ 
                <p><b>/api</b> : for help</p>
                <p><b>/api/indexes</b> : to get out all indexes available in the database</p>
                <p><b>/api/index/indexName</b> : to get all types of the given index <i>ex : ontology</i></p>
                <p><b>/api/index/indexName/typeName</b> : to get all the documents of the given type<i>ex : po for plant ontology</i></p>
                <p>/<b>api/index/indexName/typeName/id</b> : to get the value of the docuement referenced by the id
                <i>ex : 2  ; a document is a concept in the given typeName(ontology)</i></p>
                <hr>
                <p><a href='/home'>Go to home</a></p>
            """
# welcome page
@app.route('/home')
def home():
    onto = ontology.Ontology()
    buckets = onto.buckets
    print(buckets)
    types = []
    for index in buckets:
        indexVal = index['key']
        alltype = onto.indexQuery(indexVal)
        aggType = alltype['aggregations']
        typeAggType = aggType['typesAgg']
        print(typeAggType['buckets'])
        types.append(typeAggType['buckets'])

    print(types)

    return render_template('user_stat.html', buckets=buckets, types=types)

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
                        return redirect(url_for('administrator', message=message, buckets=onto.buckets))

                    else:
                        message = 'Something went wrong while save ontology in database'
                        return render_template('admin.html', message=message)
    else:
        redirect(url_for('home'))

# print out all ontologies in the databasea
@app.route('/api/indexes', methods=['GET'])
def ontologies():
    onto = ontology.Ontology()
    allindex = onto.noIndexQuery()
    if allindex:
        aggregations = allindex['aggregations']
        typeAgg = aggregations['typesAgg']
        buckets = typeAgg['buckets']
        return buckets
    else:
        message = 'Problem on your request'
        return message


@app.route('/getIndexes', methods=['GET'])
def getIndexes():
    onto = ontology.Ontology()
    if onto.buckets:

        return render_template('user_indexes.html', buckets=onto.buckets)
    else:
        message = 'Problem on your request'
        return render_template('index.html', message=message)


# print out the list of all the concepts of a given ontologyName
@app.route('/api/index/<string:indexName>/<string:typeName>', methods=['POST'])
def concepts():
    onto = ontology.Ontology()

    return render_template('user_stat.html', buckets=onto.buckets)


# print out the list of all the concepts of a given ontologyName
@app.route('/getTypes')
def getTypes():
    pass


# print out a concept of a given ontologyName given the concept's id
@app.route('/api/index/<string:index>/<string:typeName>/<int:concetpId>')
def concept():
    onto = ontology.Ontology()
    return render_template('user_stat.html', buckets=onto.buckets)

# case 1 not index selected
@app.route('/getQueryNoIndex', methods=['POST'])
def getQueryNoIndex():
    onto = ontology.Ontology()
    print('get query no index ')
    if request.method == 'POST':
        words = request.form['words']
        print(words)
        procewords = textProcessing(words)
        # no type selected
        if request.form['indexes'] == '0' and not request.form['newontology']:
            results = onto.queryOntology(procewords)
            finalResult = resultProcessin(results)
            return render_template('user_result.html', buckets=onto.buckets, words=words, finalResult=finalResult)
        elif request.form['indexes'] == '0' and request.form['newontology']:
            print('ici ')
            newOnto = request.form['newontology']
            print(newOnto)
            results = onto.queryOntology(procewords)
            finalResult = resultProcessin(results)
            #obtaind unique element
            tmp1 = []
            for concept in finalResult:
                if concept not in tmp1:
                    tmp1.append(concept)

            yourresult = onto.personalOntology(procewords, newOnto)
            print(yourresult)
            yourresultsort = sorted(yourresult, key=lambda k: k['similarity'])
            tmp2 = []
            for concept in yourresultsort:
                if concept not in tmp2:
                    tmp2.append(concept)
            tmp2 = sorted(tmp2, key=lambda k: k['similarity'])
            return render_template('user_result.html', buckets=onto.buckets, words=words, finalResult=tmp1, yourresult=tmp2)
        elif request.form['indexes'] != '0' and request.form['newontology']:
            newOnto = request.form['newontology']
            onto.personalOntology(procewords, newOnto)
        elif request.form['indexes'] != '0' and not request.form['newontology']:
            # a type selected
            index = request.form['indexes']
            print(index)
            results = onto.queryOntology(procewords, indexValue=str(index))
            finalResult = resultProcessin(results)
            return render_template('user_result.html', buckets=onto.buckets, words=words, finalResult=finalResult)

    else:
        return render_template('erro.html')


# case 2 an index selected


# case 3  no index selected and  a type selected


# case 4 an index selected  and a type selected


# get a class
@app.route('/api/class/<string:classuri>', methods=['GET','POST'])
def getClass():
    pass



if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug=True)