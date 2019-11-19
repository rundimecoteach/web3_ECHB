from langid.langid import LanguageIdentifier, model
import pycountry


def getLanguages(data):
    res = dict()
    identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    for filename, datum in data.items():
        lang, prob = identifier.classify(datum)
        res[filename] = pycountry.languages.get(
            alpha_2=lang)
    return res
