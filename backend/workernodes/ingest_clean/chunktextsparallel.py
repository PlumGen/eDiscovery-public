import spacy
from transformers import AutoTokenizer
import re

_tokenizer = None
_nlp = None

def init_worker(tokenizer_name="BAAI/bge-large-en", nlpmodel="en_core_web_md"):
    global _tokenizer, _nlp
    _tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    _nlp = spacy.load(nlpmodel, disable=["ner"])
    _nlp.add_pipe("sentencizer")

def is_complete_sentence(sent):
    has_subject = any(t.dep_ in {"nsubj", "nsubjpass", "expl"} for t in sent)
    has_verb = any(t.pos_ in {"VERB", "AUX"} for t in sent)
    is_imperative = sent.root.pos_ == "VERB" and sent.root.dep_ == "ROOT"
    return (has_subject and has_verb) or is_imperative



def clean_text(text, regex_list=None):
    if regex_list is None:
        regex_list = [
            (r"[\r\n]+", " "),
            (r"[^\w@%&$.,:/\-–()]+", " "),
            (r"\s{2,}", " ")
        ]
    for pattern, repl in regex_list:
        text = re.sub(pattern, repl, text)
    return text.strip().lower()

def chunk_doc_worker(row, chunk_size=512, overlap=100, regex_list=None, columnaNames=None):
    
    id_column = columnaNames['docid']
    text_column = columnaNames['Body']
                        
    docid, text = row[id_column], row[text_column]
    text = clean_text(str(text) if text else "", regex_list)
    encoded = _tokenizer.encode(text, add_special_tokens=False)

    step = chunk_size - overlap
    chunks = [encoded[i:i + chunk_size] for i in range(0, len(encoded), step)]
#    if len(chunks) > 0 and len(chunks[-1]) < chunk_size:
#        chunks[-1] = encoded[-chunk_size:]

    decoded_chunks = [_tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
    docs = list(_nlp.pipe(decoded_chunks, batch_size=32))

    results = []
    for chunkid, doc in enumerate(docs):
        filtered_sentences = [sent.text.strip() for sent in doc.sents if is_complete_sentence(sent)]
        filtered = ' '.join(filtered_sentences)
        if not filtered.strip():
            # fallback to decoded chunk if sentence filter too aggressive
            filtered = decoded_chunks[chunkid]
    
        results.append({
            id_column: docid,
            'chunkid': chunkid,
            'chunk_text': decoded_chunks[chunkid],
            'clean_text': clean_text(filtered, regex_list),
            'num_sentences':len(filtered_sentences)
        })

    return results
