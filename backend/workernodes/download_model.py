from transformers import AutoTokenizer, AutoModel
from embedding_models import embedding_models

#model_name = 'BAAI/bge-large-en'  # Replace with your model name

for model_name in embedding_models:
    # Download and cache the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)