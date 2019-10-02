"""Word2Vec model 1"""
import re

from gensim.matutils import corpus2csc
import joblib
from sanic import Blueprint, response
from unidecode import unidecode

from .common import flatreq


bp = Blueprint(__name__, url_prefix='/w2v1')

TEXT_ONLY_REGEX = re.compile("[^a-zA-Z ]")


def pre_normalize(name):
    return TEXT_ONLY_REGEX.sub("", unidecode(name).lower())


class Classifier:

    def __init__(self, dictionary_file, model_file):
        self.dictionary = joblib.load(dictionary_file)
        self.rf_model = joblib.load(model_file)
        self.u = self.rf_model.u
        self.num_terms = len(self.dictionary)

    def msg2bow(self, msg):
        return self.dictionary.doc2bow(pre_normalize(msg).split())

    def msg2csc(self, msg):
        return corpus2csc([self.msg2bow(msg)], num_terms=self.num_terms)

    def predict(self, msg):
        return self.rf_model.predict(self.msg2csc(msg).T @ self.u)[0]


model = Classifier(
    dictionary_file="amp_w2v1.dict",
    model_file="amp_w2v1.model",
)


@bp.route("/", methods=["GET", "POST"])
@flatreq(fields=["msg"])
async def from_msg(request, msg=""):
    return response.json({"country": model.predict(msg)})
