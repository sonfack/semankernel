import os
import re

from flask import Flask, render_template, request, url_for, redirect, jsonify
# NLTK Stop words
from nltk.corpus import stopwords
# NLTK tokenize
from nltk.tokenize import word_tokenize
# NLTK stemming
from nltk.stem import PorterStemmer
from rdflib import URIRef, Graph, RDF

from werkzeug.utils import secure_filename

from src.common import ontology

from stemming.porter2 import stem

from pyjarowinkler import distance


#configure
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['rdf', 'owl'])


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def levenshtein_distance(a, b):
    """Return the Levenshtein edit distance between two strings *a* and *b*."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not a:
        return len(b)
    previous_row = range(len(b) + 1)
    for i, column1 in enumerate(a):
        current_row = [i + 1]
        for j, column2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (column1 != column2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

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
                <p><b>/api/index/indexName/</b> : to get all the documents of the given index<i>ex : po for plant ontology</i></p>
                <p><b>/api/index/indexName/size</b> : to get size(integer) the documents of the given index<i>ex : po for plant ontology</i></p>
                <p><b>/api/index/indexName/begin/size</b> : to get size(integer) the documents of the given index from a setting begin(integer)<i>ex : po for plant ontology</i></p
                <p>/<b>api/document/indexName/id</b> : to get the value of the docuement referenced by the id
                <i>ex : 2  ; a document is a concept in the given typeName(ontology)</i></p>
                <hr>
                <p><a href='/home'>Go to home</a></p>
            """


# print out all ontologies in the databasea
@app.route('/api/indexes', methods=['GET'])
def ontologies():
    onto = ontology.Ontology()
    allindex = onto.noIndexQuery()
    if allindex:
        print(onto.buckets)
        return jsonify({"ontologies":onto.buckets})
    else:
        message = 'Problem on your request'
        return jsonify({'message': message})


@app.route('/api/document/<string:indexName>/<int:id>', methods=['GET'])
def getDocumentByIndexAndId(indexName,id):
    onto = ontology.Ontology()
    result = onto.getDocumentById(indexName, id)
    return jsonify({'document':result})

# print out a concept of a given ontologyName
@app.route('/api/document/<string:indexName>', methods=['GET'])
def getAllDocument(indexName):
    onto = ontology.Ontology()
    result = onto.getAllConceptsOfOntology(indexName)
    print(result)
    return jsonify({'ontology':result})


# print out a concept of a given ontologyName
@app.route('/api/index/<string:indexName>', methods=['GET'])
def getAllDocumentOfIndex(indexName):
    onto = ontology.Ontology()
    result = onto.getAllConceptsOfOntology(indexName)
    print(result)
    return jsonify({'ontology':result})


# print out a concept of a given ontologyName
@app.route('/api/index/<string:indexName>/<int:size>', methods=['GET'])
def getFixedSizeOfDocument(indexName, size):
    onto = ontology.Ontology()
    result = onto.getAllConceptsOfOntology(indexName, size=size)
    print(result)
    return jsonify({'ontology':result})

# print out a concept of a given ontologyName
@app.route('/api/index/<string:indexName>/<int:begin>/<int:size>', methods=['GET'])
def getFixedSizeOfDocumentFromBegining(indexName, begin, size):
    onto = ontology.Ontology()
    result = onto.getAllConceptsOfOntology(indexName, begin=begin, size=size)
    print(result)
    return jsonify({'ontology':result})




# print out the list of all the concepts of a given ontologyName
@app.route('/getTypes')
def getTypes():
    pass



# welcome page
@app.route('/home')
def home():
    onto = ontology.Ontology()
    buckets = onto.buckets
    print(buckets)
    types = onto.types
    print(types)

    return render_template('user_stat.html', buckets=buckets)

# admin page
@app.route('/administrator')
def admin():
    onto = ontology.Ontology()
    buckets = onto.buckets
    return render_template('admin_stat.html', buckets=buckets)

@app.route('/administrator/ontology', methods=['POST'])
def saveOntology():
    onto = ontology.Ontology()
    buckets = onto.buckets
    if request.method == 'POST':
        if 'ontologyFile' not in request.files:
            message = 'No file to upload'
            return render_template('admin_stat.html', message=message, buckets=buckets)
        else:
            file = request.files['ontologyFile']
            if file.filename == '':
                message = 'No selected file'
                return render_template('admin_stat.html', message=message, buckets=buckets)
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
                        return render_template('admin_stat.html', message=message, buckets=buckets)
    else:
        return redirect(url_for('administrator',buckets=buckets))


@app.route('/api/getindexes', methods=['GET'])
def getontologies():
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


