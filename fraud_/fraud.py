import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score,accuracy_score
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from bs4 import BeautifulSoup
from string import punctuation
from sklearn.naive_bayes import MultinomialNB
import cPickle as pickle

#Option 1: Use acct_type and delivery_method column Get 96.5% accuracy
df=pd.read_json('./data/data.json')
#df = df_orig


#Change payout_type to integer values
row_index = df['payout_type'] ==''
df.loc[row_index, 'payout_type'] = '0'
row_index = df['payout_type'] =='ACH'
df.loc[row_index, 'payout_type'] = '1'
row_index = df['payout_type'] =='CHECK'
df.loc[row_index, 'payout_type'] = '2'

#Handle NANs for delivery_method column
df['delivery_method']=df['delivery_method'].fillna(9999)
df['org_facebook']=df['org_facebook'].fillna(9999)

df['fraud'] = [1 if item == "fraudster_event" else 0 for item in df['acct_type']]
y = df['fraud']

def make_soup(input):
   soup = BeautifulSoup(input)
   text = [''.join(node.findAll(text=True)) for node in soup.findAll('p')]
   text = ','.join(text).lower()
   #stop = set(stopwords.words('english'))
   #text = [[word for word in text if word not in stop]]
   text = text.replace(u'\xa0',' ')
   return text

clean = []
for i in df['description']:
    text = make_soup(i)
    clean.append(text)

X_other = df[['num_payouts', 'payout_type', 'delivery_method']]
X_train, X_test, y_train, y_test = train_test_split(X_other, y)

rf = RandomForestClassifier(n_estimators=100)
model = rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

if __name__ == '__main__':
    print recall_score(y_test, y_pred)
# with open("model.pkl", 'w') as f:
#     pickle.dump(model, f)
