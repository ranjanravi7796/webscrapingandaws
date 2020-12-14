import boto3
import pickle

s3 = boto3.client('s3')

buckets = s3.list_buckets()

for bucket in buckets['Buckets']:
    print(bucket['Name'])

obj = s3.get_object(Bucket='demoexcelbuck',Key='mytempdata')
sobj = obj['Body'].read()

data = pickle.loads(sobj)

print(data)
