# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import re

TRAINING_DATA = {
    'relevant': [
        'مناقصة تذاكر سفر',
        'خدمات الحج والعمرة',
        'توفير وسائل نقل',
        'خدمات السفر والسياحة',
        'تنظيم رحلات',
    ],
    'irrelevant': [
        'توريد مواد غذائية',
        'صيانة مباني',
        'خدمات نظافة',
        'تجهيزات مكتبية',
        'مستلزمات طبية',
    ]
}

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return ' '.join(text.split()).lower()

def init_classifier():
    texts, labels = [], []
    for t in TRAINING_DATA['relevant']:
        texts.append(preprocess_text(t)); labels.append(1)
    for t in TRAINING_DATA['irrelevant']:
        texts.append(preprocess_text(t)); labels.append(0)
    vec = TfidfVectorizer()
    X = vec.fit_transform(texts)
    clf = MultinomialNB().fit(X, labels)
    return vec, clf

def smart_filter(data):
    df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
    if df.empty:
        return df
    vec, clf = init_classifier()
    desc = df['description'] if 'description' in df.columns else pd.Series([''] * len(df), index=df.index)
    texts = (df['title'].fillna('') + ' ' + desc.fillna('')).map(preprocess_text)
    probs = clf.predict_proba(vec.transform(texts))
    df['relevance_score'] = [round(p[1], 2) for p in probs]
    df['classification'] = df['relevance_score'].apply(lambda x: 'مرتفع' if x >= 0.7 else ('متوسط' if x >= 0.4 else 'منخفض'))
    return df
