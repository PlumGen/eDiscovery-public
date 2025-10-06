import pandas as pd
import numpy as np
from transformers import AutoTokenizer



def get_tokenizer(model_name):
    global _tokenizer
    _tokenizer = AutoTokenizer.from_pretrained(model_name)
    return _tokenizer  # ✅ return it


def tokenize_chunked_df(df, text_col='clean_text', model_name='BAAI/bge-large-en'):
    tokenizer = get_tokenizer(model_name)

    encoded = tokenizer.batch_encode_plus(
        df[text_col].tolist(),
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )

    df[f'tokenized'] = [
        {
            'input_ids': ids.tolist(),
            'attention_mask': mask.tolist()
        }
        for ids, mask in zip(encoded['input_ids'], encoded['attention_mask'])
    ]
    return df
