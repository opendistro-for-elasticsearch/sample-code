# Open Distro for Elasticsearch CloudFormation Templates

These templates create a full Open Distro for Elasticsearch cluster, including secure networking provided through VPC, configurable data nodes, master nodes, and client nodes. The client nodes provide also run Kibana server, providing Kibana access with a public IP  address.

## Template descriptions

The deployment uses CloudFormation's [nested stacks](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-nested-stacks.html) to deploy a number of sub stacks. When complete, the architecture will look like this

![Open Distro for Elasticsearch deployed in a VPC](https://github.com/Jon-AtAWS/community/blob/master/cloudformation-deployment/arch.png)

## od4es.json

This is the root stack, that you deploy directly via the CloudFormation console. It contains links to the other stacks that will create a VPC, create a seed node for bootstrapping an ES 7 cluster, create master nodes, create data nodes, and create a client node with a public IP address.

## network.json

Deploys an [Amazon VPC](https://aws.amazon.com/vpc/) to provide secure networking for the Open Distro for Elasticsearch cluster. The VPC spans 2 availability zones, with a public and a private subnet in each of those zones. The stack adds an Internet Gateway for outbound traffic and a NAT gateway for inbound traffic. EC2 instances in the public subnet can have public IP addresses; the seed node, and the client nodes are publicly accessible.

## seed.json

Deploys a single, seed instance at a known IP address that is the seed to bootstrap the Elasticsearch cluster.

## data-nodes.json

Deploys an auto scaled group of data nodes into the private subnet of the VPC

## master-nodes.json

Deploys an auto scaled group of master nodes. Initially it deploys 2 instances. The seed node remains in the cluster as the 3rd master.

## client-nodes.json

Deploys an auto scaled group of client nodes with public IP addresses in the public subnet of the VPC. These instances also join the cluster as client nodes. The client nodes run Kibana server.

# To use this stack

### Create an S3 bucket

\- Clone or download the repository.
\- Create an S3 bucket to hold the templates, in the region you want to deploy the stack.  You can use the AWS Console to create a bucket. Or, if you have [installed and configured the AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html), you can run the command  

```aws s3 mb <your bucket> --region <desired region>```

### Modify `od4es.json`, editing S3 bucket references

`od4es.json` has 5 `AWS::CloudFormation::Stack` resources. Each of these has an S3 location for the stack. For example, the seed node's stack is defined like this

```
        "Seed":{
            "Type": "AWS::CloudFormation::Stack",
            "Properties": {
                "TemplateURL": "https://s3-us-west-2.amazonaws.com/odfe-cfn/seed.json",
                "Parameters": {
                    "NetworkStackName" : { "Fn::GetAtt" : [ "Network", "Outputs.StackName" ] },
                    "KeyName" : {"Ref" : "KeyName"},
                    "MasterInstanceType": { "Ref": "MasterInstanceType" }
                }
            }
        }
```

Edit `od4es.json`, replacing the `TemplateURL`'s bucket `odfe-cfn` with the [region endpoint](https://docs.aws.amazon.com/general/latest/gr/rande.html) and name of the bucket you created above.

### Put the templates in your bucket

\- Edit `package-to-s3.sh`, replacing the bucket name in the first line `bucket=_bucket_name_` with the bucket name from the bucket you created above.  
\- Make the script executable `chmod u+x package-to-s3.sh`  
\- Run `./package-to-s3.sh` to send all the templates to your bucket.  

### Create the stack

\- Navigate to the AWS CloudFormation console.  
\- Click *Create Stack*  
\- Use the S3 URL `https://s3-<region endpoint>.amazonaws.com/<your bucket>/od4es.json`  
