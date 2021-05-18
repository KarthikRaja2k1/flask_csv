import pandas as pd
import sys




df=pd.read_csv(sys.argv[1])


#loc[tset['FileName']==filen]['TypeOfTB'] for filen in Fileset)
#print(df.loc[max(df['Maths'])])

print(df.columns)
for col in df.columns[1:]:
	print("Topper in {}".format(col),df[df[col]==df[col].max()]["Name"].values)

df["sum"] = df.sum(axis=1)
sorted_df = df.sort_values(by=["sum"], ascending=False)


print("Best students in the class are ",sorted_df["Name"][:3].values)
