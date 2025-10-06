import os
import time
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import json

from .errors import EmbeddingError, EmbeddingOOMError


# Set up logging with adjustable verbosity
def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

setup_logging(logging.INFO)


from torch.utils.data import Dataset
def custom_collate_fn(batch):
    """
    Prevent PyTorch from converting lists into tensors.
    Simply returns the batch as a list of lists.
    """
    return batch

# Custom Dataset for Pandas DataFrame
class PandasDataset(Dataset):
    def __init__(self, dataframe, column):
        """
        Args:
            dataframe (pd.DataFrame): The dataframe containing data.
            column (str): The name of the column to extract data from.
        """
        self.dataframe = dataframe
        self.column = column

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        """
        Returns:
            The content of the specified column at index `idx`.
        """
        # Return the vector stored in the column at row index `idx`
        return self.dataframe.iloc[idx][self.column]

def process_in_batches(df, file, model, tokenizer, batch_size=32, concurrency=10):
    """
    Processes text embeddings in batches using a PyTorch DataLoader.
    """
    # Prepare DataLoader with custom Dataset
    dataset = PandasDataset(df, f"{file['column_name']}")
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, collate_fn=custom_collate_fn)

    all_embeddings = []
    for batch in tqdm(data_loader, desc="Processing Batches"):
        batch_df = pd.DataFrame({f"{file['column_name']}":batch})
        
        print(f'shape of batch_df {batch_df.shape}')

        batch_embeddings = localembedBAAI_hybrid(batch_df, file, model, tokenizer, concurrency)
        all_embeddings.append(batch_embeddings)
        if cudaflag=='cuda':
            torch.cuda.empty_cache()
    # Combine all embeddings into a single DataFrame
    print('getting ready to concat')
    final_embeddings = pd.concat(all_embeddings, ignore_index=True)
    print('completed concat')
    return final_embeddings



# Refactored localembedBAAI_hybrid function
def localembedBAAI_hybrid(df, file, model, tokenizer, concurrency=10):
    try:
        input_ids_list = []
        attention_masks_list = []

        for row in df[f"{file['column_name']}"]:
            # input_ids = torch.tensor(row['input_ids'].tolist())
                        

            if isinstance(row, str):
                row = json.loads(row)
    
            input_ids = torch.tensor(row['input_ids'].tolist() if isinstance(row['input_ids'], np.ndarray) else row['input_ids'])

            # attention_mask = torch.tensor(row['attention_mask'].tolist())
            attention_mask = torch.tensor(row['attention_mask'].tolist() if isinstance(row['attention_mask'], np.ndarray) else row['attention_mask'])

            input_ids_list.append(input_ids)
            attention_masks_list.append(attention_mask)

        input_ids_padded = torch.nn.utils.rnn.pad_sequence(input_ids_list, batch_first=True, padding_value=tokenizer.pad_token_id)
        attention_masks_padded = torch.nn.utils.rnn.pad_sequence(attention_masks_list, batch_first=True, padding_value=0)

        input_ids_padded = input_ids_padded.to(cudaflag)
        attention_masks_padded = attention_masks_padded.to(cudaflag)

        with torch.no_grad():
            outputs = model(input_ids=input_ids_padded, attention_mask=attention_masks_padded)
            pooled = (outputs.last_hidden_state * attention_masks_padded.unsqueeze(-1)).sum(1)
            pooled /= attention_masks_padded.sum(1).unsqueeze(-1)
            if cudaflag=='cuda':
                torch.cuda.empty_cache()


        # Attach embeddings back to DataFrame
        df["embed"] = [v.cpu().tolist() for v in pooled]
        return df

    except torch.cuda.OutOfMemoryError as e:
        logging.error("CUDA OOM in localembedBAAI_hybrid", exc_info=True)
        raise EmbeddingOOMError(str(e))

    except Exception as e:
        logging.error("Error in localembedBAAI_hybrid", exc_info=True)
        raise EmbeddingError(str(e))


# Main script to process data
def main(parsed_emails_df, file, cudaflag_override=None, model_name=None, batch_size=16, raise_on_error=True):
    global cudaflag
    cudaflag = cudaflag_override or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))

    try:
        model_name = model_name or "BAAI/bge-large-en"

        if cudaflag.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name).to(cudaflag)
        model.eval()

        body_embeddings = process_in_batches(
            parsed_emails_df[[f"{file['column_name']}"]],
            file, model, tokenizer, batch_size=batch_size, concurrency=5
        )

        if cudaflag.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        if body_embeddings is None or "embed" not in body_embeddings.columns:
            raise EmbeddingError("Embedding stage produced no 'embed' column")

        parsed_emails_df = parsed_emails_df.copy()
        parsed_emails_df["embed"] = body_embeddings["embed"]
        return parsed_emails_df

    except Exception as e:
        logging.error("Main script error", exc_info=True)
        if raise_on_error:
            raise
        return None
