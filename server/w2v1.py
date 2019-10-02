"""Word2Vec model 1"""
import io
import re

from clea import Article
from gensim.matutils import corpus2csc
import joblib
from sanic import Blueprint, response
from unidecode import unidecode

from common import flatreq, nestget_list


bp = Blueprint(__name__, url_prefix='/w2v1')

TEXT_ONLY_REGEX = re.compile("[^a-zA-Z ]")
CLEA_COMMON_PATHS = [
    ("article_meta", 0, "article_title"),
    ("journal_meta", 0, "journal_title"),
    ("journal_meta", 0, "publisher_name"),
]
FIELDS = [
    "article_title",
    "journal_title",
    "publisher_name",
    "addr_city",
    "addr_state",
    "aff_text",
    "contrib_bio",
    "contrib_prefix",
    "contrib_name",
    "contrib_surname",
    "institution_orgdiv1",
    "institution_orgdiv2",
    "institution_orgname",
    "institution_orgname_rewritten",
    "institution_original",
]


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
        result = self.rf_model.predict_proba(self.msg2csc(msg).T @ self.u)
        pairs = sorted(((probability, code)
                        for probability, code
                        in zip(result.ravel(), self.rf_model.classes_)
                        if probability > 0),
                       reverse=True)
        return [{"c": code, "p": probability} for probability, code in pairs]


model = Classifier(
    dictionary_file="amp_w2v1.dict",
    model_file="amp_w2v1.model",
)


@bp.route("/", methods=["GET", "POST"])
@flatreq(["msg"])
async def from_msg(request, msg=""):
    return response.json({"country": model.predict(msg)})


def fields2msg(**kwargs):
    msg_parts = [kwargs.get(field, "") for field in FIELDS]
    inst_names = [kwargs[field] for field in [
                                    "institution_original",
                                    "institution_orgname",
                                    "institution_orgname_rewritten",
                                ] if kwargs.get(field, "")]
    if inst_names:
        msg_parts.append(inst_names[-1])
    if len(inst_names) == 1:
        msg_parts.extend(inst_names * 2)
    elif len(inst_names) == 2:
        msg_parts.append(inst_names[-1])
    return " ".join(msg_parts)


@bp.route("/fields", methods=["GET", "POST"])
@flatreq(FIELDS)
async def from_fields(request, **kwargs):
    return response.json({"country": model.predict(fields2msg(**kwargs))})


def clea2fields_gen(clea_data):
    common_data = {path[-1]: nestget_list(clea_data, path)
                   for path in CLEA_COMMON_PATHS}
    for aidx, cidx in clea_data["aff_contrib_pairs"]:
        aff_data = clea_data["aff"][aidx] if aidx >= 0 else {}
        contrib_data = clea_data["contrib"][cidx] if cidx >= 0 else {}
        row_data = {**common_data, **aff_data, **contrib_data}
        flat_data = {k: " ".join(v) for k, v in row_data.items()}
        yield {"idx_pair": (aidx, cidx), **flat_data}


def xml2clea(xml_data):
    art = Article(io.BytesIO(xml_data))
    return {**art.data_full, "aff_contrib_pairs": art.aff_contrib_full_indices}


@bp.route("/xml", methods=["POST"])
async def from_xml(request):
    if request.content_type == "application/json":
        clea_data = request.json  # Clea CLI output
    elif request.content_type == "text/xml":
        clea_data = xml2clea(request.body)
    elif request.content_type.startswith("multipart/form-data"):
        if "xml" not in request.files:
            return response.json({"error": "missing_xml_file"}, status=400)
        if len(request.files["xml"]) != 1:
            return response.json({"error": "multiple_xml_file"}, status=400)
        clea_data = xml2clea(request.files["xml"][0].body)
    else:
        return response.json({"error": "invalid_content_type"}, status=415)
    return response.json({"result": [
        {
            "country": model.predict(fields2msg(**fields)),
            "country_input": "|".join(nestget_list(fields,
                                                   "addr_country_code")),
            "aff_contrib_pair": fields["idx_pair"],
        } for fields in clea2fields_gen(clea_data)
    ]})
