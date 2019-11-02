#! /bin/bash
bucket=_replace_with_your_bucket_name_

for file in od4es.json network.json seed.json data-nodes.json master-nodes.json client-nodes.json; do
    echo "Sending $file"
    aws s3 rm s3://$bucket/$file
    aws s3 cp $file s3://$bucket/$file
    aws s3api put-object-acl --bucket $bucket --key $file --acl public-read
done