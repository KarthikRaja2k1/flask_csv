import requests

Base='http://127.0.0.1:5000/todos/'


inp=int(input().split()[0])

if(inp<0):
	x = requests.post(Base,json={
  "id": 0,
  "task": "string",
  "dueby": "20190201",
  "status": "in progress"
})
elif(inp==0):
	x = requests.get(Base)
else:
	x = requests.get(Base+"{}".format(inp))
for i,k in x.__dict__.items():
	print(i," = ",k)