@app.route('/getIdUri', methods=['POST'])
def getIdUri():
    onto = ontology.Ontology()
    if request.method == 'POST':
        conceptid = request.form['id']
        index = request.form['indexes']
        if conceptid and index:
            if index != '0':
                results = onto.getConceptById(conceptid, indexValue=index)
                finalResult = resultProcessin(results)
                tmp1 = []
                mylist = []
                if not isinstance(finalResult, bool):
                    for concept in finalResult:
                        if str(concept.get('id')) == str(conceptid) and len(str(concept.get('id'))) == len(str(conceptid)):
                            tmp1.append(concept)
                            break
                        elif concept.get('id') not in mylist :
                            mylist.append(concept.get('id'))
                    del mylist
                    if len(tmp1) > 0 and tmp1:
                        return render_template('user_result.html', buckets=onto.buckets,finalResult=tmp1)
                    elif not tmp1 or len(tmp1) == 0:
                        message = 'No result available'
                        return render_template('user_stat.html', message=message)
                else:
                    message = 'No result for query ' + conceptid
                    return render_template('user_stat.html', message=message, buckets=onto.buckets)
            else:
                results = onto.getConceptById(conceptid, indexValue=None)
                finalResult = resultProcessin(results)
                tmp1 = []
                mylist = []
                if not isinstance(finalResult, bool):
                    for concept in finalResult:
                        if concept.get('id') not in mylist and concept.get('id') != conceptid:
                            mylist.append(concept.get('id'))
                        elif concept.get('id') not in mylist:
                            tmp1.append(concept)
                            break
                    del mylist
                    return render_template('user_result.html', buckets=onto.buckets, finalResult=tmp1)
                else:
                    message = 'No result for query '+ conceptid
                    return render_template('user_stat.html', message=message, buckets=onto.buckets)
    else:
        message = 'Request should be POST'
        return render_template('user_stat.html', message=message, buckets=onto.buckets)

@app.route('/getIndexes', methods=['GET'])
def getIndexes():
    onto = ontology.Ontology()
    if onto.buckets:

        return render_template('user_indexes.html', buckets=onto.buckets)
    else:
        message = 'Problem on your request'
        return render_template('index.html', message=message)


# case 1 not index selected
@app.route('/match', methods=['POST'])
def getMatchFromDatabaseOrLink():
    onto = ontology.Ontology()
    print(' route : /match ')
    if request.method == 'POST':
        words = request.form['words']
        print('user words :'+ words)
        procewords = textProcessing(words)
        print('process word from user : ')
        print(procewords)
        # no type selected and not link given
        if request.form['indexes'] == '0' and not request.form['newontology']:
            print('condition request.form[indexes] == 0 and not request.form[newontology]')
            results = onto.queryOntology(procewords)
            finalResult = resultProcessin(results)
            tmp1 = []
            mylist = []
            for concept in finalResult:
                if concept.get('subject') not in mylist:
                    conceptLabel = concept.get('label')
                    words = str(" ".join(procewords))
                    newLabel = textProcessing(conceptLabel)
                    joinNewLable = str(" ".join(newLabel))
                    concept.update({'similarity': float(
                        distance.get_jaro_distance(joinNewLable, str(words), winkler=True, scaling=0.1))})
                    tmp1.append(concept)
                    mylist.append(concept.get('subject'))
            del mylist
            tmp1 = sorted(tmp1, key=lambda k: k['similarity'], reverse=True)
            return render_template('user_result.html', buckets=onto.buckets,  words=words, finalResult=tmp1)
        elif request.form['indexes'] == '0' and request.form['newontology']:
            print('condition request.form[indexes] == 0 and request.form[newontology]')
            newOnto = request.form['newontology']
            print('new ontology'+newOnto)
            results = onto.queryOntology(procewords)
            finalResult = resultProcessin(results)
            yourresult = onto.personalOntology(procewords, newOnto)
            print('result from online ontology')
            print(yourresult)
            print('-----------------------------------------------------------------------------------------------')
            tmp1 = []
            mylist = []
            for concept in finalResult:
                if concept.get('subject') not in mylist:
                    conceptLabel = concept.get('label')
                    words = str(" ".join(procewords))
                    newLabel = textProcessing(conceptLabel)
                    joinNewLable = str(" ".join(newLabel))
                    concept.update({'similarity': float(
                        distance.get_jaro_distance(joinNewLable, str(words), winkler=True, scaling=0.1))})
                    print(concept)
                    tmp1.append(concept)
                    mylist.append(concept.get('subject'))
            del mylist
            tmp1 = sorted(tmp1, key=lambda k: k['similarity'], reverse=True)
            print(tmp1)
            tmp2 = []
            mylist = []
            for concept in yourresult:
                if concept.get('subject') not in mylist:
                    tmp2.append(concept)
                    mylist.append(concept.get('subject'))
            tmp2 = sorted(tmp2, key=lambda k: k['similarity'], reverse=True)
            print(tmp2)
            tmp = []
            for concept in tmp1:
                tmp.append(concept)

            for concept in tmp2:
                tmp.append(concept)

            tmp = sorted(tmp, key=lambda k: k['similarity'], reverse=True)
            print('-------------------------- tmp ---------------------------')
            print(tmp)
            return render_template('user_result.html', buckets=onto.buckets, words=words, finalResult=tmp1, yourresult=tmp2, combine=tmp)
        elif request.form['indexes']!= '0' and not request.form['newontology']:
            print('ontology selected &&  no other ontology')
            index = request.form['indexes']
            print(index)
            print('words')
            print(procewords)
            results = onto.queryOntology(procewords, typeValue=None, indexValue=index)
            finalResult = resultProcessin(results)
            tmp1 = []
            mylist = []
            for concept in finalResult:
                if concept.get('subject') not in mylist:
                    conceptLabel = concept.get('label')
                    words = str(" ".join(procewords))
                    newLabel = textProcessing(conceptLabel)
                    joinNewLable = str(" ".join(newLabel))
                    concept.update({'similarity': float(
                        distance.get_jaro_distance(joinNewLable, str(words), winkler=True, scaling=0.1))})
                    print(concept)
                    tmp1.append(concept)
                    mylist.append(concept.get('subject'))
            del mylist
            tmp1 = sorted(tmp1, key=lambda k: k['similarity'], reverse=True)
            print(tmp1)

            return render_template('user_result.html', buckets=onto.buckets, types=onto.types, words=words, finalResult=tmp1)
        elif request.form['indexes']!= '0' and request.form['newontology']:
            index = request.form['indexes']
            newOnto = request.form['newontology']
            yourresult = onto.personalOntology(procewords, newOnto)
            tmp2 = []
            mylist = []
            for concept in yourresult:
                if concept.get('subject') not in mylist:
                    tmp2.append(concept)
                    mylist.append(concept.get('subject'))
            tmp2 = sorted(tmp2, key=lambda k: k['similarity'], reverse=True)

            results = onto.queryOntology(procewords, typeValue=None, indexValue=index)
            finalResult = resultProcessin(results)
            tmp1 = []
            mylist = []
            for concept in finalResult:
                if concept.get('subject') not in mylist:
                    conceptLabel = concept.get('label')
                    words = str(" ".join(procewords))
                    newLabel = textProcessing(conceptLabel)
                    joinNewLable = str(" ".join(newLabel))
                    concept.update({'similarity': float(
                        distance.get_jaro_distance(joinNewLable, str(words), winkler=True, scaling=0.1))})
                    print(concept)
                    tmp1.append(concept)
                    mylist.append(concept.get('subject'))
            del mylist
            tmp1 = sorted(tmp1, key=lambda k: k['similarity'], reverse=True)
            tmp = []
            for concept in tmp1:
                tmp.append(concept)

            for concept in tmp2:
                tmp.append(concept)

            tmp = sorted(tmp, key=lambda k: k['similarity'], reverse=True)
            return render_template('user_result.html', buckets=onto.buckets, words=words, finalResult=tmp1, yourresult=tmp2, combine=tmp)
    else:
        return render_template('user_stat.html',  buckets=onto.buckets)



