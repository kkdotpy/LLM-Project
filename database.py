import pandas as pd
import pickle

df=pd.DataFrame({
    'Item':[],
    'Quantity':[],
    'Expiration':[],
    'Barcode':[],
    'Category':[]
})

print(df)
with open('database.pkl','wb') as f:
    pickle.dump(df,f)

# df=pd.DataFrame()
# with open('database.pkl','rb') as f:
#     df=pickle.load(f)
#     print(df)
