from fastai.text import *
from transformers import RobertaTokenizer as ModelTokenizer


class config(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def set(self, key, val):
        self[key] = val
        setattr(self, key, val)

###################### DATA #############################################

class FastAiModelTokenizer(BaseTokenizer):
    def __init__(self, tokenizer: ModelTokenizer, max_seq_len: int=128, model_type: str="bert", **kwargs): 
        self._pretrained_tokenizer = tokenizer
        self.max_seq_len = max_seq_len 
        self.model_type = model_type
        
    def __call__(self, *args, **kwargs): 
        return self 
    
    def tokenizer(self, t:str) -> List[str]:        
        CLS = self._pretrained_tokenizer.cls_token
        SEP = self._pretrained_tokenizer.sep_token
        if model_type in ['roberta']:
            tokens = self._pretrained_tokenizer.tokenize(t, add_prefix_space=True)[:self.max_seq_len - 2]
            tokens = [CLS] + tokens + [SEP]
        else:
            tokens = self._pretrained_tokenizer.tokenize(t)[:self.max_seq_len - 2]
            if self.model_type in ['xlnet']:
                tokens = tokens + [SEP] +  [CLS]
            else:
                tokens = [CLS] + tokens + [SEP]
        return tokens


# In[3]:


class TransformersVocab(Vocab):
    
    def __init__(self, tokenizer: ModelTokenizer):
        super(TransformersVocab, self).__init__(itos = [])
        self.tokenizer = tokenizer
    
    def numericalize(self, t:Collection[str]) -> List[int]:
        "Convert a list of tokens `t` to their ids."
        return self.tokenizer.convert_tokens_to_ids(t)
        #return self.tokenizer.encode(t)

    def textify(self, nums:Collection[int], sep=' ') -> List[str]:
        "Convert a list of `nums` to their tokens."
        nums = np.array(nums).tolist()
        return sep.join(self.tokenizer.convert_ids_to_tokens(nums)) if sep is not None else self.tokenizer.convert_ids_to_tokens(nums)
        
    def __getstate__(self):
        return {'itos':self.itos, 'tokenizer':self.tokenizer}

    def __setstate__(self, state:dict):
        self.itos = state['itos']
        self.tokenizer = state['tokenizer']
        self.stoi = collections.defaultdict(int,{v:k for k,v in enumerate(self.itos)})


# In[4]:


class ModelDataBunch(TextDataBunch):
    @classmethod
    def create(cls, train_ds, valid_ds, test_ds=None, path:PathOrStr='.', bs:int=64, val_bs:int=None, pad_idx=1,
               pad_first=True, device:torch.device=None, no_check:bool=False, backwards:bool=False, 
               dl_tfms:Optional[Collection[Callable]]=None, **dl_kwargs) -> DataBunch:
        "Function that transform the `datasets` in a `DataBunch` for classification. Passes `**dl_kwargs` on to `DataLoader()`"
        datasets = cls._init_ds(train_ds, valid_ds, test_ds)
        val_bs = ifnone(val_bs, bs)
        collate_fn = partial(pad_collate, pad_idx=pad_idx, pad_first=pad_first, backwards=backwards)
        train_sampler = SortishSampler(datasets[0].x, key=lambda t: len(datasets[0][t][0].data), bs=bs)
        train_dl = DataLoader(datasets[0], batch_size=bs, sampler=train_sampler, drop_last=True, **dl_kwargs)
        dataloaders = [train_dl]
        for ds in datasets[1:]:
            lengths = [len(t) for t in ds.x.items]
            sampler = SortSampler(ds.x, key=lengths.__getitem__)
            dataloaders.append(DataLoader(ds, batch_size=val_bs, sampler=sampler, **dl_kwargs))
        return cls(*dataloaders, path=path, device=device, dl_tfms=dl_tfms, collate_fn=collate_fn, no_check=no_check)


class ModelTextList(TextList):
    _bunch = ModelDataBunch
    _label_cls = TextList


def preprocessing_data(args):
    transformer_tokenizer = ModelTokenizer.from_pretrained("roberta-base")

    fastai_tokenizer = Tokenizer(tok_func=FastAiModelTokenizer(transformer_tokenizer, max_seq_len=args.max_seq_len, model_type=args.model_type), 
                             pre_rules=[], post_rules=[])


    tokenize_processor = TokenizeProcessor(tokenizer=fastai_tokenizer, 
                                           include_bos=False, 
                                           include_eos=False)

    transformer_vocab =  TransformersVocab(tokenizer = transformer_tokenizer)
    numericalize_processor = NumericalizeProcessor(vocab = transformer_vocab)

    transformer_processor = [tokenize_processor, numericalize_processor]
    
    data = ModelTextList.from_df(args.data_for_train, cols=args.text_column_name, processor=transformer_processor) \
             .split_by_rand_pct(args.split, seed=42) \
             .label_from_df(cols = args.labels) \
             .add_test(args.data_for_test) \
             .databunch(bs=args.bs, pad_first=False, pad_idx=0)
    
    
    return data


##############################################################################

def all_text_to_string(x):
    if type(x) == list:
        return x[0]
    else:
        return x
    
def mister_proper(x):
    text = re.sub("[^a-zA-Z]+", " ", x)    
    text = " ".join(text.split())
    return text

def stringConverter(text, use_mister_proper = False): 
    if use_mister_proper == True:
        return mister_proper(all_text_to_string(text))
    else:
        return all_text_to_string(text)

from sklearn.preprocessing import MultiLabelBinarizer

def ConverDataMLB(df, text_col, tags_col):
    tags = df[tags_col]
    mlb = MultiLabelBinarizer()
    Data = (pd.DataFrame(mlb.fit_transform(tags), columns=mlb.classes_, index=df.index))
    Data.insert(loc=0, column=text_col, value=df[text_col])
    return Data


###################### MODEL #############################################

import torch
import torch.nn as nn
from transformers import RobertaForSequenceClassification as ModelForSequenceClassification
    
class SequenceClassificationModel(nn.Module):
    def __init__(self,num_labels: int=0, model_name: str = ""):
        super(SequenceClassificationModel,self).__init__()
        self.num_labels = num_labels
        self.model_name = model_name
        self.roberta = ModelForSequenceClassification.from_pretrained(model_name, num_labels = num_labels)

    def forward(self, input_ids, token_type_ids=None, attention_mask=None, labels=None):
        outputs = self.roberta(input_ids, token_type_ids, attention_mask)
        logits = outputs[0] 
        return logits

    
#TRAIN
def train_model(args):
    data = preprocessing_data(args)
    
    roberta_model = SequenceClassificationModel(num_labels = len(args.labels), model_name = args.model_name) 
    
    loss_func = nn.BCEWithLogitsLoss()
    acc_02 = partial(accuracy_thresh, thresh=0.2)
    f_score = partial(fbeta, thresh=0.2)

    learner = Learner(data, roberta_model, loss_func=loss_func, metrics=[acc_02, f_score])
    
    return learner

#PREDICT
def predict(text, args):
    prediction = args["model"].predict(text)
    predictionResults = list(np.array(args["labels"])[np.where(prediction[1].numpy() == 1)[0]])
    return predictionResults



    
    
    
    
    
    
    
    
    
    
    
    