# get a class
@app.route('/api/class/<string:classuri>', methods=['GET','POST'])
def getClass():
    pass

@app.route('/manualannotation', methods=['GET', 'POST'])
def manualAnnotation():
    print('annotatin')
    onto = ontology.Ontology()
    if request.method == 'POST':
        print('annotatin1')
        if request.form['uri'] and request.form['value']:
            print('annotatin2')
            uriValue = request.form['uri']
            valueObj = request.form['value']
            uri = URIRef(uriValue)
            g = Graph()
            g.parse(uri)
            print('annotation3')
            listResult = []
            listProperty = []
            for subj, pred, obj in g:
                print(subj)
                if subj == uri and valueObj in obj:
                    print(subj, '---', pred, '---', obj)
                    listResult.append({'uri':subj, 'predicate':pred, 'object':obj})
                    uriPred = URIRef(pred)
                    gPred = Graph()
                    gPred.parse(uriPred)
                    for objPred in gPred.objects(subject=uriPred, predicate=RDF.type):
                        print('---Type', objPred)
                        listProperty.append(objPred)
            if len(listResult) > 0:
                print('annotatin4')
                return render_template('user_result_annotation.html', buckets=onto.buckets, words=valueObj, finalResult=listResult)
            elif request.form['indexes'] == '0' and not request.form['newontology']:
                print('annotatin5')
                words = request.form['value']
                procewords = textProcessing(words)
                results = onto.queryOntology(procewords)
                if results is None:
                    exit()
                else:
                    finalResult = resultProcessin(results)
                    tmp1 = []
                    mylist = []
                    for concept in finalResult:
                        if concept.get('subject') not in mylist:
                            conceptLabel = concept.get('label')
                            words = str(" ".join(words))
                            concept.update({'similarity': float(
                                distance.get_jaro_distance(conceptLabel, str(words), winkler=True, scaling=0.1))})
                            print(concept)
                            tmp1.append(concept)
                            mylist.append(concept.get('subject'))
                    del mylist
                    tmp1 = sorted(tmp1, key=lambda k: k['similarity'], reverse=True)
                    print('annotation5')
                    return render_template('user_result_annotation.html', buckets=onto.buckets, words=words, uri=uriValue, yourresult=tmp1)
    else:
        message = 'No data entered'
        return render_template('user_stat.html', buckets=onto.buckets, message=message)


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug=True)